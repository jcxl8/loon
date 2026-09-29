#!/usr/bin/env python3
"""Build a conservative Instagram/Facebook/Meta Loon ad-blocking plugin."""

from __future__ import annotations

from pathlib import Path

from build_hagezi_ad_shield import fetch, parse_adblock


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Plugin" / "Meta_remove_ads_Loon.lpx"

HAGEZI_SOURCES = {
    "pro-plus": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/adblock/pro.plus.txt",
    "ultimate": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/adblock/ultimate.txt",
}

# Deliberately exclude graph.*, connect.*, mqtt.*, web.* and CDN hosts: these are
# core Meta services and blocking them can prevent login, feeds, or media from loading.
STATIC_HOSTS = {
    "ads.facebook.com",
    "an.facebook.com",
    "analytics.facebook.com",
    "badge.facebook.com",
    "badges.instagram.com",
    "pixel.facebook.com",
    "tr.facebook.com",
    "ads.instagramstoryviewer.org",
}

AD_MARKERS = {
    "ad",
    "ads",
    "advert",
    "advertising",
    "analytics",
    "an",
    "badge",
    "badges",
    "beacon",
    "event",
    "events",
    "marketing",
    "measure",
    "metrics",
    "pixel",
    "track",
    "tracking",
    "tracker",
    "tr",
}


REWRITE_FILTER = r'''walk(if type == "object" and ((.is_ad? == true) or (.is_ad? == "true") or (.is_sponsored? == true) or (.is_sponsored? == "true") or (.is_promoted? == true) or (.is_promoted? == "true") or (.ad_id? != null) or (.ad_metadata? != null) or (.sponsor? != null) or (.commerciality_status? == "SPONSORED") or (.commerciality_status? == "sponsored") or (.commerciality_status? == "AD") or (.commerciality_status? == "ad")) then empty else . end)'''

REWRITE_RULES = [
    rf"^https:\/\/i\.instagram\.com\/api\/v\d+\/ response-body-json-jq '{REWRITE_FILTER}'",
    rf"^https:\/\/(www\.)?instagram\.com\/(api\/)?graphql\/ response-body-json-jq '{REWRITE_FILTER}'",
    rf"^https:\/\/(www\.)?facebook\.com\/api\/graphql\/ response-body-json-jq '{REWRITE_FILTER}'",
    rf"^https:\/\/graph\.(instagram|facebook)\.com\/ response-body-json-jq '{REWRITE_FILTER}'",
]


def _brand_label(label: str) -> bool:
    return (
        label in {"instagram", "facebook", "meta"}
        or label.startswith(("instagram-", "facebook-", "meta-"))
        or label.endswith(("-instagram", "-facebook", "-meta"))
    )


def hagezi_meta_hosts() -> set[str]:
    hosts: set[str] = set(STATIC_HOSTS)
    for url in HAGEZI_SOURCES.values():
        for host in parse_adblock(fetch(url)):
            labels = host.split(".")
            if any(_brand_label(label) for label in labels) and any(
                label in AD_MARKERS for label in labels
            ):
                hosts.add(host)
    return hosts


def build() -> int:
    hosts = hagezi_meta_hosts()
    if not hosts:
        raise RuntimeError("HaGeZi sources returned no Meta-related advertising hosts")

    lines = [
        "#!name=Meta（Instagram / Facebook）去广告（远程更新）",
        "#!desc=拦截 Instagram、Facebook、Meta 的广告与跟踪端点，并清理部分信息流响应中的推广内容",
        "#!author=jcxl8 / HaGeZi / Codex",
        "#!homepage=https://github.com/jcxl8/loon",
        "#!tag=Instagram,Facebook,Meta,去广告,远程更新",
        "",
        "[Rule]",
        "# Static Meta endpoints plus conservative matches from HaGeZi pro.plus and ultimate.",
        *[f"DOMAIN-SUFFIX,{host},REJECT" for host in sorted(hosts)],
        "",
        "[Rewrite]",
        "# Remove objects marked as ads/sponsored/promoted from supported JSON responses.",
        *REWRITE_RULES,
        "",
        "[MITM]",
        "hostname = %APPEND% i.instagram.com,www.instagram.com,graph.instagram.com,www.facebook.com,graph.facebook.com",
        "",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    return len(hosts)


if __name__ == "__main__":
    print(f"Generated {OUTPUT} with {build()} Meta-related network rules")
