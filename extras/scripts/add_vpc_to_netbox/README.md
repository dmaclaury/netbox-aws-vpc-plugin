# Add VPC to NetBox (`add_vpc_to_netbox`)

Example tooling that discovers AWS VPCs (and optionally subnets) with **boto3**, then creates or updates **NetBox** `ipam.Prefix` rows and plugin objects (`AWSAccount`, `AWSVPC`, `AWSSubnet`) through the REST API via **pynetbox**.

## Install

From the repository root (use a virtualenv if you like):

```bash
pip install -r extras/scripts/add_vpc_to_netbox/requirements.txt
```

## Entry points

- **`python -m extras.scripts.add_vpc_to_netbox`** — preferred (uses `__main__.py`).
- **`python extras/scripts/add_vpc_to_netbox/cli.py`** — same CLI when run from the repo (ensures the repository root is on `sys.path` for the `extras` package).

### NetBox authentication

NetBox 4.x **v2 API tokens** (`nbt_…`) are sent as Bearer tokens. Set:

| Variable / flag | Purpose |
|-----------------|--------|
| `NETBOX_URL` or `--netbox-url` | NetBox base URL (e.g. `https://netbox.example.com`) |
| `NETBOX_TOKEN` or `--netbox-token` | API token (v2 format) |

If either URL or token is missing, the script still runs **AWS discovery only** and does not call NetBox.

**Troubleshooting:** If NetBox returns `403` with `Invalid v1 token`, the client was using legacy `Authorization: Token …` while your key is a v2 `nbt_…` token. This script’s `connect_pynetbox()` forces `Bearer` for `nbt_` tokens that pynetbox would otherwise mis-detect. Prefer tokens in the documented form `nbt_<id>.<secret>` (includes a dot).

Optional:

| Variable | Purpose |
|----------|--------|
| `NETBOX_SITE_ID` | If set, passed as `site` when creating new `ipam.Prefix` objects (integer PK). |
| `NETBOX_VRF_ID` | If set, passed as `vrf` when creating new prefixes (integer PK). |
| `NETBOX_REGION_SLUG` or `--netbox-region-slug` | `dcim.Region` **slug** for linking VPC/subnet region (default: same as AWS region, e.g. `us-east-1`). Use when your regions use a different slug (e.g. `aws-us-east-1`). |

### AWS

| Flag | Purpose |
|------|--------|
| `--aws-profile` | AWS profile name for `boto3.Session`. |
| `--aws-region` | Region for the EC2 client. Use the VPC’s region so `describe_vpcs` / `describe_subnets` hit the correct endpoint. |

### Sync behavior

| Flag | Purpose |
|------|--------|
| `--dry-run` | Log intended NetBox creates/updates; no `POST`/`PATCH` (reads such as prefix lookups may still run). |
| `--sync-subnets` | After syncing the VPC, discover subnets in that VPC and sync each to `AWSSubnet`. |

### Example

```bash
export NETBOX_URL=https://netbox.example.com
export NETBOX_TOKEN=nbt_your_token_here
python -m extras.scripts.add_vpc_to_netbox vpc-0123456789abcdef0 \
  --aws-region us-east-1 \
  --sync-subnets
```

## Layout

| File | Role |
|------|------|
| `cli.py` | CLI, `DiscoverVPC`, `DiscoverSubnetsForVpc` |
| `netbox_sync.py` | `NetBoxSync`: prefixes, accounts, regions, VPCs, subnets |
| `tests/` | `pytest` with mocks (no live AWS or NetBox required) |

The plugin REST base path is **`/api/plugins/aws-vpc/`** (e.g. `…/aws-accounts/`, `…/aws-vpcs/`). That matches NetBox Swagger and `PluginConfig.base_url` in this repo’s `netbox_aws_vpc_plugin` package.

Run tests from the repo root (with dev dependencies such as `pytest` installed):

```bash
python -m pytest extras/scripts/add_vpc_to_netbox/tests/ -v
```
