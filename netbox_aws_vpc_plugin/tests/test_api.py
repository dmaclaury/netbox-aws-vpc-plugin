from django.contrib.auth import get_user_model
from django.urls import reverse
from ipam.models import Prefix
from utilities.testing.api import APITestCase

from netbox_aws_vpc_plugin.choices import AWSAccountStatusChoices, AWSSubnetStatusChoices, AWSVPCStatusChoices
from netbox_aws_vpc_plugin.models.aws_account import AWSAccount
from netbox_aws_vpc_plugin.models.aws_vpc import AWSVPC


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)
        self.assertEqual(response.status_code, 200)


class AWSAccountModelAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", email="superuser@example.com", password="supersecret"
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.superuser)

    def test_api_crud_account(self):
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:awsaccount-list")
        payload = {
            "account_id": "999999999999",
            "name": "API Test Account",
            "status": AWSAccountStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, payload, format="json", **self.header)
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]
        response = self.client.get(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["account_id"], "999999999999")
        response = self.client.patch(f"{url}{pk}/", {"name": "Updated Account"}, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Account")
        response = self.client.delete(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 204)


class AWSVPCModelAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser2", email="superuser2@example.com", password="supersecret2"
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.superuser)

    def test_api_crud_vpc(self):
        account = AWSAccount.objects.create(account_id="888888888888", name="API VPC Account")
        prefix = Prefix.objects.create(prefix="10.1.0.0/16")
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:awsvpc-list")
        payload = {
            "vpc_id": "vpc-api-test",
            "owner_account": account.pk,
            "vpc_cidr": prefix.pk,
            "status": AWSVPCStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, payload, format="json", **self.header)
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]
        response = self.client.get(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["vpc_id"], "vpc-api-test")
        response = self.client.patch(f"{url}{pk}/", {"name": "Updated VPC"}, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated VPC")
        response = self.client.delete(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 204)


class AWSSubnetModelAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser3", email="superuser3@example.com", password="supersecret3"
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.superuser)

    def test_api_crud_subnet(self):
        account = AWSAccount.objects.create(account_id="777777777777", name="API Subnet Account")
        vpc = AWSVPC.objects.create(vpc_id="vpc-for-subnet-api", owner_account=account)
        prefix = Prefix.objects.create(prefix="10.2.1.0/24")
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:awssubnet-list")
        payload = {
            "subnet_id": "subnet-api-test",
            "vpc": vpc.pk,
            "owner_account": account.pk,
            "subnet_cidr": prefix.pk,
            "status": AWSSubnetStatusChoices.STATUS_ACTIVE,
        }
        response = self.client.post(url, payload, format="json", **self.header)
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]
        response = self.client.get(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["subnet_id"], "subnet-api-test")
        response = self.client.patch(f"{url}{pk}/", {"name": "Updated Subnet"}, format="json", **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Subnet")
        response = self.client.delete(f"{url}{pk}/", **self.header)
        self.assertEqual(response.status_code, 204)
