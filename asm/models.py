"""Result graph data model.

Kept as plain dataclasses so the whole thing serializes to JSON with
`dataclasses.asdict` and stays easy to diff between runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HttpProbe:
    """One HTTP(S) probe result against a host."""

    url: str
    status: int | None = None
    title: str | None = None
    server: str | None = None
    error: str | None = None


@dataclass
class Host:
    """A resolved subdomain and everything learned about it."""

    name: str
    addresses: list[str] = field(default_factory=list)
    http: list[HttpProbe] = field(default_factory=list)
    open_ports: list[int] = field(default_factory=list)

    @property
    def alive(self) -> bool:
        return any(p.status is not None for p in self.http)


@dataclass
class ScanResult:
    """Top-level result for one target domain."""

    domain: str
    started_at: str
    finished_at: str | None = None
    subdomains_found: int = 0
    hosts: list[Host] = field(default_factory=list)
