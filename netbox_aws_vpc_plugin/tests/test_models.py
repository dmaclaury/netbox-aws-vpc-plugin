from django.test import SimpleTestCase
from ipam.models import Prefix

from netbox_aws_vpc_plugin import __version__
from netbox_aws_vpc_plugin.choices import AWSAccountStatusChoices, AWSSubnetStatusChoices, AWSVPCStatusChoices
from netbox_aws_vpc_plugin.models.aws_account import AWSAccount
from netbox_aws_vpc_plugin.models.aws_subnet import AWSSubnet
from netbox_aws_vpc_plugin.models.aws_vpc import AWSVPC


class NetBoxAWSVPCVersionTestCase(SimpleTestCase):
    def test_version(self):
        assert __version__ == "0.0.6"


class AWSAccountModelTestCase(SimpleTestCase):
    def test_create_aws_account(self):
        account = AWSAccount.objects.create(account_id="123456789012", name="Test Account")
        self.assertEqual(account.account_id, "123456789012")

    def test_account_status_choices(self):
        for status, _, _ in AWSAccountStatusChoices.CHOICES:
            short_id = (status[:12]).ljust(12, "0")
            account = AWSAccount.objects.create(account_id=short_id, name="Test", status=status)
            self.assertEqual(account.status, status)


class AWSVPCModelTestCase(SimpleTestCase):
    def test_create_aws_vpc_with_prefix(self):
        account = AWSAccount.objects.create(account_id="123456789012", name="Test Account")
        prefix = Prefix.objects.create(prefix="10.0.0.0/16")
        vpc = AWSVPC.objects.create(vpc_id="vpc-1234567890abcdef0", owner_account=account, vpc_cidr=prefix)
        self.assertEqual(vpc.vpc_id, "vpc-1234567890abcdef0")
        self.assertEqual(str(vpc.vpc_cidr), "10.0.0.0/16")

    def test_vpc_status_choices(self):
        account = AWSAccount.objects.create(account_id="idVPC", name="Test Account")
        for status, _, _ in AWSVPCStatusChoices.CHOICES:
            base = "vpc-"
            short_id = (base + status.lower())[:21]
            vpc = AWSVPC.objects.create(vpc_id=short_id, owner_account=account, status=status)
            self.assertEqual(vpc.status, status)


class AWSSubnetModelTestCase(SimpleTestCase):
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

    def test_subnet_status_choices(self):
        account = AWSAccount.objects.create(account_id="idSUBNET", name="Test Account")
        vpc = AWSVPC.objects.create(vpc_id="vpc-for-subnet", owner_account=account)
        for status, _, _ in AWSSubnetStatusChoices.CHOICES:
            subnet = AWSSubnet.objects.create(
                subnet_id=f"subnet-{status.lower()}", vpc=vpc, owner_account=account, status=status
            )
            self.assertEqual(subnet.status, status)
