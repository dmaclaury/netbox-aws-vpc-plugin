"""
Define the django models for AWS Subnets.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .aws_vpc import AWSVPC
from .aws_account import AWSAccount


class AWSSubnet(NetBoxModel):
    subnet_id = models.CharField(max_length=47, unique=True)
    name = models.CharField(
        max_length=256,
        blank=True,
    )
    arn = models.CharField(max_length=2000, blank=True, verbose_name="ARN")
    subnet_cidr = models.ForeignKey(
        blank=True, null=True, on_delete=models.PROTECT, to="ipam.Prefix", verbose_name="CIDR Block"
    )
    vpc = models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, to=AWSVPC, verbose_name="VPC ID")
    # TODO: IPv6 CIDRs
    owner_account = models.ForeignKey(
        blank=True, null=True, on_delete=models.PROTECT, to=AWSAccount, verbose_name="Owner Account"
    )
    # TODO: Region
    # TODO: Availability Zone
    # TODO: Resource Tags
    # TODO: Status
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ("subnet_id",)

    def __str__(self):
        # TODO: conditional if name is not blank
        return self.subnet_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_vpc_plugin:awssubnet", args=[self.pk])
