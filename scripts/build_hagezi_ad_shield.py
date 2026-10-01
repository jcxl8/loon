#!/usr/bin/env python3
"""Build a Loon plugin from HaGeZi plus the anti-AD remote domain set."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Plugin" / "Hagezi_AdShield.lpx"

SOURCES = {
    "domains": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/share/ad-shield.txt",
    "subdomains": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/share/ad-shield-subdomains.txt",
    "adblock": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/share/ad-shield-adblock.txt",
}

ANTI_AD_DOMAIN_SET = "https://anti-ad.net/surge2.txt"

HOST_LABEL = re.compile(r"^[a-z0-9-]{1,63}$")


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "jcxl8-loon-hagezi-builder/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def normalize_host(value: str) -> str | None:
    host = value.strip().lower().rstrip(".")
    if host.startswith("*."):
        host = host[2:]
    labels = host.split(".")
    if len(labels) < 2 or any(not HOST_LABEL.fullmatch(label) for label in labels):
        return None
    return host


def parse_domains(text: str) -> set[str]:
    domains: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        host = normalize_host(line)
        if host:
            domains.add(host)
    return domains


def parse_adblock(text: str) -> set[str]:
    domains: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("||") or line.startswith("@@"):
            continue
        host = re.split(r"[\^/$|*]", line[2:], maxsplit=1)[0]
        host = normalize_host(host)
        if host:
            domains.add(host)
    return domains


def build() -> tuple[int, dict[str, int]]:
    parsed = {
        "domains": parse_domains(fetch(SOURCES["domains"])),
        "subdomains": parse_domains(fetch(SOURCES["subdomains"])),
        "adblock": parse_adblock(fetch(SOURCES["adblock"])),
    }
    if any(not entries for entries in parsed.values()):
        raise RuntimeError(f"One or more HaGeZi sources returned no usable domains: {parsed}")

    domains = set().union(*parsed.values())
    lines = [
        "#!name=HaGeZi Ad Shield（远程更新）",
        "#!desc=自动同步 HaGeZi Ad-Shield，并远程引用 anti-AD 中文广告域名集",
        "#!author=jcxl8 / HaGeZi / anti-AD",
        "#!homepage=https://github.com/hagezi/dns-blocklists",
        "#!tag=广告拦截,Ad-Shield,anti-AD,远程更新",
        "",
        "[Rule]",
        "# Yahoo News 页面兼容：仅放行该精确 HTML 加载域名，不放行整个 html-load.com 或 yahoo.com",
        "DOMAIN,0.yahoo-homepage.html-load.com,DIRECT",
        "# HaGeZi ad-shield.txt, ad-shield-subdomains.txt and ad-shield-adblock.txt",
        "# anti-AD 中文广告域名集（云端维护）",
        f"DOMAIN-SET,{ANTI_AD_DOMAIN_SET},REJECT",
        *[f"DOMAIN-SUFFIX,{domain},REJECT" for domain in sorted(domains)],
        "",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    return len(domains), {name: len(entries) for name, entries in parsed.items()}


if __name__ == "__main__":
    total, counts = build()
    print(f"Generated {OUTPUT} with {total} unique Loon rules: {counts}")
