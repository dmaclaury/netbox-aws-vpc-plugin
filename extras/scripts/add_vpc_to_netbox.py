#! /usr/bin/env python3

"""
Script to add a single AWS VPC to NetBox, using boto3 to query AWS for the VPC details.

Phase 1 we will focus on gathering the required VPC details for our custom models.
We are not yet implemeting the logic to add them into NetBox.
"""

import argparse
import logging
import re

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def validate_vpc_id(vpc_id):
    """
    Validate the format of the VPC ID.
    """
    if not re.match(r"^vpc-[a-f0-9]{8,17}$", vpc_id):
        raise ValueError(f"Invalid VPC ID format: {vpc_id}")


class DiscoverVPC:
    """
    Class to discover VPC details from AWS using boto3.
    """

    def __init__(self, vpc_id, aws_profile=None, aws_region=None):
        self.vpc_id = vpc_id
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.ec2_client = self.setup_boto3_client()
        self.aws_partition = None
        self.vpc_data = {
            "vpc_id": None,
            "vpc_name": None,
            "vpc_arn": None,
            "vpc_cidr": None,
            "vpc_secondary_ipv4_cidrs": [],
            "vpc_ipv6_cidrs": [],
            "owner_account_id": None,
            "region": None,
        }

    def setup_boto3_client(self):
        """
        Set up the boto3 client with the specified AWS profile and region.
        """
        session_kwargs = {}
        if self.aws_profile:
            session_kwargs["profile_name"] = self.aws_profile
        if self.aws_region:
            session_kwargs["region_name"] = self.aws_region

        session = boto3.Session(**session_kwargs)
        ec2_client = session.client("ec2")

        self.aws_partition = session.get_partition_for_region(self.aws_region or ec2_client.meta.region_name)
        return ec2_client

    def discover(self):
        """
        Discover the VPC details from AWS.
        """
        logger.info(f"Discovering details for VPC: {self.vpc_id}")
        # Use boto3 to query AWS for VPC details and return them in a structured format
        try:
            response = self.ec2_client.describe_vpcs(VpcIds=[self.vpc_id])
            logger.info(response)
        except ClientError as e:
            logger.error(e)
            return

        # Validate we only found a single VPC matching the ID we provided, otherwise log an error and exit
        if len(response.get("Vpcs", [])) != 1:
            logger.error(
                f"Expected to find exactly 1 VPC with ID {self.vpc_id}, but found {len(response.get('Vpcs', []))}"
            )
            return

        # VPC Data will be filled with only the data returned by AWS
        # even VPC ID which is already known, to ensure we receive a response from AWS
        self.vpc_data["vpc_id"] = response.get("Vpcs", [{}])[0].get("VpcId")
        self.vpc_data["vpc_name"] = next(
            (tag.get("Value") for tag in response.get("Vpcs", [{}])[0].get("Tags", []) if tag.get("Key") == "Name"),
            None,
        )
        # Build the ARN using the partition, region, account ID, and VPC ID
        self.vpc_data["vpc_arn"] = (
            f"arn:{self.aws_partition}:ec2:{self.aws_region}:"
            f"{response.get('Vpcs', [{}])[0].get('OwnerId')}:vpc/{self.vpc_id}"
        )
        self.vpc_data["vpc_cidr"] = response.get("Vpcs", [{}])[0].get("CidrBlock")
        # For secondary CIDRs, we need to look at the Ipv4CidrBlockAssociationSet and filter
        # for those that are associated and not the primary CIDR
        self.vpc_data["vpc_secondary_ipv4_cidrs"] = [
            assoc.get("CidrBlock")
            for assoc in response.get("Vpcs", [{}])[0].get("Ipv4CidrBlockAssociationSet", [])
            if assoc.get("AssociationState", {}).get("State") == "associated"
            and assoc.get("CidrBlock") != self.vpc_data["vpc_cidr"]
        ]
        # For IPv6 CIDRs, we need to look at the Ipv6CidrBlockAssociationSet and filter for those that are associated
        self.vpc_data["vpc_ipv6_cidrs"] = [
            assoc.get("Ipv6CidrBlock")
            for assoc in response.get("Vpcs", [{}])[0].get("Ipv6CidrBlockAssociationSet", [])
            if assoc.get("AssociationState", {}).get("State") == "associated"
        ]
        # We pull the owner account ID from the VPC details in case of shared VPCs where
        # the account running the script may not be the owner of the VPC
        self.vpc_data["owner_account_id"] = response.get("Vpcs", [{}])[0].get("OwnerId")
        self.vpc_data["region"] = self.aws_region or self.ec2_client.meta.region_name

        logger.debug(f"Discovered VPC Data: {self.vpc_data}")


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting to parse arg inputs...")
    parser = argparse.ArgumentParser()
    # Args to implement: vpc-id, aws profile, aws region, log level, dry run
    parser.add_argument(
        "vpc_id",
        help="The ID of the VPC to add to NetBox (Ex: `vpc-1234567890abcdef0`)",
    )
    parser.add_argument(
        "--aws-profile",
        help="AWS CLI Profile to use otherwise, default or env vars will be used",
    )
    parser.add_argument(
        "--aws-region",
        help="AWS Region to query, otherwise we will use the region in profile, or default",
    )
    parser.add_argument(
        "--log-level",
        help="Specify the log level to use during the run. (Ex: `INFO` (default), `DEBUG`, etc.)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="""
            If set, the script will not make any changes to NetBox,
            but will still perform all queries and log the intended actions.
        """,
    )
    args = parser.parse_args()
    logger.info("Completed arg parse")
    if args.log_level:
        log_level = getattr(logging, args.log_level.upper(), None)
        if isinstance(log_level, int):
            logger.setLevel(log_level)

    logger.debug(f"Args Parsed: {args}")

    try:
        validate_vpc_id(args.vpc_id)
    except ValueError as e:
        logger.error(str(e))
        return

    DiscoverVPC(
        vpc_id=args.vpc_id,
        aws_profile=args.aws_profile,
        aws_region=args.aws_region,
    ).discover()


if __name__ == "__main__":
    main()
