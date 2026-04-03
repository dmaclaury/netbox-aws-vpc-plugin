#! /usr/bin/env python3

"""
Discover an AWS VPC (and optionally subnets) with boto3, then sync to NetBox via pynetbox.

When ``NETBOX_URL`` / ``NETBOX_TOKEN`` (or ``--netbox-url`` / ``--netbox-token``) are set,
creates or updates ``ipam.Prefix`` and plugin objects (``AWSAccount``, ``AWSVPC``, ``AWSSubnet``).
Use ``--dry-run`` to log intended changes without mutating NetBox.
"""

import argparse
import logging
import os
import re
import sys

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
        resolved_region = self.aws_region or self.ec2_client.meta.region_name
        self.vpc_data["region"] = resolved_region
        # Build the ARN using the partition, region, account ID, and VPC ID
        self.vpc_data["vpc_arn"] = (
            f"arn:{self.aws_partition}:ec2:{resolved_region}:"
            f"{response.get('Vpcs', [{}])[0].get('OwnerId')}:vpc/{self.vpc_id}"
        )
        vpc = response.get("Vpcs", [{}])[0]
        self.vpc_data["vpc_cidr"] = vpc.get("CidrBlock")
        assoc_set = vpc.get("CidrBlockAssociationSet") or vpc.get("Ipv4CidrBlockAssociationSet") or []
        self.vpc_data["vpc_secondary_ipv4_cidrs"] = [
            assoc.get("CidrBlock")
            for assoc in assoc_set
            if assoc.get("AssociationState", {}).get("State") == "associated"
            and assoc.get("CidrBlock") != self.vpc_data["vpc_cidr"]
        ]
        self.vpc_data["vpc_ipv6_cidrs"] = [
            assoc.get("Ipv6CidrBlock")
            for assoc in vpc.get("Ipv6CidrBlockAssociationSet", [])
            if assoc.get("AssociationState", {}).get("State") == "associated"
        ]
        self.vpc_data["owner_account_id"] = vpc.get("OwnerId")

        logger.debug(f"Discovered VPC Data: {self.vpc_data}")


class DiscoverSubnetsForVpc:
    """
    Discover subnets in a VPC via EC2 describe_subnets (dict rows for NetBox sync).
    """

    def __init__(self, vpc_id, aws_profile=None, aws_region=None):
        self.vpc_id = vpc_id
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.ec2_client = self.setup_boto3_client()

    def setup_boto3_client(self):
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
        logger.info("Discovering subnets for VPC: %s", self.vpc_id)
        try:
            response = self.ec2_client.describe_subnets(
                Filters=[{"Name": "vpc-id", "Values": [self.vpc_id]}],
            )
        except ClientError as e:
            logger.error(e)
            return []

        resolved_region = self.aws_region or self.ec2_client.meta.region_name
        rows = []
        for s in response.get("Subnets", []):
            name = next(
                (tag.get("Value") for tag in s.get("Tags", []) if tag.get("Key") == "Name"),
                None,
            )
            sid = s.get("SubnetId")
            owner = s.get("OwnerId")
            arn = f"arn:{self.aws_partition}:ec2:{resolved_region}:{owner}:subnet/{sid}"
            ipv6 = [
                a.get("Ipv6CidrBlock")
                for a in s.get("Ipv6CidrBlockAssociationSet", [])
                if a.get("AssociationState", {}).get("State") == "associated"
            ]
            rows.append(
                {
                    "subnet_id": sid,
                    "vpc_id": s.get("VpcId"),
                    "subnet_name": name,
                    "subnet_arn": arn,
                    "subnet_cidr": s.get("CidrBlock"),
                    "owner_account_id": owner,
                    "region": resolved_region,
                    "subnet_ipv6_cidrs": ipv6,
                }
            )
        logger.debug("Discovered %s subnet(s)", len(rows))
        return rows


def _ensure_repo_root_on_path():
    """Ensure repo root is on ``sys.path`` so ``extras.*`` imports work.

    Needed when running this file as ``python extras/scripts/add_vpc_to_netbox/cli.py`` (only
    the script directory is on the default path).
    """
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if root not in sys.path:
        sys.path.insert(0, root)


def main(argv=None):
    _ensure_repo_root_on_path()
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting to parse arg inputs...")
    parser = argparse.ArgumentParser()
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
        help=(
            "If set, the script will not make any changes to NetBox, "
            "but will still perform AWS discovery and log intended NetBox actions."
        ),
    )
    parser.add_argument(
        "--netbox-url",
        default=os.environ.get("NETBOX_URL"),
        help="NetBox base URL (default: NETBOX_URL env)",
    )
    parser.add_argument(
        "--netbox-token",
        default=os.environ.get("NETBOX_TOKEN"),
        help="NetBox API token, v2 format (default: NETBOX_TOKEN env)",
    )
    parser.add_argument(
        "--sync-subnets",
        action="store_true",
        help="After syncing the VPC, discover and sync subnets in that VPC",
    )
    parser.add_argument(
        "--create-aws-account",
        action="store_true",
        help=(
            "Create a plugin AWSAccount in NetBox when the VPC owner account id is missing "
            "(default: only look up existing accounts)"
        ),
    )
    parser.add_argument(
        "--netbox-region-slug",
        default=os.environ.get("NETBOX_REGION_SLUG"),
        help=(
            "dcim.Region slug to use for VPC/subnet region FK (e.g. aws-us-east-1). "
            "Default: same as the AWS region from discovery (e.g. us-east-1). "
            "Env: NETBOX_REGION_SLUG"
        ),
    )
    args = parser.parse_args(argv)
    logger.info("Completed arg parse")
    if args.log_level:
        log_level = getattr(logging, args.log_level.upper(), None)
        if isinstance(log_level, int):
            logger.setLevel(log_level)

    logger.debug("Args Parsed: %s", args)

    try:
        validate_vpc_id(args.vpc_id)
    except ValueError as e:
        logger.error(str(e))
        return 2

    discoverer = DiscoverVPC(
        vpc_id=args.vpc_id,
        aws_profile=args.aws_profile,
        aws_region=args.aws_region,
    )
    discoverer.discover()
    if not discoverer.vpc_data.get("vpc_id"):
        logger.error("VPC discovery failed or returned no VPC id")
        return 1

    netbox_url = (args.netbox_url or "").strip()
    token = (args.netbox_token or "").strip()
    if netbox_url and token:
        try:
            from extras.scripts.add_vpc_to_netbox.netbox_sync import NetBoxSync, connect_pynetbox
        except ImportError:
            logger.error(
                "pynetbox is required for NetBox sync; install extras/scripts/add_vpc_to_netbox/requirements.txt"
            )
            return 2

        site_id = os.environ.get("NETBOX_SITE_ID")
        vrf_id = os.environ.get("NETBOX_VRF_ID")
        site_pk = int(site_id) if site_id else None
        vrf_pk = int(vrf_id) if vrf_id else None

        api = connect_pynetbox(netbox_url, token)
        nb_slug = (args.netbox_region_slug or "").strip() or None
        sync = NetBoxSync(
            api,
            dry_run=args.dry_run,
            site_id=site_pk,
            vrf_id=vrf_pk,
            create_aws_account=args.create_aws_account,
            netbox_region_slug=nb_slug,
        )
        vpc_pk = sync.sync_discovered_vpc(discoverer.vpc_data)
        if args.sync_subnets:
            subnet_rows = DiscoverSubnetsForVpc(
                vpc_id=args.vpc_id,
                aws_profile=args.aws_profile,
                aws_region=args.aws_region,
            ).discover()
            logger.info("Discovered %d subnet(s) for VPC", len(subnet_rows))
            owner = discoverer.vpc_data.get("owner_account_id")
            for row in subnet_rows:
                sync.sync_discovered_subnet(
                    row,
                    vpc_nb_id=vpc_pk,
                    default_owner_account_id=owner,
                )
    elif netbox_url or token:
        logger.error("Both --netbox-url and --netbox-token (or NETBOX_URL and NETBOX_TOKEN) are required to sync")
        return 2

    return 0
