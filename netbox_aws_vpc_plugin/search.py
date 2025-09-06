from netbox.search import SearchIndex, register_search

from .models import AWSVPC, AWSAccount, AWSSubnet


@register_search
class AWSVPCIndex(SearchIndex):
    model = AWSVPC
    fields = (
        ("vpc_id", 90),
        ("name", 100),
        ("vpc_cidr", 110),
        ("vpc_secondary_ipv4_cidrs", 120),
        ("vpc_ipv6_cidrs", 130),
        ("arn", 900),
        ("comments", 5000),
    )


@register_search
class AWSSubnetIndex(SearchIndex):
    model = AWSSubnet
    fields = (
        ("subnet_id", 90),
        ("name", 100),
        ("subnet_cidr", 110),
        ("subnet_ipv6_cidr", 120),
        ("vpc", 130),
        ("owner_account", 140),
        ("region", 150),
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
