"""Subdomain enumeration.

Two independent sources, merged:
  - Certificate Transparency logs via crt.sh (passive, no touch to target).
  - DNS brute force against a wordlist (active).

YOUR JOB: implement the functions below after you finish ports.py.
"""

from __future__ import annotations

import asyncio

import httpx
import dns.asyncresolver
import dns.resolver


CRTSH_URL = "https://crt.sh/"


async def from_crtsh(domain: str, timeout: float) -> set[str]:
    """Pull subdomains from crt.sh Certificate Transparency records.

    Request: GET https://crt.sh/?q=%.<domain>&output=json
    The response is a JSON array of objects. Each object has a "name_value"
    field that may hold several newline-separated names, some with a "*."
    wildcard prefix.

    TODO: implement.
      Steps: httpx.AsyncClient GET -> resp.json() -> for each row, split
      name_value on newlines, strip, lstrip("*."), lowercase, keep names
      that endswith(domain) and have no "@". Return a set.
      Wrap network + json parsing in try/except so one failure does not
      kill the whole scan — print a warning and return what you have.
    """
    try:
      url = f"{CRTSH_URL}?q=%.{domain}&output=json"
      async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json();
        subdomains = set();
        for row in data:
          for name in str(row.get("name_value", "")).split('\n'):
            name = name.strip().lstrip('*.').lower()
            if name.endswith(domain) and '@' not in name:
              subdomains.add(name)
          return subdomains
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        print(f"Warning: crt.sh request failed: {e}")
        return set()


async def from_bruteforce(
    domain: str, wordlist: str, concurrency: int, timeout: float
) -> set[str]:
    """Brute force `<word>.<domain>` for each word in the wordlist.

    Keep only names that resolve (have an A record).

    TODO: implement.
      Steps: read wordlist (skip blank lines and "#" comments). Build a
      dns.asyncresolver.Resolver() with .lifetime = timeout. For each word,
      try resolver.resolve(name, "A") under a Semaphore; on success keep the
      name, on dns.resolver.NXDOMAIN / NoAnswer / Timeout drop it.
    """
    try:
      with open(wordlist, encoding='utf-8', errors='ignore') as f:
        words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except OSError as e:
        print(f"Warning: failed to read wordlist {wordlist}: {e}")
        return set()

    resolver = dns.asyncresolver.Resolver()
    resolver.lifetime = timeout
    semaphore = asyncio.Semaphore(concurrency)

    async def worker(word):
      async with semaphore:
        name = f"{word}.{domain}"
        try:
          await resolver.resolve(name, "A")
          return name
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,dns.resolver.NoNameservers ,dns.exception.Timeout):
          return None

    results = await asyncio.gather(*(worker(word) for word in words))
    
    return set(name for name in results if name is not None)


async def enumerate_subdomains(
    domain: str,
    wordlist: str | None,
    concurrency: int,
    timeout: float,
) -> set[str]:
    """Merge every enabled source. Always include the apex `domain` itself.

    TODO: implement — call from_crtsh always, from_bruteforce only when a
    wordlist was given, union the results.
    """
    results = set({domain})
    results.update(await from_crtsh(domain, timeout))
    if wordlist:
        results.update(await from_bruteforce(domain, wordlist, concurrency, timeout))
    return results
