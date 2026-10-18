"""JSON and Markdown report writers.

YOUR JOB: implement after the scan pipeline works end to end.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict

from asm.models import ScanResult


def write_json(result: ScanResult, out_dir: str) -> str:
    """Write report.json and return its path.

    TODO: implement. Hint: dataclasses.asdict(result) is already JSON-safe;
    json.dump with indent=2.
    """
    path = os.path.join(out_dir, "report.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(result),f, indent=2)
    
    return path


def write_markdown(result: ScanResult, out_dir: str) -> str:
    """Write a readable report.md and return its path.

    TODO: implement. Suggested: a summary header (counts), then one section
    per resolved host with its addresses, open ports, and a small table of
    live HTTP probes (url | status | server | title).
    """
    path = os.path.join(out_dir, "report.md")
    resolved = [host for host in result.hosts if host.addresses]
    alive = [host for host in result.hosts if host.alive]

    # Summary header
    lines = [
        f"# Attack Surface Report — {result.domain}",
        "",
        f"- Subdomains found: {result.subdomains_found}",
        f"- Resolved hosts: {len(resolved)}",
        f"- Alive hosts: {len(alive)}",
        "",
        "## Hosts",
        "",
    ]

    # Per-host sections
    for host in sorted(resolved, key=lambda h:h.name):
        lines.append(f"### {host.name}")
        lines.append(f"- Addresses: {', '.join(host.addresses) or '-'}")
        if host.open_ports:
            lines.append(f"- Open ports: {', '.join(str(p) for p in sorted(host.open_ports))}")
        live = [p for p in host.http if p.status is not None]
        if live:
            lines.append("")
            lines.append("| URL | Status | Server | Title |")
            lines.append("|-----|--------|--------|-------|")
            for probe in live:
                lines.append(
                    f"| {probe.url} | {probe.status} | "
                    f"{probe.server or '-'} | {probe.title or '-'} |"
                )
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path


def write_all(result: ScanResult, out_dir: str) -> tuple[str, str]:
    """Create out_dir and write both reports.

    TODO: os.makedirs(out_dir, exist_ok=True), then call the two writers.
    """
    os.makedirs(out_dir, exist_ok=True)
    return write_json(result, out_dir), write_markdown(result, out_dir)
