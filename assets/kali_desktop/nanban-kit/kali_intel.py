#!/usr/bin/env python3
"""
kali-intel — Unified OSINT & Threat Intelligence hub (Nanban Kali Kit).

Give it one indicator (domain, IP, file hash or email) and it gathers context
from many sources, correlates it, scores the risk and writes a report — with an
AI summary from the same engine the Nanban app uses.

  kali-intel example.com
  kali-intel 104.21.56.123
  kali-intel 44d88612fea8a8f36de82e1278abb02f        # a file hash
  kali-intel someone@example.com --no-ai
  kali-intel example.com --case ~/cases/acme

Sources with NO API key (always on): DNS, WHOIS, reverse DNS, TLS cert names
(crt.sh), abuse.ch ThreatFox & URLhaus, HTTP banner.
Sources that use a key when you have one (keys in ~/.nanban-kit/keys.json or env):
  shodan, virustotal, abuseipdb, greynoise, otx (AlienVault), hibp (HaveIBeenPwned).

Set keys once:   kali-intel --set-key virustotal YOUR_KEY
Use only on targets you are authorized to investigate.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K

KEYS_PATH = K.KIT_HOME / "keys.json"
KEY_ENV = {"shodan": "SHODAN_API_KEY", "virustotal": "VT_API_KEY", "abuseipdb": "ABUSEIPDB_KEY",
           "greynoise": "GREYNOISE_KEY", "otx": "OTX_KEY", "hibp": "HIBP_KEY"}


def get_key(name: str) -> str:
    env = os.environ.get(KEY_ENV.get(name, ""), "")
    if env:
        return env
    return (K.load_json(KEYS_PATH, {}) or {}).get(name, "")


def set_key(name: str, value: str):
    keys = K.load_json(KEYS_PATH, {}) or {}
    keys[name] = value
    K.save_json(KEYS_PATH, keys)
    K.ok(f"saved key for {name}", "stored in ~/.nanban-kit/keys.json (chmod 600)")


# ───────────────────────────────────────────── collectors (each returns facts + indicators)

class Intel:
    def __init__(self, target: str, kind: str):
        self.target = target
        self.kind = kind
        self.facts: dict[str, str] = {}
        self.indicators: list[tuple[str, str, str]] = []   # (type, value, reputation)
        self.sections: list[tuple[str, str]] = []
        self.risk = 0
        self.risk_reasons: list[str] = []

    def add(self, head: str, body: str):
        if body and body.strip():
            self.sections.append((head, body.strip()))

    def bump(self, amount: int, reason: str):
        self.risk = min(100, self.risk + amount)
        self.risk_reasons.append(reason)


def c_dns(it: Intel):
    if it.kind not in ("domain", "ip"):
        return
    host = it.target if it.kind == "ip" else it.target
    if it.kind == "domain":
        if not (K.which("dig") or K.which("host")):
            K.warn("DNS", "dig/host not installed — skipping (sudo apt install dnsutils)")
            return
        recs = {}
        for rtype in ("A", "AAAA", "MX", "NS", "TXT"):
            if K.which("dig"):
                rc, out = K.run(["dig", "+short", rtype, host], timeout=20)
            else:
                rc, out = K.run(["host", "-t", rtype, host], timeout=20)
            vals = [l for l in out.splitlines() if l.strip() and "__missing__" not in l]
            if vals:
                recs[rtype] = vals
        if recs:
            body = "\n".join(f"{r}:\n  " + "\n  ".join(v) for r, v in recs.items())
            it.add("DNS records", body)
            if recs.get("A"):
                it.facts["Resolved IP"] = recs["A"][0]
            K.ok("DNS", f"{sum(len(v) for v in recs.values())} records")
    else:  # reverse DNS for an IP
        rc, out = K.run(["dig", "+short", "-x", host], timeout=15) if K.which("dig") else (1, "")
        ptr = [l for l in out.splitlines() if l.strip()]
        if ptr:
            it.facts["Reverse DNS"] = ptr[0]
            it.add("Reverse DNS", "\n".join(ptr))


def c_whois(it: Intel):
    if it.kind not in ("domain", "ip") or not K.which("whois"):
        if it.kind in ("domain", "ip") and not K.which("whois"):
            K.warn("WHOIS", "whois not installed (sudo apt install whois)")
        return
    rc, out = K.run(["whois", it.target], timeout=30)
    if rc == 0 and out.strip():
        keep = [l for l in out.splitlines()
                if any(k in l.lower() for k in ("registrar", "creation", "created", "expir",
                        "updated", "org", "name server", "nserver", "country", "netname",
                        "cidr", "origin", "descr")) and ":" in l]
        body = "\n".join(keep[:40]) or out[:1500]
        it.add("WHOIS", body)
        for l in keep:
            low = l.lower()
            if "registrar:" in low:
                it.facts["Registrar"] = l.split(":", 1)[1].strip()
            if low.strip().startswith(("creation date", "created")):
                it.facts["Created"] = l.split(":", 1)[1].strip()
            if "country:" in low and "Country" not in it.facts:
                it.facts["Country"] = l.split(":", 1)[1].strip()
        K.ok("WHOIS", it.facts.get("Registrar", "retrieved"))


def c_crtsh(it: Intel):
    if it.kind != "domain":
        return
    okk, data = K.http_json(f"https://crt.sh/?q=%25.{urllib.parse.quote(it.target)}&output=json", timeout=30)
    if not okk or not isinstance(data, list):
        return
    subs = sorted({row.get("name_value", "") for row in data})
    subs = sorted({s for entry in subs for s in entry.split("\n") if s and "*" not in s})
    if subs:
        it.add(f"Subdomains / TLS cert names ({len(subs)} unique, via crt.sh)", "\n".join(subs[:120]))
        it.facts["Subdomains found"] = str(len(subs))
        K.ok("crt.sh", f"{len(subs)} cert names")


def c_http(it: Intel):
    if it.kind != "domain":
        return
    okk, body = K.http_text(f"https://{it.target}", timeout=15)
    if not okk:
        okk, body = K.http_text(f"http://{it.target}", timeout=15)
    if okk:
        import re
        tm = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
        if tm:
            it.facts["Page title"] = re.sub(r"\s+", " ", tm.group(1)).strip()[:120]
            K.ok("HTTP", it.facts["Page title"])


def c_threatfox(it: Intel):
    """abuse.ch ThreatFox — malware IOC database, no key."""
    if it.kind not in ("domain", "ip", "hash"):
        return
    q = {"query": "search_ioc", "search_term": it.target}
    okk, data = K.http_json("https://threatfox-api.abuse.ch/api/v1/",
                            headers={"Content-Type": "application/json"},
                            data=json.dumps(q).encode(), timeout=25)
    if okk and isinstance(data, dict) and data.get("query_status") == "ok":
        rows = data.get("data") or []
        lines = []
        for r in rows[:25]:
            lines.append(f"{r.get('ioc')}  malware={r.get('malware_printable')}  "
                         f"threat={r.get('threat_type')}  conf={r.get('confidence_level')}")
            it.indicators.append((r.get("ioc_type", "ioc"), r.get("ioc", ""), "malicious"))
        if lines:
            it.add("ThreatFox (abuse.ch) matches", "\n".join(lines))
            it.bump(45, f"Listed in ThreatFox ({len(rows)} IOC record(s))")
            K.bad("ThreatFox", f"{len(rows)} malicious IOC match(es)")
    elif okk:
        K.ok("ThreatFox", "no match (clean)")


def c_urlhaus(it: Intel):
    """abuse.ch URLhaus — malicious URL/host database, no key."""
    if it.kind == "domain":
        data_field, url = ("host", "https://urlhaus-api.abuse.ch/v1/host/")
        payload = f"host={urllib.parse.quote(it.target)}"
    elif it.kind == "ip":
        data_field, url = ("host", "https://urlhaus-api.abuse.ch/v1/host/")
        payload = f"host={it.target}"
    elif it.kind == "hash":
        data_field, url = ("hash", "https://urlhaus-api.abuse.ch/v1/payload/")
        h = it.target.lower()
        payload = (f"sha256_hash={h}" if len(h) == 64 else f"md5_hash={h}")
    else:
        return
    okk, data = K.http_json(url, headers={"Content-Type": "application/x-www-form-urlencoded"},
                            data=payload.encode(), timeout=25)
    if okk and isinstance(data, dict) and data.get("query_status") == "ok":
        urls = data.get("urls") or ([data] if data.get("url") else [])
        if urls:
            lines = [f"{u.get('url', u.get('urlhaus_reference', ''))}  status={u.get('url_status')}  "
                     f"threat={u.get('threat')}" for u in urls[:20]]
            it.add("URLhaus (abuse.ch) malicious URLs", "\n".join(lines))
            it.bump(40, f"Listed in URLhaus ({len(urls)} URL(s))")
            K.bad("URLhaus", f"{len(urls)} malicious URL(s)")
    elif okk:
        K.ok("URLhaus", "no match")


def c_shodan(it: Intel):
    key = get_key("shodan")
    if it.kind != "ip" or not key:
        return
    okk, data = K.http_json(f"https://api.shodan.io/shodan/host/{it.target}?key={key}", timeout=25)
    if okk and isinstance(data, dict):
        ports = data.get("ports", [])
        it.facts["Shodan org"] = data.get("org", "?")
        it.facts["Open ports (Shodan)"] = ", ".join(map(str, ports))
        lines = [f"org: {data.get('org')}", f"os: {data.get('os')}",
                 f"country: {data.get('country_name')}", f"ports: {ports}"]
        for svc in (data.get("data") or [])[:12]:
            lines.append(f"  :{svc.get('port')}/{svc.get('transport')}  "
                         f"{svc.get('product', '')} {svc.get('version', '')}".rstrip())
        it.add("Shodan host", "\n".join(lines))
        K.ok("Shodan", f"{len(ports)} open ports")
    elif not okk:
        K.warn("Shodan", data)


def c_virustotal(it: Intel):
    key = get_key("virustotal")
    if not key:
        return
    path = {"ip": f"ip_addresses/{it.target}", "domain": f"domains/{it.target}",
            "hash": f"files/{it.target}"}.get(it.kind)
    if not path:
        return
    okk, data = K.http_json(f"https://www.virustotal.com/api/v3/{path}",
                            headers={"x-apikey": key}, timeout=25)
    if okk and isinstance(data, dict):
        attr = (data.get("data") or {}).get("attributes", {})
        stats = attr.get("last_analysis_stats", {})
        mal, susp = stats.get("malicious", 0), stats.get("suspicious", 0)
        total = sum(stats.values()) or 1
        it.facts["VirusTotal"] = f"{mal} malicious / {susp} suspicious of {total} engines"
        body = [f"detections: {mal} malicious, {susp} suspicious, {total} engines"]
        if attr.get("meaningful_name"):
            body.append(f"name: {attr['meaningful_name']}")
        if attr.get("type_description"):
            body.append(f"type: {attr['type_description']}")
        it.add("VirusTotal", "\n".join(body))
        if mal + susp > 0:
            it.bump(min(50, (mal + susp) * 5), f"VirusTotal: {mal} engines flag malicious")
            K.bad("VirusTotal", f"{mal} malicious / {total}")
        else:
            K.ok("VirusTotal", f"0 / {total}")
    elif not okk:
        K.warn("VirusTotal", data)


def c_abuseipdb(it: Intel):
    key = get_key("abuseipdb")
    if it.kind != "ip" or not key:
        return
    okk, data = K.http_json(
        f"https://api.abuseipdb.com/api/v2/check?ipAddress={it.target}&maxAgeInDays=90",
        headers={"Key": key, "Accept": "application/json"}, timeout=25)
    if okk and isinstance(data, dict):
        d = data.get("data", {})
        score = d.get("abuseConfidenceScore", 0)
        it.facts["AbuseIPDB score"] = f"{score}/100 ({d.get('totalReports', 0)} reports)"
        it.add("AbuseIPDB", f"confidence: {score}/100\nreports: {d.get('totalReports')}\n"
                            f"ISP: {d.get('isp')}\nusage: {d.get('usageType')}\n"
                            f"country: {d.get('countryCode')}")
        if score >= 25:
            it.bump(min(40, score // 2), f"AbuseIPDB confidence {score}/100")
            K.bad("AbuseIPDB", f"{score}/100")
        else:
            K.ok("AbuseIPDB", f"{score}/100")


def c_greynoise(it: Intel):
    key = get_key("greynoise")
    if it.kind != "ip" or not key:
        return
    okk, data = K.http_json(f"https://api.greynoise.io/v3/community/{it.target}",
                            headers={"key": key}, timeout=20)
    if okk and isinstance(data, dict):
        it.facts["GreyNoise"] = f"{data.get('classification', '?')} ({data.get('name', '')})"
        it.add("GreyNoise", json.dumps(data, indent=2)[:800])
        if data.get("classification") == "malicious":
            it.bump(30, "GreyNoise classifies as malicious")


def c_otx(it: Intel):
    key = get_key("otx")
    if not key:
        return
    seg = {"ip": f"IPv4/{it.target}", "domain": f"domain/{it.target}",
           "hash": f"file/{it.target}"}.get(it.kind)
    if not seg:
        return
    okk, data = K.http_json(f"https://otx.alienvault.com/api/v1/indicators/{seg}/general",
                            headers={"X-OTX-API-KEY": key}, timeout=25)
    if okk and isinstance(data, dict):
        pulses = (data.get("pulse_info") or {}).get("count", 0)
        it.facts["AlienVault OTX pulses"] = str(pulses)
        names = [p.get("name") for p in (data.get("pulse_info") or {}).get("pulses", [])[:10]]
        it.add("AlienVault OTX", f"pulses: {pulses}\n" + "\n".join(f"- {n}" for n in names if n))
        if pulses:
            it.bump(min(25, pulses * 3), f"Appears in {pulses} OTX threat pulse(s)")


def c_hibp(it: Intel):
    key = get_key("hibp")
    if it.kind != "email" or not key:
        if it.kind == "email" and not key:
            K.info("HIBP needs a key: kali-intel --set-key hibp YOUR_KEY (haveibeenpwned.com/API/Key)")
        return
    okk, data = K.http_json(
        f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(it.target)}?truncateResponse=false",
        headers={"hibp-api-key": key, "User-Agent": K.UA}, timeout=25)
    if okk and isinstance(data, list):
        names = [f"{b.get('Name')} ({b.get('BreachDate')})" for b in data]
        it.add("Have I Been Pwned — breaches", "\n".join(names))
        it.facts["Breaches"] = str(len(names))
        it.bump(min(40, len(names) * 8), f"Email in {len(names)} known breach(es)")
        K.bad("HIBP", f"{len(names)} breaches")
    elif not okk and "404" in str(data):
        K.ok("HIBP", "no breaches found")


def c_local_iocs(it: Intel):
    """Correlate against onion IOCs already collected by dark-osint, if present."""
    for p in (Path(os.path.expanduser("~/dark-osint/case")), it_case[0]):
        iocs = p / "onion_iocs.txt" if p else None
        if iocs and iocs.is_file() and it.target in iocs.read_text("utf-8", "ignore"):
            it.add("Local correlation", f"Target appears in your dark-osint IOC file: {iocs}")
            it.bump(15, "Seen in your own collected dark-web IOCs")


it_case = [None]
COLLECTORS = [c_dns, c_whois, c_crtsh, c_http, c_threatfox, c_urlhaus,
              c_shodan, c_virustotal, c_abuseipdb, c_greynoise, c_otx, c_hibp, c_local_iocs]


def risk_band(score: int) -> str:
    if score >= 70:
        return K.red(f"{score}/100  HIGH")
    if score >= 35:
        return K.ylw(f"{score}/100  MEDIUM")
    return K.grn(f"{score}/100  LOW")


def investigate(target: str, case, use_ai=True):
    kind = K.classify(target)
    if kind == "unknown":
        K.bad("Could not classify target", f"'{target}' is not a domain, IP, hash or email")
        return 2
    case = K.ensure_case(case)
    it_case[0] = case
    K.title(f"OSINT / Threat Intel — {target}", f"type: {kind}")
    it = Intel(target, kind)
    it.facts["Target"] = target
    it.facts["Type"] = kind

    for col in COLLECTORS:
        try:
            col(it)
        except KeyboardInterrupt:
            K.warn("interrupted"); break
        except Exception as e:
            K.warn(col.__name__, f"{type(e).__name__}: {e}")

    # ---- target overview
    K.title("Target Overview")
    for k, v in it.facts.items():
        print(f"  {K.dim(k + ':'):<28} {v}")
    print(f"  {K.dim('Risk score:'):<28} {risk_band(it.risk)}")
    if it.risk_reasons:
        print(f"  {K.dim('Why:')}")
        for r in it.risk_reasons:
            print(f"    • {r}")

    # ---- AI summary
    ai_summary = ""
    if use_ai:
        K.step("Asking AI to correlate and summarize…")
        facts_text = "\n".join(f"{k}: {v}" for k, v in it.facts.items())
        sec_text = "\n\n".join(f"[{h}]\n{b}" for h, b in it.sections)
        prompt = (f"Indicator under investigation: {target} (type: {kind}).\n"
                  f"Computed risk score: {it.risk}/100. Reasons: {'; '.join(it.risk_reasons) or 'none'}.\n\n"
                  f"Collected facts:\n{facts_text}\n\nRaw source findings:\n{sec_text}\n\n"
                  "Write a short threat-intel summary for an analyst: (1) what this indicator appears to be, "
                  "(2) key risks or red flags, (3) 3-5 concrete next investigation steps. "
                  "Be factual; if evidence is thin, say so.")
        ai_summary = K.ai(prompt, context="") or ""
        K.ai_box(ai_summary, "AI Threat Summary")

    # ---- report
    K.step("Writing report…")
    it.facts["Risk score"] = f"{it.risk}/100"
    meta = dict(it.facts)
    K.write_report(case, f"intel_{K.classify(target)}_{re_slug(target)}",
                   f"OSINT / Threat Intelligence — {target}",
                   it.sections, ai_summary=ai_summary, meta=meta)
    K.evidence_log(case, "osint", target, note=f"risk={it.risk}")
    print()
    return 0


def re_slug(s: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9]+", "-", s)[:40].strip("-")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--set-key":
        if len(argv) < 3:
            K.bad("usage", "kali-intel --set-key <service> <key>")
            return 2
        set_key(argv[1].lower(), argv[2])
        return 0
    if argv[0] == "--keys":
        have = K.load_json(KEYS_PATH, {}) or {}
        for s in KEY_ENV:
            print(f"  {s:<12} {'set' if (have.get(s) or os.environ.get(KEY_ENV[s])) else '—'}")
        return 0
    case, use_ai, target = K.CASE_DEFAULT, True, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--case" and i + 1 < len(argv):
            case = argv[i + 1]; i += 2; continue
        if a in ("--no-ai", "--noai"):
            use_ai = False; i += 1; continue
        target = a; i += 1
    if not target:
        K.bad("no target", "give a domain, IP, hash or email")
        return 2
    K.banner("kali-intel", "Unified OSINT & Threat Intelligence")
    return investigate(target, case, use_ai)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print()
        sys.exit(130)
