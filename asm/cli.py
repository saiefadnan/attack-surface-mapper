"""Command-line entry point and pipeline orchestration.

YOUR JOB: wire the stages together. This is the last piece — do it once the
individual modules work.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from asm.subdomains import enumerate_subdomains
from asm.hosts import resolve_and_probe
from asm.ports import parse_ports, scan_ports
from asm.report import write_all
from asm.models import ScanResult


# You will import from asm.subdomains, asm.hosts, asm.ports, asm.report,
# and asm.models here as you need them.


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Define and parse CLI arguments.

    TODO: implement with argparse. Required positional: domain.
    Options (see README table): --wordlist, --ports (default "top100"),
    --concurrency (default 30), --timeout (default 5.0), --out,
    --no-ports (store_true).
    """
    p = argparse.ArgumentParser(prog="asm", description="Attack Surface Mapper")
    p.add_argument("domain")
    p.add_argument("--wordlist", default=None)
    p.add_argument("--concurrency", type=int, default=30)
    p.add_argument("--timeout", type=float, default=5.0)
    p.add_argument("--ports", default="top100")
    p.add_argument("--out", default=None)
    p.add_argument("--no-ports", action="store_true")
    return p.parse_args(argv)


async def run(args: argparse.Namespace) -> None:
    """Run the full pipeline for one domain.

    TODO: implement the orchestration:
      1. record started_at (datetime.now(timezone.utc).isoformat())
      2. enumerate_subdomains(...)
      3. resolve_and_probe(sorted names)
      4. unless --no-ports: for each resolved host's first address,
         scan_ports and store on host.open_ports
      5. record finished_at, fill ScanResult, write_all(), print paths
    """
    started = datetime.now(timezone.utc).isoformat()
    subdomains = await enumerate_subdomains(
        args.domain, args.wordlist, args.concurrency, args.timeout
    )
    hosts = await resolve_and_probe(
        sorted(subdomains), args.concurrency, args.timeout
    )
    if not args.no_ports:
        ports = parse_ports(args.ports)
        for host in hosts:
            if host.addresses:
                host.open_ports = await scan_ports(
                    host.addresses[0], ports, args.concurrency, args.timeout
                )
    
    result = ScanResult(
        domain=args.domain,
        started_at=started,
        finished_at=datetime.now(timezone.utc).isoformat(),
        subdomains_found=len(subdomains),
        hosts=hosts,
    )
    out = args.out or f"./out/{args.domain}"
    json_path, md_path = write_all(result, out)
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    asyncio.run(run(args))
