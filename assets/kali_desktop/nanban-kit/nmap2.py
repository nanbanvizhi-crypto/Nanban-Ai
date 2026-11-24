#!/usr/bin/env python3
"""
nmap2 — a modern, visual Nmap 2.0 experience with AI analysis (Nanban Kali Kit).

Runs a real Nmap scan, then shows a visual network topology, a clean host/service
table, a scan summary, and an AI insight that flags outdated services and likely
CVEs — plus a professional HTML/Markdown report.

  nmap2 127.0.0.1
  nmap2 192.168.1.0/24                 # topology of a whole subnet
  nmap2 scanme.nmap.org --fast
  nmap2 10.0.0.5 --ports 1-1000 --no-ai
  nmap2 192.168.1.10 --args "-sV -O -A"   # pass your own nmap flags

Only scan hosts and networks you are authorized to test.
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K

OS_ICON = {"windows": "🪟", "linux": "🐧", "mac": "", "router": "📡", "printer": "🖨️",
           "camera": "📷", "phone": "📱", "embedded": "🔌"}


def guess_role(host) -> tuple[str, str]:
    """Return (icon, label) from OS + open services."""
    osname = (host.get("os") or "").lower()
    svcs = " ".join(s["name"] for s in host["services"]).lower()
    ports = {s["port"] for s in host["services"]}
    if "windows" in osname:
        return OS_ICON["windows"], "Windows"
    if any(p in ports for p in (3306, 5432, 1433, 27017)):
        return "🗄️", "Database"
    if any(p in ports for p in (80, 443, 8080, 8443)) and "http" in svcs:
        return "🌐", "Web Server"
    if 631 in ports or "ipp" in svcs or "printer" in svcs:
        return OS_ICON["printer"], "Printer"
    if 554 in ports or "rtsp" in svcs:
        return OS_ICON["camera"], "IP Camera"
    if "linux" in osname:
        return OS_ICON["linux"], "Linux"
    if 22 in ports:
        return OS_ICON["linux"], "Linux/SSH"
    return "🖥️", (host.get("os") or "Host")


def parse_nmap_xml(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    hosts = []
    for h in root.findall("host"):
        state = h.find("status")
        if state is not None and state.get("state") != "up":
            continue
        addr = ""
        for a in h.findall("address"):
            if a.get("addrtype") in ("ipv4", "ipv6"):
                addr = a.get("addr")
        hostname = ""
        hn = h.find("hostnames/hostname")
        if hn is not None:
            hostname = hn.get("name", "")
        osname = ""
        osmatch = h.find("os/osmatch")
        if osmatch is not None:
            osname = osmatch.get("name", "")
        services = []
        for port in h.findall("ports/port"):
            st = port.find("state")
            if st is None or st.get("state") != "open":
                continue
            svc = port.find("service")
            services.append({
                "port": int(port.get("portid")),
                "proto": port.get("protocol"),
                "name": (svc.get("name") if svc is not None else "") or "?",
                "product": (svc.get("product") if svc is not None else "") or "",
                "version": (svc.get("version") if svc is not None else "") or "",
            })
        services.sort(key=lambda s: s["port"])
        hosts.append({"ip": addr, "hostname": hostname, "os": osname, "services": services})
    run_el = root
    summary = root.find("runstats/finished")
    return {
        "hosts": hosts,
        "args": root.get("args", ""),
        "elapsed": summary.get("elapsed") if summary is not None else "",
        "total_services": sum(len(h["services"]) for h in hosts),
    }


def draw_topology(scan: dict):
    hosts = scan["hosts"]
    if not hosts:
        return
    K.title("Visual Network Topology")
    gw = K.cyn("( • • • )  gateway / network")
    print(f"        {gw}")
    print(f"             {K.dim('│')}")
    n = len(hosts)
    for idx, h in enumerate(hosts):
        icon, role = guess_role(h)
        last = idx == n - 1
        branch = "└──" if last else "├──"
        ports = ", ".join(str(s["port"]) for s in h["services"][:8]) or "no open ports"
        label = f"{icon}  {K.bold(h['ip'])}"
        if h["hostname"]:
            label += f" ({h['hostname']})"
        print(f"      {K.dim(branch)} {label}   {K.dim('['+role+']')}")
        pad = "         " if last else "    │    "
        print(f"      {K.dim(pad)}{K.grn('ports:')} {ports}")
    print()


def service_table(scan: dict):
    K.title("Hosts & Services")
    for h in scan["hosts"]:
        icon, role = guess_role(h)
        hdr = f"{icon} {K.bold(h['ip'])}"
        if h["hostname"]:
            hdr += f"  {K.dim(h['hostname'])}"
        if h["os"]:
            hdr += f"  {K.dim('· ' + h['os'])}"
        print(f"\n  {hdr}  {K.dim('['+role+']')}")
        if not h["services"]:
            print(K.dim("     (no open ports found)"))
            continue
        print(K.dim(f"     {'PORT':<11}{'SERVICE':<16}{'VERSION'}"))
        for s in h["services"]:
            ver = (s["product"] + " " + s["version"]).strip() or "-"
            portcol = f"{s['port']}/{s['proto']}"
            print(f"     {K.grn(portcol)}{' ' * max(1, 11 - len(portcol))}{s['name']:<16}{ver}")


def scan_summary(scan: dict):
    hosts = scan["hosts"]
    risks = find_risks(scan)
    K.title("Scan Summary")
    print(f"  {K.grn('Hosts discovered:')} {len(hosts)}")
    print(f"  {K.grn('Open ports:')}       {scan['total_services']}")
    print(f"  {K.grn('Services found:')}   {len({s['name'] for h in hosts for s in h['services']})}")
    risk_col = K.red if risks else K.grn
    print(f"  {risk_col('Potential risks:')}  {len(risks)}")
    if scan["elapsed"]:
        print(f"  {K.dim('Scan time:')}       {scan['elapsed']}s")


# Cleartext/risky services and a few historically-backdoored versions. Real version→CVE
# judgement is left to the AI insight, so we don't false-flag current software.
CLEARTEXT = {"telnet": 23, "ftp": 21, "rlogin": 513, "rsh": 514, "tftp": 69, "vnc": 5900}
KNOWN_BAD = [
    ("vsftpd 2.3.4", "known backdoor (CVE-2011-2523)"),
    ("proftpd 1.3.3c", "backdoored release (CVE-2010-3867)"),
    ("unrealircd 3.2.8.1", "backdoored release (CVE-2010-2075)"),
    ("distccd", "remote command execution by design (CVE-2004-2687)"),
    ("openssl 1.0.1", "Heartbleed-era OpenSSL — verify patch level (CVE-2014-0160)"),
]


def find_risks(scan: dict) -> list[str]:
    risks = []
    for h in scan["hosts"]:
        for s in h["services"]:
            prod = (s["product"] + " " + s["version"]).strip().lower()
            name = s["name"].lower()
            if name in CLEARTEXT or s["port"] in CLEARTEXT.values():
                risks.append(f"{h['ip']}:{s['port']} cleartext/legacy service ({s['name']}) — traffic is unencrypted")
            for bad, note in KNOWN_BAD:
                if bad in prod:
                    risks.append(f"{h['ip']}:{s['port']} {s['product']} {s['version']} — {note}")
    return risks


def ai_insight(scan: dict, use_ai: bool) -> str:
    if not use_ai:
        return ""
    lines = []
    for h in scan["hosts"]:
        for s in h["services"]:
            lines.append(f"{h['ip']}:{s['port']}/{s['proto']} {s['name']} "
                         f"{s['product']} {s['version']}".rstrip())
    if not lines:
        return ""
    K.step("AI analysing services for outdated software and likely CVEs…")
    prompt = ("Here is an nmap service/version scan result:\n" + "\n".join(lines) +
              "\n\nAs a security analyst, for each notably outdated or risky service, name the likely "
              "CVE(s) or weakness and a one-line remediation. Then give the single highest-priority "
              "finding. Keep it tight. If a version is current, say it looks current. "
              "Do NOT give exploit steps — analysis and patching guidance only.")
    txt = K.ai(prompt) or ""
    K.ai_box(txt, "AI Insight — outdated services & CVEs")
    return txt


def build_report(scan, case, ai_text):
    sections = []
    topo = []
    for h in scan["hosts"]:
        icon, role = guess_role(h)
        topo.append(f"{h['ip']} ({h['hostname'] or 'no name'}) [{role}] os={h['os'] or '?'}")
        for s in h["services"]:
            topo.append(f"    {s['port']}/{s['proto']}  {s['name']}  "
                        f"{(s['product']+' '+s['version']).strip()}")
    sections.append(("Hosts & Services", "\n".join(topo)))
    risks = find_risks(scan)
    sections.append(("Potential Risks", "\n".join(f"- {r}" for r in risks) or "None detected by heuristics."))
    meta = {"Nmap args": scan["args"], "Hosts up": len(scan["hosts"]),
            "Open ports": scan["total_services"], "Scan time": f"{scan['elapsed']}s"}
    K.write_report(case, "nmap2", "Nmap 2.0 Scan Report", sections, ai_summary=ai_text, meta=meta)


def run_scan(target, nmap_args, case, use_ai):
    if not K.which("nmap"):
        K.bad("nmap not installed", "sudo apt install -y nmap")
        return 1
    case = K.ensure_case(case)
    xml_path = case / "nmap" / f"{K.classify(target) if False else re_slug(target)}.xml"
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["nmap"] + nmap_args + ["-oX", str(xml_path), target]
    K.title(f"Nmap 2.0 — scanning {target}", " ".join(nmap_args))
    K.info("$ " + " ".join(cmd))
    rc, out = K.run(cmd, timeout=1800, on_line=lambda l: print("   " + K.dim(l)) if l.strip() else None)
    if not xml_path.is_file():
        K.bad("scan produced no XML", out[-400:])
        return 1
    try:
        scan = parse_nmap_xml(xml_path.read_text("utf-8", "replace"))
    except ET.ParseError as e:
        K.bad("could not parse nmap XML", str(e))
        return 1
    if not scan["hosts"]:
        K.warn("No hosts are up", "nothing responded to the scan")
        return 0
    draw_topology(scan)
    service_table(scan)
    scan_summary(scan)
    risks = find_risks(scan)
    if risks:
        K.title("Potential Risks")
        for r in risks:
            print(f"  {K.red('⚠')}  {r}")
    ai_text = ai_insight(scan, use_ai)
    K.step("Writing report…")
    build_report(scan, case, ai_text)
    K.evidence_log(case, "nmap", target, xml_path, f"{len(scan['hosts'])} hosts")
    print()
    return 0


def re_slug(s):
    import re
    return re.sub(r"[^A-Za-z0-9]+", "-", s)[:40].strip("-") or "scan"


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    target, case, use_ai = None, K.CASE_DEFAULT, True
    ports, fast, extra = None, False, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--case" and i + 1 < len(argv):
            case = argv[i + 1]; i += 2; continue
        if a in ("--no-ai", "--noai"):
            use_ai = False; i += 1; continue
        if a == "--fast":
            fast = True; i += 1; continue
        if a == "--ports" and i + 1 < len(argv):
            ports = argv[i + 1]; i += 2; continue
        if a == "--args" and i + 1 < len(argv):
            extra = argv[i + 1]; i += 2; continue
        target = a; i += 1
    if not target:
        K.bad("no target", "nmap2 <host|cidr>")
        return 2
    if extra:
        import shlex
        nmap_args = shlex.split(extra)
    else:
        nmap_args = ["-sV", "--version-light"]
        if fast:
            nmap_args += ["-T4", "-F"]
        else:
            nmap_args += ["-T4"]
        if ports:
            nmap_args += ["-p", ports]
    K.banner("nmap2", "Visual Nmap with AI analysis")
    return run_scan(target, nmap_args, case, use_ai)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print()
        sys.exit(130)
