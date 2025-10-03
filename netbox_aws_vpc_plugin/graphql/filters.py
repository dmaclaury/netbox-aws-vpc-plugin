import strawberry_django
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

from .. import models

__all__ = (
    "AWSAccountFilter",
    "AWSVPCFilter",
    "AWSSubnetFilter",
)


@strawberry_django.filter(models.AWSAccount, lookups=True)
class AWSAccountFilter(NetBoxModelFilterMixin):
    pass


@strawberry_django.filter(models.AWSVPC, lookups=True)
class AWSVPCFilter(NetBoxModelFilterMixin):
    pass


@strawberry_django.filter(models.AWSSubnet, lookups=True)
class AWSSubnetFilter(NetBoxModelFilterMixin):
    pass
