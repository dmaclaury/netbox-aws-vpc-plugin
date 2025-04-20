import django_tables2 as tables
from netbox.tables import NetBoxTable

from .models import AWSVPC, AWSSubnet, AWSAccount


class AWSVPCTable(NetBoxTable):
    vpc_id = tables.Column(linkify=True)
    name = tables.Column()
    vpc_cidr = tables.Column(linkify=True)
    owner_account = tables.Column(linkify=True)
    # TODO: Count of subnets

    class Meta(NetBoxTable.Meta):
        model = AWSVPC
        fields = ("pk", "id", "vpc_id", "name", "arn", "vpc_cidr", "owner_account", "actions")
        default_columns = ("vpc_id", "name", "vpc_cidr", "owner_account")


class AWSSubnetTable(NetBoxTable):
    subnet_id = tables.Column(linkify=True)
    vpc = tables.Column(linkify=True)
    name = tables.Column()
    subnet_cidr = tables.Column(linkify=True)
    owner_account = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = AWSSubnet
        fields = ("pk", "id", "subnet_id", "vpc", "name", "arn", "subnet_cidr", "owner_account", "actions")
        default_columns = ("subnet_id", "name", "subnet_cidr", "vpc")


class AWSAccountTable(NetBoxTable):
    account_id = tables.Column(linkify=True)
    name = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = AWSAccount
        fields = ("pk", "id", "account_id", "name", "arn", "actions")
        default_columns = ("account_id", "name")
