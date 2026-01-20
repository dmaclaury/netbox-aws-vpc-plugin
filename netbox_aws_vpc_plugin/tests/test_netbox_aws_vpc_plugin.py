"""Tests for `netbox_aws_vpc_plugin` package."""

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse
from ipam.models import Prefix
from utilities.testing.api import APITestCase

from netbox_aws_vpc_plugin import __version__
from netbox_aws_vpc_plugin.choices import (
    AWSAccountStatusChoices,
    AWSSubnetStatusChoices,
    AWSVPCStatusChoices,
)
from netbox_aws_vpc_plugin.models.aws_account import AWSAccount
from netbox_aws_vpc_plugin.models.aws_subnet import AWSSubnet
from netbox_aws_vpc_plugin.models.aws_vpc import AWSVPC


class NetBoxAWSVPCVersionTestCase(SimpleTestCase):
    def test_version(self):
        assert __version__ == "0.1.0"


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)

        self.assertEqual(response.status_code, 200)


class AWSAccountModelTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a superuser for API authentication
        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser",
            email="superuser@example.com",
            password="supersecret",
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.superuser)

    def test_create_aws_account(self):
        account = AWSAccount.objects.create(account_id="123456789012", name="Test Account")
        self.assertEqual(account.account_id, "123456789012")

    def test_account_status_choices(self):
        # Use unique AWS account IDs for each status choice to avoid unique constraint violations
        # Use shorter base account ID to leave room for suffix (max_length=12)
        base_account_id = "123456789"
        for i, (status, _, _) in enumerate(AWSAccountStatusChoices.CHOICES):
            # Create unique account_id by appending a suffix (max 3 digits)
            unique_account_id = f"{base_account_id}{i:03d}"
            account = AWSAccount.objects.create(account_id=unique_account_id, name=f"Test {status}", status=status)
            self.assertEqual(account.status, status)

    def test_api_crud_account(self):
        # Create
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:awsaccount-list")
        payload = {
            "account_id": "999999999999",
            "name": "API Test Account",
            "status": AWSAccountStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, payload, format="json", **self.header)
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]

        # Read
        response = self.client.get(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["account_id"], "999999999999")

        # Update
        response = self.client.patch(f"{url}{pk}/", {"name": "Updated Account"}, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Account")

        # Delete
        response = self.client.delete(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 204)


class AWSVPCModelTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser2",
            email="superuser2@example.com",
            password="supersecret2",
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.superuser)

    def test_create_aws_vpc_with_prefix(self):
        account = AWSAccount.objects.create(account_id="111111111111", name="Test Account")
        prefix = Prefix.objects.create(prefix="10.0.0.0/16")
        vpc = AWSVPC.objects.create(vpc_id="vpc-12345678", owner_account=account, vpc_cidr=prefix)
        self.assertEqual(vpc.vpc_id, "vpc-12345678")
        self.assertEqual(str(vpc.vpc_cidr), "10.0.0.0/16")

    def test_create_aws_vpc_with_ipv6_prefix(self):
        account = AWSAccount.objects.create(account_id="111111111111", name="Test Account")
        prefix = Prefix.objects.create(prefix="10.1.0.0/16")
        ipv6_prefix = Prefix.objects.create(prefix="2600:1f18:286d:f300::/56")
        vpc = AWSVPC.objects.create(
            vpc_id="vpc-12345679",
            owner_account=account,
            vpc_cidr=prefix,
        )
        self.assertEqual(vpc.vpc_ipv6_cidrs.count(), 0)
        vpc.vpc_ipv6_cidrs.add(ipv6_prefix)
        self.assertEqual(vpc.vpc_id, "vpc-12345679")
        self.assertEqual(str(vpc.vpc_cidr), "10.1.0.0/16")
        self.assertEqual(vpc.vpc_ipv6_cidrs.count(), 1)

    def test_create_aws_vpc_with_multiple_prefix(self):
        account = AWSAccount.objects.create(account_id="111111115511", name="Test Account")
        prefix = Prefix.objects.create(prefix="10.2.0.0/16")
        secondary_prefix = Prefix.objects.create(prefix="10.3.0.0/16")
        ipv6_prefix = Prefix.objects.create(prefix="2600:0000:286d:f300::/56")
        vpc = AWSVPC.objects.create(
            vpc_id="vpc-0b1eb59b119d8da06",
            owner_account=account,
            vpc_cidr=prefix,
        )
        self.assertEqual(vpc.vpc_ipv6_cidrs.count(), 0)
        self.assertEqual(vpc.vpc_secondary_ipv4_cidrs.count(), 0)
        vpc.vpc_ipv6_cidrs.add(ipv6_prefix)
        vpc.vpc_secondary_ipv4_cidrs.add(secondary_prefix)
        self.assertEqual(vpc.vpc_id, "vpc-0b1eb59b119d8da06")
        self.assertEqual(str(vpc.vpc_cidr), "10.2.0.0/16")
        self.assertEqual(vpc.vpc_ipv6_cidrs.count(), 1)
        self.assertEqual(vpc.vpc_secondary_ipv4_cidrs.count(), 1)

    def test_vpc_status_choices(self):
        account = AWSAccount.objects.create(account_id="123456789012", name="Test Account")
        for i, (status, _, _) in enumerate(AWSVPCStatusChoices.CHOICES):
            # Create unique vpc_id with realistic format
            vpc_id = f"vpc-{i:08x}"
            vpc = AWSVPC.objects.create(vpc_id=vpc_id, owner_account=account, status=status)
            self.assertEqual(vpc.status, status)

    def test_api_crud_vpc(self):
        account = AWSAccount.objects.create(account_id="888888888888", name="API VPC Account")
        prefix = Prefix.objects.create(prefix="10.1.0.0/16")
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:awsvpc-list")
        payload = {
            "vpc_id": "vpc-apitest",
            "owner_account": account.pk,
            "vpc_cidr": prefix.pk,
            "status": AWSVPCStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, payload, format="json", **self.header)
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]

        # Read
        response = self.client.get(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["vpc_id"], "vpc-apitest")

        # Update
        response = self.client.patch(f"{url}{pk}/", {"name": "Updated VPC"}, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated VPC")

        # Delete
        response = self.client.delete(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 204)


class AWSSubnetModelTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser3",
            email="superuser3@example.com",
            password="supersecret3",
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.superuser)

    def test_create_aws_subnet_with_prefix(self):
        account = AWSAccount.objects.create(account_id="222222222222", name="Test Account")
        vpc_prefix = Prefix.objects.create(prefix="10.0.0.0/16")
        vpc = AWSVPC.objects.create(vpc_id="vpc-12345678", owner_account=account, vpc_cidr=vpc_prefix)
        subnet_prefix = Prefix.objects.create(prefix="10.0.1.0/24")
        subnet = AWSSubnet.objects.create(
            subnet_id="subnet-abcdef1234567890",
            vpc=vpc,
            owner_account=account,
            subnet_cidr=subnet_prefix,
        )
        self.assertEqual(subnet.subnet_id, "subnet-abcdef1234567890")
        self.assertEqual(str(subnet.subnet_cidr), "10.0.1.0/24")

    def test_create_aws_subnet_with_ipv6_prefix(self):
        account = AWSAccount.objects.create(account_id="222222222222", name="Test Account")
        vpc_prefix = Prefix.objects.create(prefix="10.0.0.0/16")
        vpc = AWSVPC.objects.create(vpc_id="vpc-12345678", owner_account=account, vpc_cidr=vpc_prefix)
        subnet_prefix = Prefix.objects.create(prefix="10.0.1.0/24")
        subnet_ipv6_prefix = Prefix.objects.create(prefix="2001:db8::/64")
        subnet = AWSSubnet.objects.create(
            subnet_id="subnet-abcdef1234567890",
            vpc=vpc,
            owner_account=account,
            subnet_cidr=subnet_prefix,
            subnet_ipv6_cidr=subnet_ipv6_prefix,
        )
        self.assertEqual(subnet.subnet_id, "subnet-abcdef1234567890")
        self.assertEqual(str(subnet.subnet_cidr), "10.0.1.0/24")
        self.assertEqual(str(subnet.subnet_ipv6_cidr), "2001:db8::/64")

    def test_subnet_status_choices(self):
        account = AWSAccount.objects.create(account_id="333333333333", name="Test Account")
        vpc = AWSVPC.objects.create(vpc_id="vpc-87654321", owner_account=account)
        for i, (status, _, _) in enumerate(AWSSubnetStatusChoices.CHOICES):
            # Create unique subnet_id with realistic format to avoid duplicates
            subnet_id = f"subnet-{i:08x}"
            subnet = AWSSubnet.objects.create(subnet_id=subnet_id, vpc=vpc, owner_account=account, status=status)
            self.assertEqual(subnet.status, status)

    def test_api_crud_subnet(self):
        account = AWSAccount.objects.create(account_id="777777777777", name="API Subnet Account")
        vpc = AWSVPC.objects.create(vpc_id="vpc-subnetapi", owner_account=account)
        prefix = Prefix.objects.create(prefix="10.2.1.0/24")
        ipv6_prefix = Prefix.objects.create(prefix="2001:db8::/64")
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:awssubnet-list")
        payload = {
            "subnet_id": "subnet-api-test",
            "vpc": vpc.pk,
            "owner_account": account.pk,
            "subnet_cidr": prefix.pk,
            "subnet_ipv6_cidr": ipv6_prefix.pk,
            "status": AWSSubnetStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, payload, format="json", **self.header)
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]

        # Read
        response = self.client.get(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["subnet_id"], "subnet-api-test")

        # Update
        response = self.client.patch(f"{url}{pk}/", {"name": "Updated Subnet"}, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Subnet")

        # Delete
        response = self.client.delete(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 204)
