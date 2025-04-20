"""
Define the django models for AWS Accounts.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class AWSAccount(NetBoxModel):
    account_id = models.CharField(max_length=12, unique=True)
    arn = models.CharField(
        max_length=2000, blank=True, verbose_name="The Amazon Resource Name (ARN) of the account root."
    )
    name = models.CharField(
        max_length=50,
        blank=True,
    )
    description = models.CharField(max_length=500, blank=True)
    # TODO: Netbox Tenant
    # TODO: AWS Org
    # TODO: Status
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ("account_id",)

    def __str__(self):
        return self.account_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_vpc_plugin:awsaccount", args=[self.pk])
