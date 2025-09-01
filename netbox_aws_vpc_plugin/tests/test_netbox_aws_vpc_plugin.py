"""Tests for `netbox_aws_vpc_plugin` package."""

from django.test import SimpleTestCase
from django.urls import reverse
from ipam.models import Prefix
from utilities.testing.api import APITestCase

from netbox_aws_vpc_plugin import __version__
from netbox_aws_vpc_plugin.models.aws_account import AWSAccount
from netbox_aws_vpc_plugin.models.aws_subnet import AWSSubnet
from netbox_aws_vpc_plugin.models.aws_vpc import AWSVPC


class NetBoxAWSVPCVersionTestCase(SimpleTestCase):
    def test_version(self):
        assert __version__ == "0.0.6"


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)

        self.assertEqual(response.status_code, 200)


class AWSAccountModelTestCase(APITestCase):
    def test_create_aws_account(self):
        account = AWSAccount.objects.create(account_id="123456789012", name="Test Account")
        self.assertEqual(account.account_id, "123456789012")


class AWSVPCModelTestCase(APITestCase):
    def test_create_aws_vpc_with_prefix(self):
        account = AWSAccount.objects.create(account_id="123456789012", name="Test Account")
        prefix = Prefix.objects.create(prefix="10.0.0.0/16")
        vpc = AWSVPC.objects.create(vpc_id="vpc-1234567890abcdef0", owner_account=account, vpc_cidr=prefix)
        self.assertEqual(vpc.vpc_id, "vpc-1234567890abcdef0")
        self.assertEqual(str(vpc.vpc_cidr), "10.0.0.0/16")


class AWSSubnetModelTestCase(APITestCase):
    def test_create_aws_subnet_with_prefix(self):
        account = AWSAccount.objects.create(account_id="123456789012", name="Test Account")
        vpc_prefix = Prefix.objects.create(prefix="10.0.0.0/16")
        vpc = AWSVPC.objects.create(vpc_id="vpc-1234567890abcdef0", owner_account=account, vpc_cidr=vpc_prefix)
        subnet_prefix = Prefix.objects.create(prefix="10.0.1.0/24")
        subnet = AWSSubnet.objects.create(
            subnet_id="subnet-abcdef1234567890", vpc=vpc, owner_account=account, subnet_cidr=subnet_prefix
        )
        self.assertEqual(subnet.subnet_id, "subnet-abcdef1234567890")
        self.assertEqual(str(subnet.subnet_cidr), "10.0.1.0/24")
