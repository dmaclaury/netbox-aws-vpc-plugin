import os
import sys
from unittest import mock

import pytest
from botocore.exceptions import ClientError

# Ensure repository root is on sys.path so `extras` can be imported as a package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

from extras.scripts.add_vpc_to_netbox import (  # noqa: E402
    DiscoverSubnetsForVpc,
    DiscoverVPC,
    validate_vpc_id,
)


class _MockClient:
    def __init__(self, response=None, subnet_response=None, raise_exc=None, region_name="us-east-1"):
        self._response = response
        self._subnet_response = subnet_response if subnet_response is not None else {"Subnets": []}
        self._raise = raise_exc
        self.meta = type("M", (), {"region_name": region_name})

    def describe_vpcs(self, VpcIds=None):
        if self._raise:
            raise self._raise
        return self._response

    def describe_subnets(self, Filters=None):
        if self._raise:
            raise self._raise
        return self._subnet_response


class _MockSession:
    def __init__(self, client):
        self._client = client

    def client(self, service_name):
        return self._client

    def get_partition_for_region(self, region):
        return "aws"


def test_validate_vpc_id_valid():
    validate_vpc_id("vpc-1234abcd")


def test_validate_vpc_id_invalid():
    with pytest.raises(ValueError):
        validate_vpc_id("invalid-vpc-id")


def test_discover_vpc_success(monkeypatch):
    good_response = {
        "Vpcs": [
            {
                "VpcId": "vpc-12345678",
                "Tags": [{"Key": "Name", "Value": "my-vpc"}],
                "OwnerId": "111122223333",
                "CidrBlock": "10.0.0.0/16",
                "CidrBlockAssociationSet": [
                    {
                        "AssociationState": {"State": "associated"},
                        "CidrBlock": "10.1.0.0/16",
                    },
                    {
                        "AssociationState": {"State": "associated"},
                        "CidrBlock": "10.0.0.0/16",
                    },
                ],
                "Ipv6CidrBlockAssociationSet": [
                    {
                        "AssociationState": {"State": "associated"},
                        "Ipv6CidrBlock": "2001:db8::/56",
                    }
                ],
            }
        ]
    }

    mock_client = _MockClient(response=good_response, region_name="us-east-1")
    mock_session = _MockSession(client=mock_client)
    monkeypatch.setattr("extras.scripts.add_vpc_to_netbox.cli.boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverVPC(vpc_id="vpc-12345678", aws_region="us-east-1")
    d.discover()
    # discover() returns None but fills vpc_data
    assert d.vpc_data["vpc_id"] == "vpc-12345678"
    assert d.vpc_data["vpc_name"] == "my-vpc"
    assert d.vpc_data["vpc_cidr"] == "10.0.0.0/16"
    assert d.vpc_data["vpc_secondary_ipv4_cidrs"] == ["10.1.0.0/16"]
    assert d.vpc_data["vpc_ipv6_cidrs"] == ["2001:db8::/56"]
    assert d.vpc_data["owner_account_id"] == "111122223333"
    assert d.vpc_data["region"] == "us-east-1"


def test_discover_vpc_not_found(monkeypatch):
    empty_response = {"Vpcs": []}
    mock_client = _MockClient(response=empty_response)
    mock_session = _MockSession(client=mock_client)
    monkeypatch.setattr("extras.scripts.add_vpc_to_netbox.cli.boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverVPC(vpc_id="vpc-00000000", aws_region="us-west-2")
    res = d.discover()
    assert res is None
    assert d.vpc_data["vpc_id"] is None


def test_discover_vpc_arn_uses_client_region_when_aws_region_omitted(monkeypatch):
    good_response = {
        "Vpcs": [
            {
                "VpcId": "vpc-aaaaaaaa",
                "Tags": [],
                "OwnerId": "999999999999",
                "CidrBlock": "10.0.0.0/16",
                "CidrBlockAssociationSet": [
                    {
                        "AssociationState": {"State": "associated"},
                        "CidrBlock": "10.0.0.0/16",
                    },
                ],
            }
        ]
    }
    mock_client = _MockClient(response=good_response, region_name="us-west-2")
    mock_session = _MockSession(client=mock_client)
    monkeypatch.setattr("extras.scripts.add_vpc_to_netbox.cli.boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverVPC(vpc_id="vpc-aaaaaaaa")
    d.discover()
    assert d.vpc_data["region"] == "us-west-2"
    assert ":ec2:us-west-2:" in d.vpc_data["vpc_arn"]
    assert "None" not in d.vpc_data["vpc_arn"]


def test_discover_vpc_client_error(monkeypatch):
    err = ClientError(
        {"Error": {"Code": "InvalidVpcID.NotFound", "Message": "Not found"}},
        "DescribeVpcs",
    )
    mock_client = _MockClient(raise_exc=err)
    mock_session = _MockSession(client=mock_client)
    monkeypatch.setattr("extras.scripts.add_vpc_to_netbox.cli.boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverVPC(vpc_id="vpc-doesnotexist", aws_region="us-west-2")
    res = d.discover()
    assert res is None


def test_discover_subnets_success(monkeypatch):
    subnet_response = {
        "Subnets": [
            {
                "SubnetId": "subnet-abc12345",
                "VpcId": "vpc-12345678",
                "CidrBlock": "10.0.1.0/24",
                "OwnerId": "111122223333",
                "Tags": [{"Key": "Name", "Value": "private-a"}],
                "Ipv6CidrBlockAssociationSet": [],
            }
        ]
    }
    mock_client = _MockClient(subnet_response=subnet_response, region_name="us-east-1")
    mock_session = _MockSession(client=mock_client)
    monkeypatch.setattr("extras.scripts.add_vpc_to_netbox.cli.boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverSubnetsForVpc(vpc_id="vpc-12345678", aws_region="us-east-1")
    data = d.discover()
    assert data[0]["subnet_id"] == "subnet-abc12345"
    assert data[0]["subnet_cidr"] == "10.0.1.0/24"
    assert data[0]["subnet_name"] == "private-a"
    assert data[0]["owner_account_id"] == "111122223333"
    assert data[0]["region"] == "us-east-1"
    assert ":ec2:us-east-1:" in data[0]["subnet_arn"]
    assert data[0]["subnet_arn"].endswith(":subnet/subnet-abc12345")


def test_main_invokes_netbox_sync_after_discover(monkeypatch):
    monkeypatch.setenv("NETBOX_URL", "https://netbox.example/")
    monkeypatch.setenv("NETBOX_TOKEN", "nbt_testtoken")

    sync_calls = []

    class DummySync:
        def __init__(self, api, **kwargs):
            self._api = api

        def sync_discovered_vpc(self, data):
            sync_calls.append(data)

    class DummyDiscover:
        def __init__(self, vpc_id, aws_profile=None, aws_region=None):
            self._vpc_id = vpc_id

        def discover(self):
            self.vpc_data = {
                "vpc_id": self._vpc_id,
                "vpc_name": "test",
                "vpc_arn": f"arn:aws:ec2:us-east-1:111111111111:vpc/{self._vpc_id}",
                "vpc_cidr": "10.0.0.0/16",
                "vpc_secondary_ipv4_cidrs": [],
                "vpc_ipv6_cidrs": [],
                "owner_account_id": "111111111111",
                "region": "us-east-1",
            }

    monkeypatch.setattr("extras.scripts.add_vpc_to_netbox.netbox_sync.NetBoxSync", DummySync)
    monkeypatch.setattr("extras.scripts.add_vpc_to_netbox.cli.DiscoverVPC", DummyDiscover)
    api_mock = mock.Mock()
    monkeypatch.setattr(
        "extras.scripts.add_vpc_to_netbox.netbox_sync.connect_pynetbox",
        lambda url, token: api_mock,
    )

    from extras.scripts.add_vpc_to_netbox import cli as mod

    rc = mod.main(
        [
            "vpc-0123456789abcdef0",
            "--netbox-url",
            "https://nb.example/",
            "--netbox-token",
            "secret",
        ]
    )
    assert rc == 0
    assert len(sync_calls) == 1
    assert sync_calls[0]["vpc_id"] == "vpc-0123456789abcdef0"
