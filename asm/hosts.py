"""DNS resolution and HTTP(S) liveness probing.

YOUR JOB: implement after subdomains.py.
"""

from __future__ import annotations

import asyncio
import re

import httpx
import dns.asyncresolver
import dns.resolver

from asm.models import Host, HttpProbe


_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


async def resolve_host(name: str, timeout: float) -> Host:
    """Resolve A records for `name` into a Host.

    A Host with an empty `addresses` list is valid — it just did not resolve.

    TODO: implement.
      Hint: dns.asyncresolver.Resolver(), set .lifetime = timeout,
      resolve(name, "A"), collect {r.address for r in answer} sorted.
      Catch the dns exceptions and return a Host with no addresses.
    """
    host = Host(name=name, addresses=[])
    resolver = dns.asyncresolver.Resolver()
    dns.resolver.Resolver.lifetime = timeout
    try:
      answer = await resolver.resolve(name, "A")
      host.addresses = sorted({r.address for r in answer})
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.resolver.NoNameservers):
      pass
    return host


def _extract_title(body: str) -> str | None:
    """Return the <title> text from an HTML body, collapsed and trimmed.

    TODO: implement using _TITLE_RE. Collapse whitespace with " ".join(
    match.group(1).split()), cap length (~200). Return None if no match.
    """
    match = _TITLE_RE.search(body)
    if match:
      raw = match.group(1)
      cleaned = " ".join(raw.split())
      return cleaned[:200] or None
    else:
      return None


async def probe_http(client: httpx.AsyncClient, host: Host, timeout: float) -> None:
    """Probe https:// then http:// for `host`, appending an HttpProbe each.

    TODO: implement.
      For each scheme build url, GET it, record status / Server header /
      title (only when content-type is HTML). On httpx.HTTPError store the
      exception class name in probe.error. Append each probe to host.http.
    """
    for scheme in ["https", "http"]:
        url = f"{scheme}://{host.name}"
        probe = HttpProbe(url=url)
        try:
          resp = await client.get(url, timeout=timeout)
          probe.status = resp.status_code
          probe.server = resp.headers.get("Server")
          if "html" in resp.headers.get("Content-Type", "").lower():
              probe.title = _extract_title(resp.text)
        except httpx.HTTPError as e:
          probe.error = type(e).__name__
        host.http.append(probe)


async def resolve_and_probe(
    names: list[str], concurrency: int, timeout: float
) -> list[Host]:
    """Resolve every name, then HTTP-probe the ones that resolved.

    TODO: implement.
      Steps: gather resolve_host over names. Keep hosts with addresses as
      probe candidates. Open one httpx.AsyncClient(follow_redirects=True,
      verify=False) and probe candidates under a Semaphore. Return ALL
      resolved hosts (probed or not).
    """
    resolved = await asyncio.gather(*[resolve_host(name, timeout) for name in names])
    candidates = [host for host in resolved if host.addresses]

    semaphore = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
      async def worker(host):
        async with semaphore:
          await probe_http(client, host, timeout)
      
      await asyncio.gather(*(worker(host) for host in candidates))
    return resolved
