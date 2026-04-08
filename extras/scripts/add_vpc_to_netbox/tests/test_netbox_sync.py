import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

from extras.scripts.add_vpc_to_netbox import (  # noqa: E402
    STATUS_ACTIVE,
    NetBoxSync,
    connect_pynetbox,
)


def test_ensure_prefix_creates_when_missing():
    calls = []

    class FakePrefixes:
        def filter(self, prefix=None, brief=False):
            calls.append(("filter", prefix, brief))
            return iter([])

        def create(self, **kwargs):
            calls.append(("create", kwargs))
            return type("P", (), {"id": 42})()

    class FakeIpam:
        def __init__(self):
            self.prefixes = FakePrefixes()

    class FakeApi:
        def __init__(self):
            self.ipam = FakeIpam()

    sync = NetBoxSync(api=FakeApi(), dry_run=False)
    pid = sync.ensure_prefix("10.0.0.0/16")
    assert pid == 42
    assert any(c[0] == "create" for c in calls)


def test_ensure_prefix_returns_existing_id():
    class P:
        id = 7

    class FakePrefixes:
        def filter(self, prefix=None, brief=False):
            return iter([P()])

        def create(self, **kwargs):
            raise AssertionError("create should not be called")

    class FakeApi:
        def __init__(self):
            self.ipam = type("I", (), {"prefixes": FakePrefixes()})()

    sync = NetBoxSync(api=FakeApi(), dry_run=False)
    assert sync.ensure_prefix("10.0.0.0/16") == 7


def test_ensure_prefix_duplicate_raises():
    class P:
        id = 1

    class FakePrefixes:
        def filter(self, prefix=None, brief=False):
            return iter([P(), P()])

    class FakeApi:
        def __init__(self):
            self.ipam = type("I", (), {"prefixes": FakePrefixes()})()

    sync = NetBoxSync(api=FakeApi(), dry_run=False)
    with pytest.raises(ValueError, match="Multiple NetBox prefixes"):
        sync.ensure_prefix("10.0.0.0/16")


def test_ensure_prefix_dry_run_no_create():
    creates = []

    class FakePrefixes:
        def filter(self, prefix=None, brief=False):
            return iter([])

        def create(self, **kwargs):
            creates.append(kwargs)
            raise AssertionError("create must not run in dry_run")

    class FakeApi:
        def __init__(self):
            self.ipam = type("I", (), {"prefixes": FakePrefixes()})()

    sync = NetBoxSync(api=FakeApi(), dry_run=True)
    assert sync.ensure_prefix("10.0.0.0/16") is None
    assert creates == []


def test_ensure_aws_account_creates_when_missing():
    creates = []

    class FakeAwsAccounts:
        def filter(self, account_id=None, brief=False):
            return iter([])

        def create(self, **kwargs):
            creates.append(kwargs)
            return type("A", (), {"id": 99})()

    class FakePlugin:
        aws_accounts = FakeAwsAccounts()
        aws_vpcs = None
        aws_subnets = None

    class FakePlugins:
        netbox_aws_vpc_plugin = FakePlugin()

    class FakeApi:
        def __init__(self):
            self.plugins = FakePlugins()

    api = FakeApi()
    sync = NetBoxSync(
        api=api,
        dry_run=False,
        create_aws_account=True,
        plugin_app=api.plugins.netbox_aws_vpc_plugin,
    )
    assert sync.ensure_aws_account("123456789012") == 99
    assert creates == [
        {"account_id": "123456789012", "name": "123456789012", "status": STATUS_ACTIVE},
    ]


def test_ensure_aws_account_returns_existing():
    class FakeAwsAccounts:
        def filter(self, account_id=None, brief=False):
            return iter([type("A", (), {"id": 5})()])

        def create(self, **kwargs):
            raise AssertionError("no create")

    class FakePlugin:
        aws_accounts = FakeAwsAccounts()

    class FakePlugins:
        netbox_aws_vpc_plugin = FakePlugin()

    class FakeApi:
        def __init__(self):
            self.plugins = FakePlugins()

    api = FakeApi()
    sync = NetBoxSync(api=api, dry_run=False, plugin_app=api.plugins.netbox_aws_vpc_plugin)
    assert sync.ensure_aws_account("123456789012") == 5


def test_ensure_aws_account_missing_without_create_flag_returns_none():
    class FakeAwsAccounts:
        def filter(self, account_id=None, brief=False):
            return iter([])

    class FakePlugin:
        aws_accounts = FakeAwsAccounts()

    class FakePlugins:
        netbox_aws_vpc_plugin = FakePlugin()

    class FakeApi:
        def __init__(self):
            self.plugins = FakePlugins()

    api = FakeApi()
    sync = NetBoxSync(
        api=api,
        dry_run=False,
        create_aws_account=False,
        plugin_app=api.plugins.netbox_aws_vpc_plugin,
    )
    assert sync.ensure_aws_account("999999999999") is None


def test_resolve_region_found_and_missing():
    class FakeRegions:
        def __init__(self, rows):
            self._rows = rows

        def filter(self, slug=None, brief=False):
            return iter(self._rows)

    class FakeDcim:
        def __init__(self, rows):
            self.regions = FakeRegions(rows)

    class FakeApi:
        def __init__(self, rows):
            self.dcim = FakeDcim(rows)
            self.plugins = type("P", (), {})()

    sync = NetBoxSync(api=FakeApi([type("R", (), {"id": 3})()]), dry_run=False)
    assert sync.resolve_region("us-east-1") == 3

    sync2 = NetBoxSync(api=FakeApi([]), dry_run=False)
    assert sync2.resolve_region("us-west-2") is None


def test_region_slug_for_netbox_override():
    sync = NetBoxSync(api=object(), netbox_region_slug="aws-us-east-1")
    assert sync.region_slug_for_netbox("us-east-1") == "aws-us-east-1"
    assert sync.region_slug_for_netbox(None) == "aws-us-east-1"


def test_region_slug_for_netbox_defaults_to_aws():
    sync = NetBoxSync(api=object())
    assert sync.region_slug_for_netbox("us-west-2") == "us-west-2"
    assert sync.region_slug_for_netbox(None) is None


def test_ensure_aws_vpc_post():
    creates = []

    class FakeAwsVpcs:
        def filter(self, vpc_id=None, brief=False):
            return iter([])

        def create(self, **kwargs):
            creates.append(kwargs)
            return type("V", (), {"id": 200})()

    class FakePlugin:
        aws_vpcs = FakeAwsVpcs()

    class FakePlugins:
        netbox_aws_vpc_plugin = FakePlugin()

    class FakeApi:
        def __init__(self):
            self.plugins = FakePlugins()

    api = FakeApi()
    sync = NetBoxSync(api=api, dry_run=False, plugin_app=api.plugins.netbox_aws_vpc_plugin)
    pk = sync.ensure_aws_vpc(
        vpc_id="vpc-newone",
        name="my",
        arn="arn:aws:ec2:us-east-1:1:vpc/vpc-newone",
        vpc_cidr_id=10,
        owner_account_id=20,
        secondary_ipv4_prefix_ids=[11, 12],
        ipv6_prefix_ids=[13],
        region_id=3,
    )
    assert pk == 200
    assert creates[0]["vpc_id"] == "vpc-newone"
    assert creates[0]["vpc_cidr"] == 10
    assert creates[0]["owner_account"] == 20
    assert creates[0]["vpc_secondary_ipv4_cidrs"] == [11, 12]
    assert creates[0]["vpc_ipv6_cidrs"] == [13]
    assert creates[0]["region"] == 3


def test_ensure_aws_vpc_patch():
    class FakeRecord:
        id = 55
        updates = []

        def update(self, data):
            self.updates.append(data)

    rec = FakeRecord()

    class FakeAwsVpcs:
        def filter(self, vpc_id=None, brief=False):
            return iter([rec])

        def create(self, **kwargs):
            raise AssertionError("no create")

    class FakePlugin:
        aws_vpcs = FakeAwsVpcs()

    class FakePlugins:
        netbox_aws_vpc_plugin = FakePlugin()

    class FakeApi:
        def __init__(self):
            self.plugins = FakePlugins()

    api = FakeApi()
    sync = NetBoxSync(api=api, dry_run=False, plugin_app=api.plugins.netbox_aws_vpc_plugin)
    assert (
        sync.ensure_aws_vpc(
            vpc_id="vpc-existing",
            name="new-name",
            arn="arn:new",
            vpc_cidr_id=1,
            owner_account_id=2,
            secondary_ipv4_prefix_ids=[30],
            ipv6_prefix_ids=[31],
            region_id=4,
        )
        == 55
    )
    assert rec.updates[0]["name"] == "new-name"
    assert rec.updates[0]["arn"] == "arn:new"
    assert rec.updates[0]["region"] == 4
    assert rec.updates[0]["vpc_secondary_ipv4_cidrs"] == [30]
    assert rec.updates[0]["vpc_ipv6_cidrs"] == [31]


def test_ensure_aws_subnet_post_and_patch():
    creates = []

    class FakeRecord:
        def __init__(self):
            self.id = 77
            self.updates = []

        def update(self, data):
            self.updates.append(data)

    rec = FakeRecord()

    class FakeAwsSubnets:
        def __init__(self):
            self._existing = False

        def filter(self, subnet_id=None, brief=False):
            if self._existing:
                return iter([rec])
            return iter([])

        def create(self, **kwargs):
            creates.append(kwargs)
            return type("S", (), {"id": 88})()

    ep = FakeAwsSubnets()

    class FakePlugin:
        aws_subnets = ep

    class FakePlugins:
        netbox_aws_vpc_plugin = FakePlugin()

    class FakeApi:
        def __init__(self):
            self.plugins = FakePlugins()

    api = FakeApi()
    sync = NetBoxSync(api=api, dry_run=False, plugin_app=api.plugins.netbox_aws_vpc_plugin)
    assert (
        sync.ensure_aws_subnet(
            subnet_id="subnet-new",
            vpc_nb_id=1,
            subnet_cidr_id=2,
            owner_account_id=3,
            region_id=4,
            name="sn",
            arn="arn:subnet",
        )
        == 88
    )
    assert creates[0]["subnet_id"] == "subnet-new"
    assert creates[0]["vpc"] == 1
    assert creates[0]["subnet_cidr"] == 2
    assert creates[0]["owner_account"] == 3
    assert creates[0]["region"] == 4

    ep._existing = True
    rec.updates = []
    assert (
        sync.ensure_aws_subnet(
            subnet_id="subnet-new",
            vpc_nb_id=1,
            subnet_cidr_id=2,
            owner_account_id=3,
            name="patched",
            arn="arn:2",
        )
        == 77
    )
    assert rec.updates[0]["name"] == "patched"
    assert rec.updates[0]["arn"] == "arn:2"


def test_sync_discovered_vpc_wires_prefixes_and_vpc():
    calls = []

    class Tracking(NetBoxSync):
        def ensure_prefix(self, prefix):
            calls.append(("prefix", prefix))
            return {"10.0.0.0/16": 1, "10.1.0.0/16": 2, "2001:db8::/56": 3}[prefix]

        def ensure_aws_account(self, account_id):
            calls.append(("account", account_id))
            return 9

        def resolve_region(self, slug):
            calls.append(("region", slug))
            return 8

        def ensure_aws_vpc(self, **kwargs):
            calls.append(("vpc", kwargs))
            return 100

    class FakeApi:
        pass

    sync = Tracking(api=FakeApi(), dry_run=False)
    data = {
        "vpc_id": "vpc-abcd1234",
        "vpc_name": "main",
        "vpc_arn": "arn:aws:ec2:eu-west-1:1:vpc/vpc-abcd1234",
        "vpc_cidr": "10.0.0.0/16",
        "vpc_secondary_ipv4_cidrs": ["10.1.0.0/16"],
        "vpc_ipv6_cidrs": ["2001:db8::/56"],
        "owner_account_id": "999999999999",
        "region": "eu-west-1",
    }
    assert sync.sync_discovered_vpc(data) == 100
    vpc_call = next(c for c in calls if c[0] == "vpc")[1]
    assert vpc_call["vpc_cidr_id"] == 1
    assert vpc_call["secondary_ipv4_prefix_ids"] == [2]
    assert vpc_call["ipv6_prefix_ids"] == [3]


def test_connect_pynetbox_forces_bearer_nbt_without_dot(monkeypatch):
    calls = []

    def fake_api(url, token=None):
        calls.append((url, token))

        class Fake:
            http_session = type("S", (), {"headers": {}})()

        return Fake()

    import pynetbox

    monkeypatch.setattr(pynetbox, "api", fake_api)

    api = connect_pynetbox("https://netbox.example", "nbt_abc123")
    assert calls == [("https://netbox.example", None)]
    assert api.http_session.headers["Authorization"] == "Bearer nbt_abc123"


def test_connect_pynetbox_passes_token_when_dotted_v2_or_legacy(monkeypatch):
    calls = []

    def fake_api(url, token=None):
        calls.append((url, token))
        return object()

    import pynetbox

    monkeypatch.setattr(pynetbox, "api", fake_api)

    connect_pynetbox("https://x", "nbt_1.a_real_secret")
    assert calls[-1] == ("https://x", "nbt_1.a_real_secret")

    connect_pynetbox("https://x", "d6f4e314a5b5fefd164995169f28ae32d987704f")
    assert calls[-1] == ("https://x", "d6f4e314a5b5fefd164995169f28ae32d987704f")
