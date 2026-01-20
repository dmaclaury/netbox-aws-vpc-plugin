"""Top-level package for NetBox AWS VPC Plugin."""

__author__ = """Daniel MacLaury"""
__email__ = "daniel@danielmaclaury.com"
__version__ = "0.1.0"


import importlib.metadata

from netbox.plugins import PluginConfig


class AWSVPCConfig(PluginConfig):
    name = "netbox_aws_vpc_plugin"
    verbose_name = "NetBox AWS VPC Plugin"
    description = "NetBox plugin for modeling AWS VPCs in NetBox"
    version = importlib.metadata.version("netbox-aws-vpc-plugin")
    base_url = "aws-vpc"
    min_version = "4.5.0"
    author = __author__
    author_email = __email__


config = AWSVPCConfig
