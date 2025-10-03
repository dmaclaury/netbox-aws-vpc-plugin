"""
GraphQL schema for NetBox AWS VPC Plugin.
"""

from netbox.graphql.types import NetBoxObjectType

from . import models


class AWSAccountType(NetBoxObjectType):
    """GraphQL type for AWS Account model."""

    class Meta:
        model = models.AWSAccount
        fields = "__all__"


class AWSVPCType(NetBoxObjectType):
    """GraphQL type for AWS VPC model."""

    class Meta:
        model = models.AWSVPC
        fields = "__all__"


class AWSSubnetType(NetBoxObjectType):
    """GraphQL type for AWS Subnet model."""

    class Meta:
        model = models.AWSSubnet
        fields = "__all__"


# Export the schema for NetBox to discover
# NetBox will automatically discover these types and make them available
schema = [
    AWSAccountType,
    AWSVPCType,
    AWSSubnetType,
]
