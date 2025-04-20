from rest_framework import serializers

from ipam.api.serializers import PrefixSerializer
from netbox.api.serializers import NetBoxModelSerializer
from ..models import AWSVPC, AWSSubnet, AWSAccount
from .nested_serializers import NestedAWSAccountSerializer, NestedAWSVPCSerializer


class AWSVPCSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awsvpc-detail")
    vpc_cidr = PrefixSerializer(required=False, allow_null=True, default=None, nested=True)
    owner_account = NestedAWSAccountSerializer()

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
            "owner_account",
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
            "vpc",
            "owner_account",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )


class AWSAccountSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awsaccount-detail")

    class Meta:
        model = AWSAccount
        fields = (
            "id",
            "url",
            "display",
            "account_id",
            "name",
            "arn",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
