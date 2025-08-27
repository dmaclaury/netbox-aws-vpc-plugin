"""
Define the django models for AWS Accounts.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from netbox_aws_vpc_plugin.choices import AWSAccountStatusChoices


class AWSAccount(NetBoxModel):
    account_id = models.CharField(max_length=12, unique=True, verbose_name="Account ID")
    arn = models.CharField(max_length=2000, blank=True, verbose_name="ARN")
    name = models.CharField(
        max_length=50,
        blank=True,
    )
    description = models.CharField(max_length=500, blank=True)
    tenant = models.ForeignKey(to="tenancy.Tenant", on_delete=models.PROTECT, blank=True, null=True)
    comments = models.TextField(blank=True)

    status = models.CharField(
        max_length=50, choices=AWSAccountStatusChoices, default=AWSAccountStatusChoices.STATUS_ACTIVE
    )

    class Meta:
        ordering = ("account_id",)
        verbose_name = "AWS Account"
        verbose_name_plural = "AWS Accounts"

    def __str__(self):
        return self.account_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_vpc_plugin:awsaccount", args=[self.pk])
