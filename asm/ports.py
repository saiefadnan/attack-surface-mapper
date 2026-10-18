"""Async TCP connect port scanner.

A connect scan completes the full TCP handshake, so it needs no special
privileges but is noisier than a SYN scan. Fine for recon against your own
assets.

YOUR JOB: implement the three things below. Start here — this module is pure
asyncio with no external APIs, so it is the easiest to test.
"""

from __future__ import annotations

import asyncio


# Nmap-style top 100 TCP ports, ordered roughly by real-world frequency.
TOP_100: list[int] = [
    7, 9, 13, 21, 22, 23, 25, 26, 37, 53, 79, 80, 81, 88, 106, 110, 111, 113,
    119, 135, 139, 143, 144, 179, 199, 389, 427, 443, 444, 445, 465, 513, 514,
    515, 543, 544, 548, 554, 587, 631, 646, 873, 990, 993, 995, 1025, 1026,
    1027, 1028, 1029, 1110, 1433, 1720, 1723, 1755, 1900, 2000, 2001, 2049,
    2121, 2717, 3000, 3128, 3306, 3389, 3986, 4899, 5000, 5009, 5051, 5060,
    5101, 5190, 5357, 5432, 5631, 5666, 5800, 5900, 6000, 6001, 6646, 7070,
    8000, 8008, 8009, 8080, 8081, 8443, 8888, 9100, 9999, 10000, 32768, 49152,
    49153, 49154, 49155, 49156, 49157,
]


def parse_ports(spec: str) -> list[int]:


    """Parse a port spec into a sorted list of unique ints.
    Must accept: "top100", a range like "1-1024", a CSV like "80,443,8080",
    and combinations. Drop anything outside 1..65535.


    TODO 2: implement.
      Hint: split on ",", then handle a "-" inside each part.
      Return sorted(set(...)).
    """
    if spec.strip().lower() == "top100":
        return list(TOP_100)

    string_list = spec.split(",")
    int_list = set()
    for x in string_list:
      if '-' in x:
        start, end = x.split("-")
        if start.isdigit() and end.isdigit():
            start, end = int(start), int(end)
            if 1 <= start <= 65535 and 1 <= end <= 65535:
                int_list.update(range(start, end + 1))
      elif x.isdigit():
        port = int(x)
        if 1 <= port <= 65535:
            int_list.add(port)
    return sorted(int_list)


async def _check_port(address: str, port: int, timeout: float) -> int | None:
    """Return `port` if the TCP handshake succeeds within `timeout`, else None.

    TODO 3a: implement.
      Hint: asyncio.open_connection(address, port) returns (reader, writer).
      Wrap it in asyncio.wait_for(..., timeout). Close the writer. Catch
      OSError and asyncio.TimeoutError and return None.
    """
    try:
      reader, writer = await asyncio.wait_for(asyncio.open_connection(address, port),timeout=timeout)
      writer.close()
      return port
    except (OSError, asyncio.TimeoutError):
      return None    


async def scan_ports(
    address: str, ports: list[int], concurrency: int, timeout: float
) -> list[int]:
    """Scan one address across `ports`, returning open ports sorted.

    TODO 3b: implement.
      Hint: bound concurrency with asyncio.Semaphore(concurrency), then
      asyncio.gather a worker per port. Filter out the None results.
    """
    semaphore = asyncio.Semaphore(concurrency)
    async def worker(port):
        async with semaphore:
            return await _check_port(address, port, timeout)
    
    results = await asyncio.gather(*(worker(port) for port in ports))
    return sorted(port for port in results if port is not None)