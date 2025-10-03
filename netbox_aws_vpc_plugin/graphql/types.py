import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import AWSVPC, AWSAccount, AWSSubnet


@strawberry_django.type(
    AWSAccount,
    fields="__all__",
)
class AWSAccountType(NetBoxObjectType):
    pass


@strawberry_django.type(
    AWSVPC,
    fields="__all__",
)
class AWSVPCType(NetBoxObjectType):
    pass


@strawberry_django.type(
    AWSSubnet,
    fields="__all__",
)
class AWSSubnetType(NetBoxObjectType):
    pass
