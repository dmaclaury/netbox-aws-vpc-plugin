from netbox.search import SearchIndex, register_search
from .models import AWSVPC, AWSSubnet, AWSAccount


@register_search
class AWSVPCIndex(SearchIndex):
    model = AWSVPC
    fields = (
        ("vpc_id", 90),
        ("name", 100),
        ("arn", 900),
        ("comments", 5000),
    )


@register_search
class AWSSubnetIndex(SearchIndex):
    model = AWSSubnet
    fields = (
        ("subnet_id", 90),
        ("name", 100),
        ("arn", 900),
        ("comments", 5000),
    )


@register_search
class AWSAccountIndex(SearchIndex):
    model = AWSAccount
    fields = (
        ("account_id", 90),
        ("name", 100),
        ("arn", 900),
        ("comments", 5000),
    )
