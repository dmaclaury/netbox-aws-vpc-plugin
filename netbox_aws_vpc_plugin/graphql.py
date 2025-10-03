"""
GraphQL schema for NetBox AWS VPC Plugin.
"""

import strawberry
import strawberry_django

from . import models


@strawberry_django.type(
    models.AWSAccount,
    fields=[
        "id",
        "account_id",
        "arn",
        "name",
        "description",
        "status",
        "comments",
        "created",
        "last_updated",
    ],
)
class AWSAccountType:
    """GraphQL type for AWS Account model."""

    pass


@strawberry_django.type(
    models.AWSVPC,
    fields=[
        "id",
        "vpc_id",
        "name",
        "arn",
        "status",
        "comments",
        "created",
        "last_updated",
    ],
)
class AWSVPCType:
    """GraphQL type for AWS VPC model."""

    pass


@strawberry_django.type(
    models.AWSSubnet,
    fields=[
        "id",
        "subnet_id",
        "name",
        "arn",
        "status",
        "comments",
        "created",
        "last_updated",
    ],
)
class AWSSubnetType:
    """GraphQL type for AWS Subnet model."""

    pass


@strawberry.type
class Query:
    """GraphQL queries for AWS VPC Plugin."""

    @strawberry.field
    def aws_account(self, id: int) -> AWSAccountType:
        """Get a single AWS Account by ID."""
        return models.AWSAccount.objects.get(id=id)

    @strawberry.field
    def aws_accounts(self) -> list[AWSAccountType]:
        """Get all AWS Accounts."""
        return models.AWSAccount.objects.all()

    @strawberry.field
    def aws_vpc(self, id: int) -> AWSVPCType:
        """Get a single AWS VPC by ID."""
        return models.AWSVPC.objects.get(id=id)

    @strawberry.field
    def aws_vpcs(self) -> list[AWSVPCType]:
        """Get all AWS VPCs."""
        return models.AWSVPC.objects.all()

    @strawberry.field
    def aws_subnet(self, id: int) -> AWSSubnetType:
        """Get a single AWS Subnet by ID."""
        return models.AWSSubnet.objects.get(id=id)

    @strawberry.field
    def aws_subnets(self) -> list[AWSSubnetType]:
        """Get all AWS Subnets."""
        return models.AWSSubnet.objects.all()


# Export the schema for NetBox to discover
schema = [
    Query,
]
