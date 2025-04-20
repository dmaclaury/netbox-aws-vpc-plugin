from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .models import AWSVPC, AWSSubnet, AWSAccount


# AWS VPC Forms
class AWSVPCForm(NetBoxModelForm):
    vpc_cidr = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
    )
    owner_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        required=False,
    )
    comments = CommentField()

    class Meta:
        model = AWSVPC
        fields = ("vpc_id", "name", "arn", "vpc_cidr", "owner_account", "comments", "tags")


class AWSVPCFilterForm(NetBoxModelFilterSetForm):
    model = AWSVPC

    owner_account = forms.ModelMultipleChoiceField(queryset=AWSAccount.objects.all(), required=False)


# AWS Subnet Forms
class AWSSubnetForm(NetBoxModelForm):
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        required=False,
    )
    subnet_cidr = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
    )
    owner_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        required=False,
    )
    comments = CommentField()

    class Meta:
        model = AWSSubnet
        fields = ("subnet_id", "vpc", "name", "arn", "subnet_cidr", "owner_account", "comments", "tags")


class AWSSubnetFilterForm(NetBoxModelFilterSetForm):
    model = AWSSubnet

    vpc = forms.ModelMultipleChoiceField(queryset=AWSVPC.objects.all(), required=False)
    owner_account = forms.ModelMultipleChoiceField(queryset=AWSAccount.objects.all(), required=False)


# AWS Account Forms
class AWSAccountForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = AWSAccount
        fields = ("account_id", "name", "arn", "description", "comments", "tags")
