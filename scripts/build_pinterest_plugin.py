#!/usr/bin/env python3
"""Build the Pinterest Loon plugin from local rules and HaGeZi adblock lists."""

from __future__ import annotations

from pathlib import Path

from build_hagezi_ad_shield import fetch, parse_adblock


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Plugin" / "Pinterest_remove_ads_Loon.lpx"

HAGEZI_SOURCES = {
    "multi": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/adblock/multi.txt",
    "pro-plus": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/adblock/pro.plus.txt",
    "ultimate": "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/adblock/ultimate.txt",
}

STATIC_RULES = {
    ("DOMAIN-SUFFIX", "bugsnag.com"),
    ("DOMAIN-SUFFIX", "snapkit.com"),
    ("DOMAIN-SUFFIX", "appsflyersdk.com"),
    ("DOMAIN-SUFFIX", "doubleclick.net"),
    ("DOMAIN-SUFFIX", "doubleclick-cn.net"),
    ("DOMAIN-SUFFIX", "google-analytics.com"),
    ("DOMAIN-SUFFIX", "app-measurement.com"),
    ("DOMAIN-SUFFIX", "adjust.com"),
    ("DOMAIN", "d.agkn.com"),
    ("DOMAIN-SUFFIX", "bidr.io"),
    ("DOMAIN-SUFFIX", "sc.omtrdc.net"),
    ("DOMAIN-SUFFIX", "demdex.net"),
    ("DOMAIN-SUFFIX", "bouncex.net"),
    ("DOMAIN-SUFFIX", "zenimpact.io"),
    ("DOMAIN", "cookiesync.mparticle.com"),
    ("DOMAIN-SUFFIX", "ads-dev.pinterest.com"),
    ("DOMAIN-SUFFIX", "ads.pinterest.com"),
    ("DOMAIN-SUFFIX", "analytics-dev.pinterest.com"),
    ("DOMAIN-SUFFIX", "analytics.pinterest.com"),
    ("DOMAIN-SUFFIX", "ct.pinterest.com"),
    ("DOMAIN-SUFFIX", "log.pinterest.com"),
    ("DOMAIN-SUFFIX", "log.pinterest.com.eg"),
    ("DOMAIN-SUFFIX", "trk.pinterest.com"),
    ("DOMAIN-SUFFIX", "trk2.pinterest.com"),
}

PINTEREST_AD_HOSTS = {
    "ads-dev.pinterest.com",
    "ads.pinterest.com",
    "analytics-dev.pinterest.com",
    "analytics.pinterest.com",
    "ct.pinterest.com",
    "log.pinterest.com",
    "log.pinterest.com.eg",
    "trk.pinterest.com",
    "trk2.pinterest.com",
}

SEARCH_ITEM_KEEP = (
    '(.story_type? != "shopping_spotlight") and '
    '(.story_type? != "slp_search_recommendation") and '
    '(.story_type? != "related_searches_organic") and '
    '(.title.format? != "购物焦点") and '
    '(.is_promoted? != true) and '
    '(.is_promoted? != "true") and '
    '(.pin_promotion_id? == null) and '
    '(.promoted_pin_id? == null) and '
    '(.ad_pin_id? == null) and '
    '(.promotion_id? == null)'
)

REWRITE_RULES = [
    r"""^https:\/\/api\.pinterest\.com\/v\d+\/feeds\/home\? response-body-json-jq '.data |= map(select(.is_promoted == false or .is_promoted == "false"))'""",
    r"""^https:\/\/api\.pinterest\.com\/v\d+\/pins\/\d+\/related\/modules\? response-body-json-jq '.data |= map(select(.is_promoted == false or .is_promoted == "false"))'""",
    rf"""^https:\/\/api\.pinterest\.com\/v\d+\/search\/ response-body-json-jq 'if (.resource_response.data.results? | type) == "array" then .resource_response.data.results |= map(select({SEARCH_ITEM_KEEP})) elif (.resource_response.data? | type) == "array" then .resource_response.data |= map(select({SEARCH_ITEM_KEEP})) elif (.data.results? | type) == "array" then .data.results |= map(select({SEARCH_ITEM_KEEP})) elif (.data? | type) == "array" then .data |= map(select({SEARCH_ITEM_KEEP})) else . end'""",
    r"""^https:\/\/api\.pinterest\.com\/v\d+\/batch\/ response-body-json-jq 'walk(if type == "object" and ((.is_promoted? == true) or (.is_promoted? == "true") or (.pin_promotion_id? != null) or (.promoted_pin_id? != null) or (.ad_pin_id? != null) or (.promotion_id? != null) or (.is_sponsored? == true) or (.is_sponsored? == "true")) then empty else . end)'""",
]


def pinterest_hosts() -> set[str]:
    hosts: set[str] = set()
    for url in HAGEZI_SOURCES.values():
        for host in parse_adblock(fetch(url)):
            # Keep ad/tracking endpoints, never core or regional Pinterest sites.
            if (
                host == "pinterest.com"
                or host.startswith("pinterest.")
                or (host.endswith(".pinterest.com") and host not in PINTEREST_AD_HOSTS)
            ):
                continue
            if "pinterest" in host or "pinimg" in host:
                hosts.add(host)
    if not hosts:
        raise RuntimeError("HaGeZi sources returned no Pinterest-specific rules")
    return hosts


def build() -> int:
    rules = set(STATIC_RULES)
    rules.update(("DOMAIN-SUFFIX", host) for host in pinterest_hosts())
    lines = [
        "#!name=Pinterest 去广告（增强版·远程更新）",
        "#!desc=移除首页、相关 Pin 和搜索结果中的推广 Pin，并同步 HaGeZi 的 Pinterest 广告与跟踪域名",
        "#!author=jcxl8 / HaGeZi / Codex",
        "#!homepage=https://github.com/jcxl8/loon",
        "#!tag=Pinterest,去广告,远程更新",
        "",
        "[Rule]",
        "# Static privacy and advertising endpoints",
        "# Core/regional Pinterest sites such as ar.pinterest.com are intentionally not blocked.",
        *[f"{kind},{host},REJECT" for kind, host in sorted(rules)],
        "",
        "[Rewrite]",
        *REWRITE_RULES,
        "",
        "[MITM]",
        "hostname = %APPEND% api.pinterest.com",
        "",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    return len(rules)


if __name__ == "__main__":
    print(f"Generated {OUTPUT} with {build()} network rules")
