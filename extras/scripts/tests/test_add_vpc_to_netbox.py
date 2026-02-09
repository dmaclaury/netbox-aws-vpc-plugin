import os
import sys

import pytest
from botocore.exceptions import ClientError

# Ensure repository root is on sys.path so `extras` can be imported as a package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from extras.scripts.add_vpc_to_netbox import DiscoverVPC, validate_vpc_id  # noqa: E402


class _MockClient:
    def __init__(self, response=None, raise_exc=None, region_name="us-east-1"):
        self._response = response
        self._raise = raise_exc
        self.meta = type("M", (), {"region_name": region_name})

    def describe_vpcs(self, VpcIds=None):
        if self._raise:
            raise self._raise
        return self._response


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
                "Ipv4CidrBlockAssociationSet": [
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
    monkeypatch.setattr("boto3.Session", lambda **kwargs: mock_session)

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
    monkeypatch.setattr("boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverVPC(vpc_id="vpc-00000000", aws_region="us-west-2")
    res = d.discover()
    assert res is None
    assert d.vpc_data["vpc_id"] is None


def test_discover_vpc_client_error(monkeypatch):
    err = ClientError(
        {"Error": {"Code": "InvalidVpcID.NotFound", "Message": "Not found"}},
        "DescribeVpcs",
    )
    mock_client = _MockClient(raise_exc=err)
    mock_session = _MockSession(client=mock_client)
    monkeypatch.setattr("boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverVPC(vpc_id="vpc-doesnotexist", aws_region="us-west-2")
    res = d.discover()
    assert res is None
