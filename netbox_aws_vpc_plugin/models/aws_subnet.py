"""
Define the django models for AWS Subnets.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from netbox_aws_vpc_plugin.choices import AWSSubnetStatusChoices
from netbox_aws_vpc_plugin.constants import IPV4_PREFIXES, IPV6_PREFIXES

from .aws_account import AWSAccount
from .aws_vpc import AWSVPC


class AWSSubnet(NetBoxModel):
    subnet_id = models.CharField(max_length=47, unique=True, verbose_name="Subnet ID")
    name = models.CharField(
        max_length=256,
        blank=True,
    )
    arn = models.CharField(max_length=2000, blank=True, verbose_name="ARN")
    # Primary CIDR
    subnet_cidr = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        to="ipam.Prefix",
        verbose_name="CIDR Block",
        related_name="aws_subnet_ipv4",
        limit_choices_to=IPV4_PREFIXES,
    )
    # IPv6 CIDR
    subnet_ipv6_cidr = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        to="ipam.Prefix",
        verbose_name="IPv6 CIDR Block",
        related_name="aws_subnet_ipv6",
        limit_choices_to=IPV6_PREFIXES,
    )
    # VPC the subnet is part of
    vpc = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        to=AWSVPC,
        verbose_name="VPC ID",
    )
    owner_account = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        to=AWSAccount,
        verbose_name="Owner Account",
    )
    region = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        to="dcim.Region",
    )
    # TODO: Availability Zone
    status = models.CharField(
        max_length=50, choices=AWSSubnetStatusChoices, default=AWSSubnetStatusChoices.STATUS_ACTIVE
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ("subnet_id",)
        verbose_name = "AWS Subnet"
        verbose_name_plural = "AWS Subnets"

    def __str__(self):
        # TODO: conditional if name is not blank
        return self.subnet_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_vpc_plugin:awssubnet", args=[self.pk])
