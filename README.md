# NetBox AWS VPC Plugin

NetBox plugin for modeling AWS VPCs in NetBox

* Free software: Apache-2.0
* Documentation: <https://dmaclaury.github.io/netbox-aws-vpc-plugin/>

## Features

This plugin provides the following models in NetBox:

* AWS VPC
* AWS Subnet
* AWS Account

## Compatibility

| NetBox Version |   Plugin Version   |
|----------------|--------------------|
|  4.0 - 4.4.x   | >= 0.0.1, <= 0.0.8 |
|      4.5 +     |       >= 0.1.0     |

## Installing

For adding to a NetBox Docker setup see
[the general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

The plugin is available as a Python package on PyPi and can be installed with pip

```bash
pip install netbox-aws-vpc-plugin
```

or by adding to your `local_requirements.txt` or `plugin_requirements.txt` (netbox-docker):

```bash
netbox-aws-vpc-plugin
```

Enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`,
 or if you use netbox-docker, your `/configuration/plugins.py` file :

```python
PLUGINS = [
    'netbox_aws_vpc_plugin'
]

PLUGINS_CONFIG = {
    "netbox_aws_vpc_plugin": {},
}
```

## Credits

Based on the NetBox plugin tutorial:

* [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
* [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.
