"""Safe URL validation for server-side HTTP fetches (SSRF mitigation)."""

from __future__ import annotations

import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

from app.core.config import settings

# Hostnames that must never be fetched, even if they resolve to a public IP.
_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "metadata",
        "metadata.google.internal",
    }
)

# Suffixes that indicate local or internal targets.
_BLOCKED_HOST_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
)


class URLValidationError(ValueError):
    """Raised when a URL is not safe to fetch server-side."""


_IpAddress = ipaddress.IPv4Address | ipaddress.IPv6Address


def _allowed_schemes() -> frozenset[str]:
    if settings.ENVIRONMENT == "production":
        return frozenset({"https"})
    return frozenset({"https", "http"})


def _hostname_blocked(hostname: str) -> bool:
    host = hostname.lower().rstrip(".")
    if host in _BLOCKED_HOSTNAMES:
        return True
    return any(host.endswith(suffix) for suffix in _BLOCKED_HOST_SUFFIXES)


def _ip_blocked(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or (isinstance(addr, ipaddress.IPv4Address) and addr in _METADATA_NET)
    )


def _resolve_host_ips(hostname: str) -> list[_IpAddress]:
    """Resolve *hostname* and return parsed IP addresses."""
    try:
        infos = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise URLValidationError(f"Cannot resolve hostname: {hostname}") from exc

    ips: list[_IpAddress] = []
    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        ip_str = sockaddr[0]
        try:
            ips.append(ipaddress.ip_address(ip_str))
        except ValueError:
            continue

    if not ips:
        raise URLValidationError(f"Cannot resolve hostname: {hostname}")

    return ips


def validate_fetch_url(url: str) -> None:
    """Validate *url* is safe to fetch. Raises :class:`URLValidationError` if not."""
    parsed = urlparse(url)
    if parsed.scheme not in _allowed_schemes():
        allowed = " or ".join(sorted(_allowed_schemes()))
        raise URLValidationError(f"URL scheme must be one of: {allowed}.")

    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("URL must include a hostname.")

    if _hostname_blocked(hostname):
        raise URLValidationError("URL hostname is not allowed.")

    # Literal IP in the URL — check before DNS.
    try:
        literal_ip: _IpAddress = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if _ip_blocked(literal_ip):
            raise URLValidationError("URL points to a private or reserved address.")
        return

    for addr in _resolve_host_ips(hostname):
        if _ip_blocked(addr):
            raise URLValidationError("URL resolves to a private or reserved address.")


async def ensure_fetch_url_safe(url: str) -> None:
    """Async wrapper that runs DNS resolution off the event loop."""
    await asyncio.to_thread(validate_fetch_url, url)


_METADATA_NET = ipaddress.ip_network("169.254.0.0/16")
