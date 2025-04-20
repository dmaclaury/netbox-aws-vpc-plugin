"""Top-level package for NetBox AWS VPC Plugin."""

__author__ = """Daniel MacLaury"""
__email__ = "daniel@danielmaclaury.com"
__version__ = "0.0.1"


from netbox.plugins import PluginConfig


class AWSVPCConfig(PluginConfig):
    name = "netbox_aws_vpc_plugin"
    verbose_name = "NetBox AWS VPC Plugin"
    description = "NetBox plugin for modeling AWS VPCs in NetBox"
    version = "version"
    base_url = "aws-vpc"
    min_version = "4.0.0"


config = AWSVPCConfig
