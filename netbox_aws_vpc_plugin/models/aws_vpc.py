"""
Define the django models for AWS VPCs.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from netbox_aws_vpc_plugin.choices import AWSVPCStatusChoices
from netbox_aws_vpc_plugin.constants import IPV4_PREFIXES, IPV6_PREFIXES

from .aws_account import AWSAccount


class AWSVPC(NetBoxModel):
    vpc_id = models.CharField(
        max_length=21,
        unique=True,
        verbose_name="VPC ID",
    )
    name = models.CharField(
        max_length=256,
        blank=True,
    )
    arn = models.CharField(max_length=2000, blank=True, verbose_name="ARN")
    # IPv4 CIDR
    vpc_cidr = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        to="ipam.Prefix",
        verbose_name="Primary IPv4 CIDR",
        related_name="vpc_cidr",
        limit_choices_to=IPV4_PREFIXES,
    )
    # Secondary IPv4 CIDRs
    vpc_secondary_ipv4_cidrs = models.ManyToManyField(
        blank=True,
        to="ipam.Prefix",
        verbose_name="Secondary IPv4 CIDRs",
        related_name="vpc_secondary_ipv4_cidrs",
        limit_choices_to=IPV4_PREFIXES,
    )
    # IPv6 CIDRs
    vpc_ipv6_cidrs = models.ManyToManyField(
        blank=True,
        to="ipam.Prefix",
        verbose_name="IPv6 CIDRs",
        related_name="vpc_ipv6_cidrs",
        limit_choices_to=IPV6_PREFIXES,
    )
    owner_account = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        to=AWSAccount,
        verbose_name="Owner Account",
    )
    region = models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, to="dcim.Region")
    status = models.CharField(
        max_length=50,
        choices=AWSVPCStatusChoices,
        default=AWSVPCStatusChoices.STATUS_ACTIVE,
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ("vpc_id",)
        verbose_name = "AWS VPC"
        verbose_name_plural = "AWS VPCs"

    def __str__(self):
        # TODO: conditional if name is not blank
        return self.vpc_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_vpc_plugin:awsvpc", args=[self.pk])
