# Build log — you drive, Claude reviews

This is your build. Each module ships with a docstring saying what to build
and a hint, but no implementation. Work the milestones in order. When a
milestone passes its check, show me your code and I review before you move on.

The point: in an interview you must explain every line. So every line is yours.

---

## Milestone 0 — environment (done once)

```bash
cd /home/nextpage/projects/hac
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Check: `python -c "import httpx, dns.resolver; print('ok')"` prints `ok`.

---

## Milestone 1 — `asm/ports.py`  (start here)

Pure asyncio, no external services, easy to test. Implement `TOP_100`,
`parse_ports`, `_check_port`, `scan_ports`.

Check parsing (no network):
```bash
python -c "from asm.ports import parse_ports; print(parse_ports('80,443,1-3'))"
# expect: [1, 2, 3, 80, 443]
```

Check scanning against your own machine — open a listener first:
```bash
python -m http.server 8000 &   # target you control
python -c "import asyncio; from asm.ports import scan_ports; \
print(asyncio.run(scan_ports('127.0.0.1', [8000, 8001], 50, 2.0)))"
# expect: [8000]
kill %1
```

---

## Milestone 2 — `asm/subdomains.py`

Implement `from_crtsh` first (passive, safe). Test against a domain you own
or a well-known one you are allowed to query passively.

Check:
```bash
python -c "import asyncio; from asm.subdomains import from_crtsh; \
print(len(asyncio.run(from_crtsh('example.com', 10.0))))"
# expect: a number >= 1
```

Then `from_bruteforce` and `enumerate_subdomains`. Only brute-force domains
you are authorized to test.

---

## Milestone 3 — `asm/hosts.py`

Implement `resolve_host`, `_extract_title`, `probe_http`, `resolve_and_probe`.

Check title parsing offline:
```bash
python -c "from asm.hosts import _extract_title; \
print(_extract_title('<html><title> Hello  World </title>'))"
# expect: Hello World
```

---

## Milestone 4 — `asm/report.py`

Implement the three writers. Build a `ScanResult` by hand in a Python shell,
call `write_all`, open the files, confirm they look right.

---

## Milestone 5 — `asm/cli.py`

Wire it all together. Then the real run, against a domain you are allowed to
test:
```bash
python -m asm example.com --out ./out/example.com
```

Check: `out/example.com/report.json` and `report.md` exist and make sense.

---

## After it works

- Write a short "Authorized use" note at the top of the README (already there — read it).
- Add `tests/` with pytest for `parse_ports` and `_extract_title` (pure functions, easy wins).
- First git commit. Then pick the next feature from the README roadmap.

## Rules for us

- You write code. I review, explain, point to bugs. I do not fill TODOs for you.
- Stuck for real? Ask a specific question ("why does my semaphore deadlock?"),
  not "do milestone 2."
- Paste errors exact.
