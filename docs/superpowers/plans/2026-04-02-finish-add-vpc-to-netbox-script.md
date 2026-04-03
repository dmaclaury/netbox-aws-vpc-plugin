# Finish add_vpc_to_netbox script — TDD implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a boto3-driven script that discovers an AWS VPC (and later subnets), then creates or updates NetBox **core** objects (`ipam.Prefix`, optional `dcim.Region` link) and **plugin** objects (`AWSAccount`, `AWSVPC`, `AWSSubnet`) via the plugin REST API, with idempotent reruns and `--dry-run`.

**Architecture:** Keep **AWS discovery** in [`extras/scripts/add_vpc_to_netbox.py`](extras/scripts/add_vpc_to_netbox.py) (or a sibling module under `extras/scripts/` if the file grows). Add a small **`extras/scripts/netbox_sync.py`** (name can vary) that wraps pynetbox calls with pagination and natural-key lookups (`vpc_id`, `subnet_id`, `account_id`). **Tests** live under [`extras/scripts/tests/`](extras/scripts/tests/) and use mocks only—no live NetBox or AWS in CI.

**Tech stack:** Python 3.12+, `boto3` / `botocore`, `pynetbox`, `pytest`. NetBox **v2 API tokens** (`Bearer nbt_...`) per [netbox-integration-best-practices SKILL.md](../../../.agents/skills/netbox-integration-best-practices/SKILL.md). Plugin REST paths from [`netbox_aws_vpc_plugin/api/urls.py`](../../../netbox_aws_vpc_plugin/api/urls.py): `aws-accounts`, `aws-vpcs`, `aws-subnets`.

**Related prior plan:** Cursor plan `finish_add_vpc_to_netbox_script` (high-level); this document replaces it for execution detail and TDD ordering.

---

## File map

| File | Responsibility |
|------|----------------|
| [`extras/scripts/add_vpc_to_netbox.py`](../../../extras/scripts/add_vpc_to_netbox.py) | CLI, `DiscoverVPC`, optional `DiscoverSubnetsForVpc`, orchestration calling sync layer |
| **Create** `extras/scripts/netbox_sync.py` | `NetBoxSync` (or functions): ensure prefix, account, region resolve, VPC, subnet; dry-run recording |
| **Create** `extras/scripts/requirements.txt` | `pynetbox`, `boto3` pins for script users (extras-only; do not add to root [`pyproject.toml`](../../../pyproject.toml) without maintainer approval) |
| [`extras/scripts/tests/test_add_vpc_to_netbox.py`](../../../extras/scripts/tests/test_add_vpc_to_netbox.py) | Discovery + CLI unit tests |
| **Create** `extras/scripts/tests/test_netbox_sync.py` | Sync layer tests with mocked pynetbox |
| [`extras/scripts/README.md`](../../../extras/scripts/README.md) | Env vars, token format, examples, region/prefix policy |

---

## Conventions (read once)

- **TDD loop:** add failing test → run pytest (expect FAIL) → minimal implementation → pytest (expect PASS) → commit.
- **Commits:** Conventional Commits, one logical unit per commit (e.g. `test(scripts): ...`, `fix(scripts): ...`, `feat(scripts): ...`).
- **Pagination:** Any `.filter()` / list in pynetbox that can return many rows: iterate pages (see netbox-integration skill: `limit` ≤ 1000; use pynetbox’s pagination or loop until empty).
- **Idempotency:** GET by unique field using `.filter(..., brief=True)` for performance → PATCH if exists, POST if not (for VPC `vpc_id`, subnet `subnet_id`, account `account_id`).
- **Region:** Resolve `dcim.Region` by **slug** equal to AWS region string; if none, omit FK and log (do not auto-create unless you add an explicit task later).
- **Prefix duplicates:** If multiple `ipam.Prefix` match the same `prefix` string, **fail with clear error** (deterministic, documented).

---

### Task 1: Discovery — ARN uses resolved region (TDD)

**Files:**

- Modify: [`extras/scripts/tests/test_add_vpc_to_netbox.py`](../../../extras/scripts/tests/test_add_vpc_to_netbox.py)
- Modify: [`extras/scripts/add_vpc_to_netbox.py`](../../../extras/scripts/add_vpc_to_netbox.py)

- [ ] **Step 1: Write the failing test**

Add a new test that **does not** pass `aws_region` to `DiscoverVPC`, only relies on `mock_client.meta.region_name`, and asserts `vpc_arn` contains `us-west-2` (not `None`).

```python
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
    monkeypatch.setattr("boto3.Session", lambda **kwargs: mock_session)

    d = DiscoverVPC(vpc_id="vpc-aaaaaaaa")
    d.discover()
    assert d.vpc_data["region"] == "us-west-2"
    assert ":ec2:us-west-2:" in d.vpc_data["vpc_arn"]
    assert "None" not in d.vpc_data["vpc_arn"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/daniel/GitHub/netbox-aws-vpc-plugin && python -m pytest extras/scripts/tests/test_add_vpc_to_netbox.py::test_discover_vpc_arn_uses_client_region_when_aws_region_omitted -v
```

Expected: **FAIL** — ARN still contains `None` or wrong region.

- [ ] **Step 3: Minimal implementation**

In `DiscoverVPC.discover()`, after you have `OwnerId` and partition, set `resolved_region = self.aws_region or self.ec2_client.meta.region_name` and use `resolved_region` in the ARN f-string. Set `self.vpc_data["region"] = resolved_region`.

- [ ] **Step 4: Run tests**

Run:

```bash
python -m pytest extras/scripts/tests/test_add_vpc_to_netbox.py -v
```

Expected: **PASS** for the new test; existing tests may still pass or fail until Task 2.

- [ ] **Step 5: Commit**

```bash
git add extras/scripts/add_vpc_to_netbox.py extras/scripts/tests/test_add_vpc_to_netbox.py
git commit -m "fix(scripts): use resolved region in VPC ARN; test ARN without explicit aws_region"
```

---

### Task 2: Discovery — secondary IPv4 from `CidrBlockAssociationSet` (TDD)

**Files:**

- Modify: [`extras/scripts/tests/test_add_vpc_to_netbox.py`](../../../extras/scripts/tests/test_add_vpc_to_netbox.py) (`test_discover_vpc_success` fixture)
- Modify: [`extras/scripts/add_vpc_to_netbox.py`](../../../extras/scripts/add_vpc_to_netbox.py)

- [ ] **Step 1: Write the failing test**

In `test_discover_vpc_success`, replace `Ipv4CidrBlockAssociationSet` with **`CidrBlockAssociationSet`** (real boto3/EC2 shape). Keep primary + secondary blocks. Run pytest — expect **FAIL** (`vpc_secondary_ipv4_cidrs` empty).

- [ ] **Step 2: Implement**

Read secondary IPv4 from `CidrBlockAssociationSet` (associated state, exclude primary `vpc_cidr`). Optionally accept **both** keys for one release if you want backward compatibility with old mocks:

```python
assoc_set = vpc.get("CidrBlockAssociationSet") or vpc.get("Ipv4CidrBlockAssociationSet") or []
```

- [ ] **Step 3: Verify**

```bash
python -m pytest extras/scripts/tests/test_add_vpc_to_netbox.py::test_discover_vpc_success -v
```

Expected: **PASS**

- [ ] **Step 4: Commit**

```bash
git commit -m "fix(scripts): parse VPC secondary IPv4 from CidrBlockAssociationSet"
```

---

### Task 3: Discover subnets (new class or methods) (TDD)

**Files:**

- Modify: [`extras/scripts/add_vpc_to_netbox.py`](../../../extras/scripts/add_vpc_to_netbox.py)
- Modify: [`extras/scripts/tests/test_add_vpc_to_netbox.py`](../../../extras/scripts/tests/test_add_vpc_to_netbox.py)

- [ ] **Step 1: Write the failing test**

Extend `_MockClient` with `describe_subnets(self, Filters=None)` returning one subnet:

```python
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
    # ... monkeypatch Session to return client with describe_subnets
    # d = DiscoverSubnets(ec2_client=..., vpc_id="vpc-12345678", region="us-east-1")
    # data = d.discover()
    # assert data[0]["subnet_id"] == "subnet-abc12345"
```

Adjust design to your preference (`DiscoverVPC` method vs new class); keep **pure dict** output for sync layer.

- [ ] **Step 2: Run — expect FAIL** (`AttributeError` or missing symbol)

- [ ] **Step 3: Implement** `describe_subnets` with `Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]`, map Name tag, CIDR, OwnerId, build ARN like VPC.

- [ ] **Step 4: pytest PASS**

- [ ] **Step 5: Commit** — `feat(scripts): discover subnets for a VPC via EC2`

---

### Task 4: `netbox_sync` — ensure prefix (TDD)

**Files:**

- Create: `extras/scripts/netbox_sync.py`
- Create: `extras/scripts/tests/test_netbox_sync.py`

- [ ] **Step 1: Write the failing test**

```python
def test_ensure_prefix_creates_when_missing():
    calls = []

    class FakePrefixes:
        def filter(self, prefix=None):
            calls.append(("filter", prefix))
            return self

        def list(self):
            return []

        def create(self, **kwargs):
            calls.append(("create", kwargs))
            return type("P", (), {"id": 42})()

    class FakeIpam:
        def __init__(self):
            self.prefixes = FakePrefixes()

    class FakeApi:
        def __init__(self):
            self.ipam = FakeIpam()

    from extras.scripts.netbox_sync import NetBoxSync

    sync = NetBoxSync(api=FakeApi(), dry_run=False)
    pid = sync.ensure_prefix("10.0.0.0/16")
    assert pid == 42
    assert any(c[0] == "create" for c in calls)
```

- [ ] **Step 2: Run — expect FAIL** (import error)

```bash
python -m pytest extras/scripts/tests/test_netbox_sync.py::test_ensure_prefix_creates_when_missing -v
```

- [ ] **Step 3: Implement** `NetBoxSync.ensure_prefix` using real pynetbox when `api` is default; filter by prefix, create with optional `site`/`vrf` from config object.

- [ ] **Step 4: Add test** “returns existing id when prefix found” (filter returns one object with `id=7`).

- [ ] **Step 5: Commit** — `feat(scripts): NetBoxSync.ensure_prefix with tests`

---

### Task 5: `ensure_aws_account` (TDD)

**Files:**

- Modify: `extras/scripts/netbox_sync.py`
- Modify: `extras/scripts/tests/test_netbox_sync.py`

- [ ] **Step 1: Failing test** — mock `plugins.netbox_aws_vpc_plugin.aws_accounts.filter(account_id=...).list()` empty → `create` called with `account_id`, `status` active.

- [ ] **Step 2: Implement** (pagination-safe list; match plugin app label in pynetbox: typically `plugins.netbox_aws_vpc_plugin` — **verify** against your NetBox `/api/plugins/` listing).

- [ ] **Step 3: Second test** — existing account → no `create`, return id.

- [ ] **Step 4: Commit**

---

### Task 6: `resolve_region` + `ensure_aws_vpc` (TDD)

**Files:**

- Modify: `extras/scripts/netbox_sync.py`
- Modify: `extras/scripts/tests/test_netbox_sync.py`

- [ ] **Step 1: Test `resolve_region`** — `dcim.regions.filter(slug="us-east-1").list()` returns `[obj]` → id; empty → `None`.

- [ ] **Step 2: Test `ensure_aws_vpc` POST** — no existing `vpc_id`, builds payload with `vpc_cidr` PK, `owner_account` PK, optional `vpc_secondary_ipv4_cidrs` / `vpc_ipv6_cidrs` as **lists of int** (match [`test_api_crud_vpc`](../../../netbox_aws_vpc_plugin/tests/test_netbox_aws_vpc_plugin.py) style).

- [ ] **Step 3: Test `ensure_aws_vpc` PATCH** — existing object, assert PATCH path with updated `name`/`arn`.

- [ ] **Step 4: Implement** (use `.create()` / `.update()` or partial update per pynetbox patterns).

- [ ] **Step 5: Commit**

---

### Task 7: `ensure_aws_subnet` (TDD)

**Files:**

- Modify: `extras/scripts/netbox_sync.py`
- Modify: `extras/scripts/tests/test_netbox_sync.py`

- [ ] **Step 1: Failing test** — mock plugin subnets endpoint; POST includes `subnet_id`, `vpc` (int pk), `subnet_cidr`, `owner_account`, `region`.

- [ ] **Step 2: Implement**

- [ ] **Step 3: Idempotency test** — existing `subnet_id` → PATCH only.

- [ ] **Step 4: Commit**

---

### Task 8: Dry-run mode (TDD)

**Files:**

- Modify: `extras/scripts/netbox_sync.py`
- Modify: `extras/scripts/tests/test_netbox_sync.py`

- [ ] **Step 1: Test** — `NetBoxSync(..., dry_run=True).ensure_prefix(...)` does not call `create` on fake API; returns a sentinel (e.g. `None`) or logs intent (choose one and document).

- [ ] **Step 2: Implement** — short-circuit mutating calls; allow read-only GET/list for planning if needed.

- [ ] **Step 3: Commit**

---

### Task 9: Wire CLI and env config

**Files:**

- Modify: [`extras/scripts/add_vpc_to_netbox.py`](../../../extras/scripts/add_vpc_to_netbox.py)
- Modify: [`extras/scripts/tests/test_add_vpc_to_netbox.py`](../../../extras/scripts/tests/test_add_vpc_to_netbox.py) (argparse / main smoke with `unittest.mock`)

- [ ] **Step 1: Test** — with env `NETBOX_URL`/`NETBOX_TOKEN` set, mock `NetBoxSync` and assert `main()` invokes sync after discover (use `pytest` `monkeypatch.setenv` + patch constructor).

- [ ] **Step 2: Implement** argparse flags: `--netbox-url`, `--netbox-token` (optional if env set), `--sync-subnets` flag for milestone B behavior, reuse `--dry-run`.

- [ ] **Step 3: Run full extras pytest + `make lint`**

```bash
python -m pytest extras/scripts/tests/ -v
make lint
```

- [ ] **Step 4: Commit**

---

### Task 10: Documentation and extras requirements

**Files:**

- Create: `extras/scripts/requirements.txt`
- Modify: [`extras/scripts/README.md`](../../../extras/scripts/README.md)

- [ ] **Step 1:** Add `pynetbox` and compatible `boto3` pins.

- [ ] **Step 2:** Document `NETBOX_URL`, `NETBOX_TOKEN` (v2 Bearer), optional `NETBOX_SITE_ID` / `NETBOX_VRF_ID`, `--aws-region` requirement for correct EC2 endpoint.

- [ ] **Step 3: Commit** — `docs(scripts): document NetBox sync script and requirements`

---

## Plan review loop (optional but recommended)

1. After this file is complete, dispatch a **plan document reviewer** with: path to this plan, link to plugin models [`aws_vpc.py`](../../../netbox_aws_vpc_plugin/models/aws_vpc.py) / [`aws_subnet.py`](../../../netbox_aws_vpc_plugin/models/aws_subnet.py), and REST test [`test_api_crud_vpc`](../../../netbox_aws_vpc_plugin/tests/test_netbox_aws_vpc_plugin.py).
2. If issues: fix this document, re-review (max 3 rounds, then ask human).

---

## Execution handoff

**Plan complete and saved to** [`docs/superpowers/plans/2026-04-02-finish-add-vpc-to-netbox-script.md`](./2026-04-02-finish-add-vpc-to-netbox-script.md).

**Two execution options:**

1. **Subagent-driven (recommended)** — fresh subagent per task, review between tasks; use **superpowers:subagent-driven-development**.
2. **Inline execution** — same session, batch with checkpoints; use **superpowers:executing-plans**.

**Optional:** Run brainstorming / worktree skill first if you want isolation (`superpowers:using-git-worktrees`).

**Which approach?** (Human or lead agent chooses before coding.)
