import strawberry_django
from netbox.graphql.types import NetBoxObjectType

from ..models import AWSVPC, AWSAccount, AWSSubnet
from .filters import AWSAccountFilter, AWSSubnetFilter, AWSVPCFilter


@strawberry_django.type(AWSAccount, fields="__all__", filters=AWSAccountFilter)
class AWSAccountType(NetBoxObjectType):
    pass


@strawberry_django.type(AWSVPC, fields="__all__", filters=AWSVPCFilter)
class AWSVPCType(NetBoxObjectType):
    pass


@strawberry_django.type(AWSSubnet, fields="__all__", filters=AWSSubnetFilter)
class AWSSubnetType(NetBoxObjectType):
    pass
