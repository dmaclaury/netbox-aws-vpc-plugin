from netbox.filtersets import NetBoxModelFilterSet
from .models import AWSVPC, AWSSubnet, AWSAccount


class AWSVPCFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = AWSVPC
        fields = ["vpc_id", "name", "arn", "vpc_cidr", "owner_account"]

    # def search(self, queryset, name, value):
    #     return queryset.filter(description__icontains=value)


class AWSSubnetFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = AWSSubnet
        fields = ["subnet_id", "name", "arn", "subnet_cidr", "vpc", "owner_account"]

    # def search(self, queryset, name, value):
    #     return queryset.filter(description__icontains=value)


class AWSAccountFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = AWSAccount
        fields = ["account_id", "name", "arn"]

    # def search(self, queryset, name, value):
    #     return queryset.filter(description__icontains=value)
