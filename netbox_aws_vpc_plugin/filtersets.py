from netbox.filtersets import NetBoxModelFilterSet

from .models import AWSVPC, AWSAccount, AWSSubnet


class AWSVPCFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AWSVPC
        fields = [
            "vpc_id",
            "name",
            "arn",
            "vpc_cidr",
            "vpc_secondary_ipv4_cidrs",
            "vpc_ipv6_cidrs",
            "owner_account",
            "region",
            "status",
        ]


class AWSSubnetFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AWSSubnet
        fields = [
            "subnet_id",
            "name",
            "arn",
            "subnet_cidr",
            "subnet_ipv6_cidr",
            "vpc",
            "owner_account",
            "region",
            "status",
        ]


class AWSAccountFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AWSAccount
        fields = ["account_id", "name", "arn", "tenant", "status"]
