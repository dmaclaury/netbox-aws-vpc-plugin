from dcim.api.serializers import RegionSerializer
from ipam.api.serializers import PrefixSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer

from ..models import AWSVPC, AWSAccount, AWSSubnet
from .nested_serializers import NestedAWSAccountSerializer, NestedAWSVPCSerializer


class AWSVPCSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awsvpc-detail")
    vpc_cidr = PrefixSerializer(required=False, allow_null=True, default=None, nested=True)
    owner_account = NestedAWSAccountSerializer()
    region = RegionSerializer(required=False, allow_null=True, default=None, nested=True)

    class Meta:
        model = AWSVPC
        fields = (
            "id",
            "url",
            "display",
            "vpc_id",
            "name",
            "arn",
            "vpc_cidr",
            "vpc_secondary_ipv4_cidrs",
            "vpc_ipv6_cidrs",
            "owner_account",
            "region",
            "status",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )


class AWSSubnetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awssubnet-detail")
    subnet_cidr = PrefixSerializer(required=False, allow_null=True, default=None, nested=True)
    vpc = NestedAWSVPCSerializer()
    owner_account = NestedAWSAccountSerializer()
    region = RegionSerializer(required=False, allow_null=True, default=None, nested=True)

    class Meta:
        model = AWSSubnet
        fields = (
            "id",
            "url",
            "display",
            "subnet_id",
            "name",
            "arn",
            "subnet_cidr",
            "subnet_ipv6_cidr",
            "vpc",
            "owner_account",
            "region",
            "status",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )


class AWSAccountSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awsaccount-detail")
    tenant = TenantSerializer(required=False, allow_null=True, default=None, nested=True)

    class Meta:
        model = AWSAccount
        fields = (
            "id",
            "url",
            "display",
            "account_id",
            "name",
            "arn",
            "tenant",
            "description",
            "status",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
