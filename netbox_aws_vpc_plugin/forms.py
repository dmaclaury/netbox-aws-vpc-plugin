from dcim.models import Region
from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from tenancy.models import Tenant
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .models import AWSVPC, AWSAccount, AWSSubnet


# AWS VPC Forms
class AWSVPCForm(NetBoxModelForm):
    vpc_cidr = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Primary CIDR",
    )
    owner_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        required=False,
        label="Owner Account",
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label="Region",
    )
    comments = CommentField()

    class Meta:
        model = AWSVPC
        fields = ("vpc_id", "name", "arn", "vpc_cidr", "owner_account", "region", "status", "comments", "tags")


class AWSVPCFilterForm(NetBoxModelFilterSetForm):
    model = AWSVPC

    owner_account = forms.ModelMultipleChoiceField(queryset=AWSAccount.objects.all(), required=False)
    region = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )


# AWS Subnet Forms
class AWSSubnetForm(NetBoxModelForm):
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        required=False,
        label="VPC",
    )
    subnet_cidr = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Subnet CIDR",
    )
    owner_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        required=False,
        label="Owner Account",
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label="Region",
    )
    comments = CommentField()

    class Meta:
        model = AWSSubnet
        fields = (
            "subnet_id",
            "vpc",
            "name",
            "arn",
            "subnet_cidr",
            "owner_account",
            "region",
            "status",
            "comments",
            "tags",
        )


class AWSSubnetFilterForm(NetBoxModelFilterSetForm):
    model = AWSSubnet

    vpc = forms.ModelMultipleChoiceField(queryset=AWSVPC.objects.all(), required=False)
    owner_account = forms.ModelMultipleChoiceField(queryset=AWSAccount.objects.all(), required=False)
    region = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
    )


# AWS Account Forms
class AWSAccountForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label="Tenant",
    )
    comments = CommentField()

    class Meta:
        model = AWSAccount
        fields = ("account_id", "name", "arn", "tenant", "description", "status", "comments", "tags")
