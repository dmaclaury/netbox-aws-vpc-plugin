from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from ..models import AWSVPC, AWSSubnet, AWSAccount


class NestedAWSVPCSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awsvpc-detail")

    class Meta:
        model = AWSVPC
        fields = ("id", "url", "display", "vpc_id")


class NestedAWSSubnetSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awssubnet-detail")

    class Meta:
        model = AWSSubnet
        fields = ("id", "url", "display", "subnet_id")


class NestedAWSAccountSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_vpc_plugin-api:awsaccount-detail")

    class Meta:
        model = AWSAccount
        fields = ("id", "url", "display", "account_id")
