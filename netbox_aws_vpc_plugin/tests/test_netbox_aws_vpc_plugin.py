"""Tests for `netbox_aws_vpc_plugin` package."""

from django.urls import reverse
from django.test import SimpleTestCase
from netbox_aws_vpc_plugin import __version__
from utilities.testing.api import APITestCase


class NetBoxAWSVPCVersionTestCase(SimpleTestCase):
    def test_version(self):
        assert __version__ == "0.0.1"


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("plugins-api:netbox_aws_vpc_plugin-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)

        self.assertEqual(response.status_code, 200)
