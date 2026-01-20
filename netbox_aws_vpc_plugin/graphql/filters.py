import strawberry_django
from netbox.graphql.filters import NetBoxModelFilter

from .. import models

__all__ = (
    "AWSAccountFilter",
    "AWSVPCFilter",
    "AWSSubnetFilter",
)


@strawberry_django.filter(models.AWSAccount, lookups=True)
class AWSAccountFilter(NetBoxModelFilter):
    pass


@strawberry_django.filter(models.AWSVPC, lookups=True)
class AWSVPCFilter(NetBoxModelFilter):
    pass


@strawberry_django.filter(models.AWSSubnet, lookups=True)
class AWSSubnetFilter(NetBoxModelFilter):
    pass
