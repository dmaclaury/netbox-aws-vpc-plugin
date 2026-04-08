# Optional scripts (`extras/scripts/`)

This directory holds optional tooling that is **not** part of the shipped `netbox_aws_vpc_plugin` package. Install dependencies per tool; nothing here is required for the core plugin.

## Tools

| Tool | Description |
|------|-------------|
| [add_vpc_to_netbox](add_vpc_to_netbox/README.md) | Discover AWS VPCs (and optionally subnets) with **boto3**, then create or update NetBox prefixes and plugin objects via **pynetbox**. |

**Install (add-VPC tool):** from the repository root:

```bash
pip install -r extras/scripts/add_vpc_to_netbox/requirements.txt
```

**Run:**

```bash
python -m extras.scripts.add_vpc_to_netbox --help
```

You can also run the CLI module as a file (repository root on `PYTHONPATH` or run from repo with the path shown):

```bash
python extras/scripts/add_vpc_to_netbox/cli.py --help
```
