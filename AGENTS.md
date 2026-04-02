<!-- FOR AI AGENTS — structured for automation; keep section order stable -->
<!-- Last updated: 2026-04-02 | Last verified: 2026-04-02 -->

# AGENTS.md

**Precedence:** the **closest `AGENTS.md`** to the files you are changing wins. Root holds global defaults; scoped files are listed in [`ROADMAP.md`](ROADMAP.md) as a future improvement.

**Claude / other tools:** [`CLAUDE.md`](CLAUDE.md) is a symlink to this file.

## Project

| Item | Value |
|------|--------|
| Purpose | [NetBox](https://github.com/netbox-community/netbox) plugin: custom models for **AWS Account**, **AWS VPC**, **AWS Subnet**, linked with core NetBox objects (e.g. Prefix, Region, Tenant). |
| Language | Python `>=3.12` ([`pyproject.toml`](pyproject.toml)) |
| Package | `netbox_aws_vpc_plugin` ([`netbox_aws_vpc_plugin/`](netbox_aws_vpc_plugin/)) — models, UI, REST, GraphQL |
| NetBox compatibility | See [README.md — Compatibility](README.md). For **local dev**, treat **NetBox 4.5** as the current minor series; pin the NetBox image with `NETBOX_VERSION` (example: `v4.5-3.4.2` in [`.devcontainer/README.md`](.devcontainer/README.md)). |
| Plugin development | Follow [NetBox plugin development](https://netboxlabs.com/docs/netbox/plugins/development/) — including **REST and GraphQL** for plugin objects ([`api/`](netbox_aws_vpc_plugin/api/), [`graphql/`](netbox_aws_vpc_plugin/graphql/)). |
| Broader NetBox integration | [`skills-lock.json`](skills-lock.json) references [netboxlabs/netbox-best-practices](https://github.com/netboxlabs/netbox-best-practices) (general NetBox usage, not plugin-specific). In-repo copy: [`.agents/skills/netbox-integration-best-practices/`](.agents/skills/netbox-integration-best-practices/). |

## Branching and releases

| Rule | Detail |
|------|--------|
| Default branch | `main` — **do not use it for ongoing feature work**; open a **feature branch** instead. |
| Merge | Feature branches merge into `main` via PR; **releases are cut in GitHub** after merge. |
| Versioning | **[Semantic Versioning](https://semver.org/)** — `MAJOR.MINOR.PATCH` in [`pyproject.toml`](pyproject.toml) and GitHub releases (major = breaking API, minor = compatible features, patch = compatible fixes). |
| Legacy CI branches | The repo **does not** use `develop` / `testing` for day-to-day work; some workflows may still mention them. |

## Data model (follow existing patterns)

Review [`netbox_aws_vpc_plugin/models/`](netbox_aws_vpc_plugin/models/) before changing behavior. Summary:

| Model | Role |
|-------|------|
| **AWSAccount** | Unique `account_id`; optional `tenancy.Tenant`; status via `AWSAccountStatusChoices`. |
| **AWSVPC** | Unique `vpc_id`; primary IPv4 → `ipam.Prefix` (`vpc_cidr`); secondary IPv4 + IPv6 → M2M to `Prefix` (see [`constants.py`](netbox_aws_vpc_plugin/constants.py) `IPV4_PREFIXES` / `IPV6_PREFIXES`); optional `owner_account` → `AWSAccount`, `dcim.Region`; status. |
| **AWSSubnet** | Unique `subnet_id`; IPv4 / IPv6 CIDR → `Prefix` FKs; `vpc` → `AWSVPC` (**CASCADE**); optional `owner_account`, `region`; status. |

All three extend **`NetBoxModel`** (NetBox tags, custom fields, change logging, etc.).

## Commands

> CI definitions: [`.github/workflows/test.yml`](.github/workflows/test.yml), [`.github/workflows/format-check.yml`](.github/workflows/format-check.yml). Prefer those when local and CI differ.

| Task | Command | Notes |
|------|---------|--------|
| Format | `make format` | `isort` + `black` (see [`Makefile`](Makefile)) |
| Lint | `make lint` | `flake8 netbox_aws_vpc_plugin` |
| Pre-commit | `make pre-commit` or `pre-commit run --all-files` | Also runs in CI |
| Tests (integration, matches CI) | From NetBox app dir with plugin installed: `python netbox/manage.py test netbox_aws_vpc_plugin.tests --parallel -v2` | CI checks out `netbox-community/netbox` @ `main`, installs this plugin, then runs this ([`test.yml`](.github/workflows/test.yml)) |
| Tests (devcontainer) | Shell alias `netbox-test` | Defined in [`.devcontainer/setup.sh`](.devcontainer/setup.sh) — runs the same `manage.py test` invocation |

**Local install for formatting/lint (no NetBox):** `pip install -r requirements_dev.txt` ([`requirements_dev.txt`](requirements_dev.txt)).

**Do not assume `make test` works end-to-end:** the `Makefile` references a missing `unittest` target — see [`ROADMAP.md`](ROADMAP.md). Use the NetBox `manage.py test` flow above for plugin tests.

## Workflow

1. **Before coding:** Read this file; for NetBox API or integration behavior, see [`.agents/skills/netbox-integration-best-practices/SKILL.md`](.agents/skills/netbox-integration-best-practices/SKILL.md).
2. **After edits:** Run `make lint` and/or `pre-commit run --all-files` for Python-only changes; run plugin tests via NetBox when behavior touches models, API, or migrations.
3. **Before claiming done:** Match CI — formatting (`isort`/`black` checks), `flake8`, `pre-commit`, and (for substantive changes) the NetBox test command above.

## File map (plugin)

```
netbox_aws_vpc_plugin/
├── __init__.py              # PluginConfig
├── api/                     # REST: views, serializers, urls
├── graphql/                 # GraphQL types, filters, schema
├── models/                  # AWSAccount, AWSVPC, AWSSubnet
├── migrations/
├── tests/
├── navigation.py, views.py, urls.py, forms.py, filtersets.py, tables.py, search.py
├── choices.py, constants.py
└── templates/               # (package data in pyproject)
```

**Extras (not core plugin):** [`extras/`](extras/) — scripts, examples, and optional tooling **outside** the shipped package (`models`, API, GraphQL, UI, migrations). **AWS API usage** (e.g. `boto3`) is **optional** and only relevant when developing or running these extras (see work in progress such as [`extras/scripts/add_vpc_to_netbox.py`](extras/scripts/add_vpc_to_netbox.py)). Do not require AWS for core plugin behavior.

## Development environment

| Approach | Entry |
|----------|--------|
| Dev container | [`.devcontainer/`](.devcontainer/) — Docker Compose, NetBox on port **8000**, [`devcontainer.json`](.devcontainer/devcontainer.json), [`setup.sh`](.devcontainer/setup.sh) |
| venv (docs) | [README.md — Development](README.md) |

## CI / quality gates

| Workflow | Trigger | Role |
|----------|---------|------|
| `test.yml` | Pull requests | Matrix Python **3.12, 3.13, 3.14**; Postgres + Redis services; NetBox `main` + plugin; `manage.py test netbox_aws_vpc_plugin.tests --parallel` |
| `format-check.yml` | PR/push (see workflow for branch list) | `isort --check-only`, `black --check`, `make lint`, `pre-commit run --all-files` |

## Boundaries

### Always

- Run the same checks CI runs before opening a PR when your change touches those areas.
- Add or update tests under `netbox_aws_vpc_plugin/tests/` for new behavior; migrations belong in `netbox_aws_vpc_plugin/migrations/`.
- Match existing style: **Black** line length **120** in [`pyproject.toml`](pyproject.toml) (editor rulers in devcontainer may differ).
- Use **[Conventional Commits](https://www.conventionalcommits.org/)** for commit messages (e.g. `type(scope): description`).

### Ask first

- Adding dependencies ([`pyproject.toml`](pyproject.toml) / [`requirements_dev.txt`](requirements_dev.txt)).
- Changing CI workflows or supported Python / NetBox matrix.
- Breaking changes to serializers, GraphQL types, or model fields.

### Never

- Commit secrets, production AWS credentials, or real NetBox tokens.
- Delete or rewrite applied Django migrations; add new migrations for schema changes instead.
- Land **feature development** directly on `main` — use a feature branch and PR.

### Extras vs core

- Core plugin changes belong under [`netbox_aws_vpc_plugin/`](netbox_aws_vpc_plugin/).
- [`extras/`](extras/) is for optional scripts and use cases; keep AWS-dependent code there unless the project explicitly expands scope.

## Golden samples (patterns)

| Area | Reference |
|------|-----------|
| Model definition | [`netbox_aws_vpc_plugin/models/aws_vpc.py`](netbox_aws_vpc_plugin/models/aws_vpc.py), [`aws_subnet.py`](netbox_aws_vpc_plugin/models/aws_subnet.py), [`aws_account.py`](netbox_aws_vpc_plugin/models/aws_account.py) |
| REST API | [`netbox_aws_vpc_plugin/api/`](netbox_aws_vpc_plugin/api/) |
| GraphQL | [`netbox_aws_vpc_plugin/graphql/`](netbox_aws_vpc_plugin/graphql/) |
| Plugin registration | [`netbox_aws_vpc_plugin/__init__.py`](netbox_aws_vpc_plugin/__init__.py) |

## Contributing (agents)

- Link issues when applicable; describe what changed and why.
- Prefer small, reviewable changes; avoid unrelated refactors in the same PR.
- Branch from `main`, open a PR back to `main`; maintainers cut **releases in GitHub** after merge.
- Bump versions per **SemVer** when releasing; write commits using **Conventional Commits** so history stays readable and release notes stay traceable.
