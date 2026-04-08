"""Optional tooling: discover AWS VPCs/subnets and sync to NetBox via pynetbox."""

from .cli import DiscoverSubnetsForVpc, DiscoverVPC, main, validate_vpc_id
from .netbox_sync import (
    PLUGIN_API_SLUG,
    STATUS_ACTIVE,
    NetBoxSync,
    connect_pynetbox,
)

__all__ = [
    "PLUGIN_API_SLUG",
    "STATUS_ACTIVE",
    "DiscoverSubnetsForVpc",
    "DiscoverVPC",
    "NetBoxSync",
    "connect_pynetbox",
    "main",
    "validate_vpc_id",
]
