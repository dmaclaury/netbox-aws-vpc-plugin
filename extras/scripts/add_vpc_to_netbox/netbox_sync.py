"""
pynetbox-backed sync for ``extras.scripts.add_vpc_to_netbox`` (see ``cli.py``).

Uses brief=True on filters for lighter responses. Dry-run skips creates/updates;
reads (filter/list) are still performed so planning matches a real run.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

STATUS_ACTIVE = "ACTIVE"

# NetBox REST path segment for this plugin: ``/api/plugins/<slug>/…`` — must match
# ``PluginConfig.base_url`` in ``netbox_aws_vpc_plugin`` (see Swagger).
PLUGIN_API_SLUG = "aws-vpc"


def connect_pynetbox(url: str, token: str) -> Any:
    """Build a :mod:`pynetbox` ``Api`` with correct auth for NetBox 4.5+.

    v2 tokens use ``Authorization: Bearer nbt_...``. pynetbox only switches to Bearer when
    the token matches ``nbt_<id>.<secret>`` (a dot in the secret segment). Valid v2 tokens
    without that shape were sent as legacy ``Token``, which NetBox rejects with
    ``403 {'detail': 'Invalid v1 token'}``.
    """
    import pynetbox
    from pynetbox.core.query import _is_v2_token

    token = (token or "").strip()
    url = (url or "").strip().rstrip("/")
    if not url or not token:
        raise ValueError("NetBox url and token are required")

    if token.startswith("nbt_") and not _is_v2_token(token):
        api = pynetbox.api(url, token=None)
        api.http_session.headers["Authorization"] = f"Bearer {token}"
        return api

    return pynetbox.api(url, token=token)


class NetBoxSync:
    def __init__(
        self,
        api: Any,
        *,
        dry_run: bool = False,
        site_id: int | None = None,
        vrf_id: int | None = None,
        create_aws_account: bool = False,
        plugin_app: Any | None = None,
        netbox_region_slug: str | None = None,
    ):
        self.api = api
        self.dry_run = dry_run
        self.site_id = site_id
        self.vrf_id = vrf_id
        self.create_aws_account = create_aws_account
        self._plugin_app_override = plugin_app
        self.netbox_region_slug = (netbox_region_slug or "").strip() or None

    def _prefixes(self):
        return self.api.ipam.prefixes

    def _plugin(self):
        if self._plugin_app_override is not None:
            return self._plugin_app_override
        from pynetbox.core.app import App

        if not hasattr(self, "_cached_plugin_app"):
            # ``nb.plugins.netbox_aws_vpc_plugin`` maps to the wrong path (hyphenated package name).
            # The real API is ``/api/plugins/<PluginConfig.base_url>/`` (e.g. ``aws-vpc``).
            self._cached_plugin_app = App(self.api, f"plugins/{PLUGIN_API_SLUG}")
        return self._cached_plugin_app

    def ensure_prefix(self, prefix: str) -> int | None:
        matches = list(self._prefixes().filter(prefix=prefix, brief=True))
        if len(matches) > 1:
            raise ValueError(
                f"Multiple NetBox prefixes match {prefix!r}; resolve duplicates before syncing.",
            )
        if len(matches) == 1:
            return matches[0].id
        if self.dry_run:
            logger.info("dry-run: would create ipam.Prefix %s", prefix)
            return None
        payload: dict[str, Any] = {"prefix": prefix}
        if self.site_id is not None:
            payload["site"] = self.site_id
        if self.vrf_id is not None:
            payload["vrf"] = self.vrf_id
        created = self._prefixes().create(**payload)
        return created.id

    def ensure_aws_account(self, account_id: str) -> int | None:
        from pynetbox.core.query import RequestError

        if not account_id:
            return None
        try:
            matches = list(self._plugin().aws_accounts.filter(account_id=account_id, brief=True))
        except RequestError as exc:
            logger.error(
                "NetBox API error while looking up AWS account %s (check URL, token, and plugin install): %s",
                account_id,
                exc,
            )
            return None
        if matches:
            return matches[0].id
        if not self.create_aws_account:
            logger.warning(
                "No AWSAccount in NetBox for owner %s; skipping account create "
                "(use --create-aws-account to create it, or create it in the UI)",
                account_id,
            )
            return None
        if self.dry_run:
            logger.info("dry-run: would create AWSAccount %s", account_id)
            return None
        created = self._plugin().aws_accounts.create(
            account_id=account_id,
            name=account_id,
            status=STATUS_ACTIVE,
        )
        return created.id

    def region_slug_for_netbox(self, aws_region: str | None) -> str | None:
        """Slug passed to ``dcim.regions`` lookup: optional override or AWS region string."""
        if self.netbox_region_slug:
            return self.netbox_region_slug
        if not aws_region:
            return None
        return aws_region.strip() or None

    def resolve_region(self, slug: str | None) -> int | None:
        if not slug:
            return None
        matches = list(self.api.dcim.regions.filter(slug=slug, brief=True))
        if not matches:
            logger.warning("No dcim.Region with slug %r; region FK will be omitted", slug)
            return None
        if len(matches) > 1:
            raise ValueError(f"Multiple dcim.Region objects match slug {slug!r}")
        return matches[0].id

    def ensure_aws_vpc(
        self,
        *,
        vpc_id: str,
        name: str | None,
        arn: str | None,
        vpc_cidr_id: int | None,
        owner_account_id: int | None,
        secondary_ipv4_prefix_ids: list[int] | None = None,
        ipv6_prefix_ids: list[int] | None = None,
        region_id: int | None = None,
    ) -> int | None:
        secondary_ipv4_prefix_ids = secondary_ipv4_prefix_ids or []
        ipv6_prefix_ids = ipv6_prefix_ids or []
        ep = self._plugin().aws_vpcs
        matches = list(ep.filter(vpc_id=vpc_id, brief=True))

        if matches:
            rec = matches[0]
            patch: dict[str, Any] = {
                "name": name or "",
                "arn": arn or "",
            }
            if region_id is not None:
                patch["region"] = region_id
            if secondary_ipv4_prefix_ids:
                patch["vpc_secondary_ipv4_cidrs"] = secondary_ipv4_prefix_ids
            if ipv6_prefix_ids:
                patch["vpc_ipv6_cidrs"] = ipv6_prefix_ids
            if self.dry_run:
                logger.info("dry-run: would PATCH aws-vpc id=%s %s", rec.id, patch)
                return rec.id
            rec.update(patch)
            return rec.id

        if self.dry_run:
            logger.info(
                "dry-run: would POST aws-vpc vpc_id=%s vpc_cidr=%s owner_account=%s",
                vpc_id,
                vpc_cidr_id,
                owner_account_id,
            )
            return None
        if vpc_cidr_id is None:
            raise ValueError("vpc_cidr_id is required to create an AWS VPC in NetBox")
        if owner_account_id is None:
            raise ValueError(
                "owner_account_id is required to create an AWS VPC in NetBox "
                "(use --create-aws-account if the account object does not exist yet)",
            )

        payload: dict[str, Any] = {
            "vpc_id": vpc_id,
            "vpc_cidr": vpc_cidr_id,
            "owner_account": owner_account_id,
            "status": STATUS_ACTIVE,
        }
        if name:
            payload["name"] = name
        if arn:
            payload["arn"] = arn
        if region_id is not None:
            payload["region"] = region_id
        if secondary_ipv4_prefix_ids:
            payload["vpc_secondary_ipv4_cidrs"] = secondary_ipv4_prefix_ids
        if ipv6_prefix_ids:
            payload["vpc_ipv6_cidrs"] = ipv6_prefix_ids
        created = ep.create(**payload)
        return created.id

    def ensure_aws_subnet(
        self,
        *,
        subnet_id: str,
        vpc_nb_id: int,
        subnet_cidr_id: int | None,
        owner_account_id: int | None,
        region_id: int | None = None,
        name: str | None = None,
        arn: str | None = None,
        subnet_ipv6_cidr_id: int | None = None,
    ) -> int | None:
        ep = self._plugin().aws_subnets
        matches = list(ep.filter(subnet_id=subnet_id, brief=True))

        if matches:
            rec = matches[0]
            patch: dict[str, Any] = {"name": name or "", "arn": arn or ""}
            if region_id is not None:
                patch["region"] = region_id
            if self.dry_run:
                logger.info("dry-run: would PATCH aws-subnet id=%s %s", rec.id, patch)
                return rec.id
            rec.update(patch)
            return rec.id

        if self.dry_run:
            logger.info(
                "dry-run: would POST aws-subnet subnet_id=%s vpc=%s subnet_cidr=%s owner_account=%s",
                subnet_id,
                vpc_nb_id,
                subnet_cidr_id,
                owner_account_id,
            )
            return None
        if subnet_cidr_id is None:
            raise ValueError("subnet_cidr_id is required to create an AWS subnet in NetBox")
        if owner_account_id is None:
            raise ValueError("owner_account_id is required to create an AWS subnet in NetBox")

        payload: dict[str, Any] = {
            "subnet_id": subnet_id,
            "vpc": vpc_nb_id,
            "subnet_cidr": subnet_cidr_id,
            "owner_account": owner_account_id,
            "status": STATUS_ACTIVE,
        }
        if name:
            payload["name"] = name
        if arn:
            payload["arn"] = arn
        if region_id is not None:
            payload["region"] = region_id
        if subnet_ipv6_cidr_id is not None:
            payload["subnet_ipv6_cidr"] = subnet_ipv6_cidr_id
        created = ep.create(**payload)
        return created.id

    def sync_discovered_vpc(self, vpc_data: dict[str, Any]) -> int | None:
        vpc_id = vpc_data.get("vpc_id")
        if not vpc_id:
            return None

        primary = self.ensure_prefix(vpc_data["vpc_cidr"])
        sec_ids: list[int] = []
        for cidr in vpc_data.get("vpc_secondary_ipv4_cidrs") or []:
            pid = self.ensure_prefix(cidr)
            if pid is not None:
                sec_ids.append(pid)
        v6_ids: list[int] = []
        for cidr in vpc_data.get("vpc_ipv6_cidrs") or []:
            pid = self.ensure_prefix(cidr)
            if pid is not None:
                v6_ids.append(pid)

        acc_id = self.ensure_aws_account(vpc_data["owner_account_id"])
        region_pk = self.resolve_region(self.region_slug_for_netbox(vpc_data.get("region")))

        if acc_id is None and not self.dry_run:
            logger.error(
                "Cannot sync VPC to NetBox: no AWSAccount for owner %s. "
                "Create the account in NetBox or pass --create-aws-account.",
                vpc_data.get("owner_account_id"),
            )
            return None

        return self.ensure_aws_vpc(
            vpc_id=vpc_id,
            name=vpc_data.get("vpc_name"),
            arn=vpc_data.get("vpc_arn"),
            vpc_cidr_id=primary,
            owner_account_id=acc_id,
            secondary_ipv4_prefix_ids=sec_ids,
            ipv6_prefix_ids=v6_ids,
            region_id=region_pk,
        )

    def sync_discovered_subnet(
        self,
        row: dict[str, Any],
        *,
        vpc_nb_id: int | None,
        default_owner_account_id: str | None,
    ) -> int | None:
        sid = row.get("subnet_id")
        if not sid:
            return None

        cidr_id = self.ensure_prefix(row["subnet_cidr"])
        owner_str = row.get("owner_account_id") or default_owner_account_id
        owner_id = self.ensure_aws_account(owner_str) if owner_str else None
        region_pk = self.resolve_region(self.region_slug_for_netbox(row.get("region")))

        v6_ids: list[int] = []
        for c6 in row.get("subnet_ipv6_cidrs") or []:
            p = self.ensure_prefix(c6)
            if p is not None:
                v6_ids.append(p)
        subnet_ipv6_cidr_id = v6_ids[0] if len(v6_ids) == 1 else None
        if len(v6_ids) > 1:
            logger.warning(
                "Subnet %s has multiple IPv6 CIDRs; only first is mapped to subnet_ipv6_cidr",
                sid,
            )

        if vpc_nb_id is None:
            if self.dry_run:
                logger.info("dry-run: would sync subnet %s (VPC not in NetBox yet)", sid)
            else:
                logger.warning("Skipping subnet %s: no NetBox VPC id (sync VPC first)", sid)
            return None

        if owner_id is None and not self.dry_run:
            from pynetbox.core.query import RequestError

            try:
                exists = list(self._plugin().aws_subnets.filter(subnet_id=sid, brief=True))
            except RequestError as exc:
                logger.error("NetBox API error while checking subnet %s: %s", sid, exc)
                return None
            if not exists:
                logger.error(
                    "Cannot sync subnet %s: no AWSAccount for owner %s. "
                    "Use --create-aws-account or create the account in NetBox.",
                    sid,
                    owner_str,
                )
                return None

        return self.ensure_aws_subnet(
            subnet_id=sid,
            vpc_nb_id=vpc_nb_id,
            subnet_cidr_id=cidr_id,
            owner_account_id=owner_id,
            region_id=region_pk,
            name=row.get("subnet_name"),
            arn=row.get("subnet_arn"),
            subnet_ipv6_cidr_id=subnet_ipv6_cidr_id,
        )
