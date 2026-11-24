#!/usr/bin/env python3
"""
kali-forensics — AI-assisted digital forensics lab (Nanban Kali Kit).

Triage a suspicious file or image: identify it, hash it (chain of custody),
pull metadata, extract readable strings and indicators (URLs, IPs, .onion,
emails), carve embedded files, run YARA, inspect PDFs, and — when a memory
image and Volatility 3 are present — list suspicious processes. An AI assistant
explains the artifacts and suggests next steps.

  kali-forensics sample.bin                 # full AI triage + report
  kali-forensics info  sample.exe
  kali-forensics strings sample.bin
  kali-forensics meta  photo.jpg
  kali-forensics carve firmware.bin
  kali-forensics yara  sample.bin [rules.yar]
  kali-forensics pdf   invoice.pdf
  kali-forensics mem   memory.raw            # needs volatility3 (vol)
  kali-forensics --case ~/cases/x sample.bin

Analyse untrusted samples ONLY inside this VM/sandbox, never on your main PC.
Use for authorized investigations and learning.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitlib as K

IOC_PATTERNS = {
    "url": re.compile(r"https?://[^\s\"'<>]{4,}"),
    "onion": re.compile(r"[a-z2-7]{56}\.onion"),
    "ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "domain": re.compile(r"\b(?:[a-zA-Z0-9-]{1,63}\.)+(?:com|net|org|io|ru|cn|info|biz|xyz|top|onion)\b"),
}


def need_file(path: str) -> Path | None:
    p = Path(os.path.expanduser(path))
    if not p.is_file():
        K.bad("file not found", path)
        return None
    return p


def t_info(p: Path, it):
    K.title("File Identification", p.name)
    rc, ftype = K.run(["file", "-b", str(p)], timeout=20)
    size = p.stat().st_size
    md5 = hashlib.md5(p.read_bytes()).hexdigest() if size < 200 * 1024 * 1024 else "(skipped, >200MB)"
    sha = K.sha256_file(p)
    print(f"  {K.dim('Name:'):<16} {p.name}")
    print(f"  {K.dim('Size:'):<16} {size:,} bytes")
    print(f"  {K.dim('Type:'):<16} {ftype.strip()}")
    print(f"  {K.dim('MD5:'):<16} {md5}")
    print(f"  {K.dim('SHA-256:'):<16} {K.grn(sha)}")
    it["facts"].update({"Name": p.name, "Size": f"{size:,} bytes",
                        "Type": ftype.strip(), "MD5": md5, "SHA-256": sha})
    it["sections"].append(("File identification",
                           f"name: {p.name}\nsize: {size}\ntype: {ftype.strip()}\nmd5: {md5}\nsha256: {sha}"))
    return ftype.strip()


def t_strings(p: Path, it, quiet=False):
    rc, out = K.run(["strings", "-n", "6", str(p)], timeout=120)
    if "__missing__" in out:
        K.warn("strings", "binutils not installed")
        return
    found = {k: sorted(set(rx.findall(out)))[:60] for k, rx in IOC_PATTERNS.items()}
    found = {k: v for k, v in found.items() if v}
    if not quiet:
        K.title("Extracted Indicators (from strings)")
    total = 0
    body = []
    for k, vals in found.items():
        total += len(vals)
        if not quiet:
            print(f"\n  {K.grn(k.upper())} ({len(vals)})")
            for v in vals[:25]:
                print(f"    {v}")
        body.append(f"[{k}] ({len(vals)})\n" + "\n".join(vals))
        for v in vals:
            it["indicators"].append((k, v))
    if total == 0 and not quiet:
        K.info("no URLs/IPs/onion/email indicators found in strings")
    it["sections"].append(("Indicators from strings", "\n\n".join(body) or "none"))
    it["facts"]["Indicators"] = str(total)


def t_meta(p: Path, it):
    if not K.which("exiftool"):
        K.warn("exiftool", "not installed (sudo apt install libimage-exiftool-perl)")
        return
    K.title("Metadata (exiftool)")
    rc, out = K.run(["exiftool", str(p)], timeout=60)
    keep = [l for l in out.splitlines() if ":" in l]
    for l in keep[:40]:
        print("  " + l)
    it["sections"].append(("Metadata (exiftool)", "\n".join(keep)))
    for l in keep:
        low = l.lower()
        if low.startswith(("author", "creator", "producer", "create date", "software")):
            k, _, v = l.partition(":")
            it["facts"][k.strip()] = v.strip()


def t_carve(p: Path, it, case: Path):
    K.title("Embedded File Carving")
    if K.which("binwalk"):
        rc, out = K.run(["binwalk", str(p)], timeout=120)
        print("\n".join("  " + l for l in out.splitlines()[:40]))
        it["sections"].append(("binwalk signatures", out[:4000]))
        extract_dir = case / "carved" / p.stem
        extract_dir.mkdir(parents=True, exist_ok=True)
        K.info(f"to extract: binwalk -e {p} -C {extract_dir}")
    else:
        K.warn("binwalk", "not installed (sudo apt install binwalk) — skipping carve")


def t_yara(p: Path, it, rules: str | None):
    if not K.which("yara"):
        K.warn("yara", "not installed (sudo apt install yara) — skipping")
        return
    rule_file = rules or _default_yara()
    if not rule_file or not Path(rule_file).is_file():
        K.info("no YARA rules given and none found; pass: kali-forensics yara <file> rules.yar")
        return
    K.title("YARA scan", Path(rule_file).name)
    rc, out = K.run(["yara", "-s", rule_file, str(p)], timeout=120)
    if out.strip():
        print("\n".join("  " + K.red(l) for l in out.splitlines()[:30]))
        it["sections"].append(("YARA matches", out[:3000]))
        it["facts"]["YARA"] = "MATCHED"
    else:
        K.ok("YARA", "no rule matched")


def _default_yara() -> str | None:
    for cand in ("/usr/share/yara/rules/index.yar",
                 os.path.expanduser("~/.nanban-kit/rules.yar")):
        if Path(cand).is_file():
            return cand
    return None


def t_pdf(p: Path, it):
    K.title("PDF structure")
    did = False
    for tool, args in (("pdfid", [str(p)]), ("pdf-parser", ["-a", str(p)])):
        if K.which(tool):
            rc, out = K.run([tool] + args, timeout=60)
            print("\n".join("  " + l for l in out.splitlines()[:30]))
            it["sections"].append((f"PDF ({tool})", out[:3000]))
            did = True
            risky = [k for k in ("/JS", "/JavaScript", "/OpenAction", "/Launch", "/EmbeddedFile", "/AA")
                     if k in out]
            if risky:
                K.warn("PDF active content", ", ".join(risky))
                it["facts"]["PDF risk"] = ", ".join(risky)
            break
    if not did:
        K.warn("pdfid/pdf-parser", "not installed (sudo apt install pdfid python3-pdfminer)")


def t_mem(p: Path, it):
    vol = "vol" if K.which("vol") else ("vol.py" if K.which("vol.py") else "volatility3" if K.which("volatility3") else None)
    if not vol:
        K.warn("volatility3", "not installed — memory analysis skipped (pipx install volatility3)")
        return
    K.title("Memory analysis (Volatility 3)", "windows.pslist / malfind")
    for plugin in ("windows.info", "windows.pslist", "windows.malfind"):
        K.step(plugin)
        rc, out = K.run([vol, "-f", str(p), plugin], timeout=600,
                        on_line=lambda l: print("   " + K.dim(l)) if l.strip() else None)
        it["sections"].append((f"Volatility {plugin}", out[:4000]))


def ai_explain(it, use_ai: bool):
    if not use_ai:
        return ""
    K.step("AI explaining the forensic artifacts…")
    facts = "\n".join(f"{k}: {v}" for k, v in it["facts"].items())
    secs = "\n\n".join(f"[{h}]\n{b[:1500]}" for h, b in it["sections"])
    prompt = (f"Forensic triage of a file.\nFacts:\n{facts}\n\nArtifacts:\n{secs}\n\n"
              "As a DFIR analyst: (1) what is this file and is anything suspicious? "
              "(2) explain the notable artifacts in plain language, (3) give 3-5 concrete next steps "
              "(e.g. dump, sandbox detonation, pivot on an IOC). "
              "Analysis and defensive guidance only — no malware authoring.")
    txt = K.ai(prompt) or ""
    K.ai_box(txt, "AI Forensic Assistant")
    return txt


def full_triage(p: Path, case: Path, use_ai: bool, rules=None):
    it = {"facts": {}, "indicators": [], "sections": []}
    K.evidence_log(case, "acquire", p.name, p, "forensic triage start")
    ftype = t_info(p, it)
    low = ftype.lower()
    t_strings(p, it)
    if any(x in low for x in ("image", "exif", "jpeg", "png", "tiff", "document", "pdf", "office")):
        t_meta(p, it)
    if "pdf" in low:
        t_pdf(p, it)
    if any(x in low for x in ("executable", "firmware", "data", "archive", "boot")):
        t_carve(p, it, case)
    t_yara(p, it, rules)
    ai_text = ai_explain(it, use_ai)
    K.step("Writing DFIR report…")
    meta = dict(it["facts"]); meta["Indicators"] = str(len(it["indicators"]))
    K.write_report(case, "forensics_" + re_slug(p.name),
                   f"Digital Forensics Triage — {p.name}", it["sections"],
                   ai_summary=ai_text, meta=meta)
    print()
    return 0


def re_slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s)[:40].strip("-") or "file"


SUB = {"info", "strings", "meta", "carve", "yara", "pdf", "mem", "hash"}


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    case, use_ai = K.CASE_DEFAULT, True
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--case" and i + 1 < len(argv):
            case = argv[i + 1]; i += 2; continue
        if a in ("--no-ai", "--noai"):
            use_ai = False; i += 1; continue
        rest.append(a); i += 1
    case = K.ensure_case(case)
    K.banner("kali-forensics", "AI-assisted digital forensics")

    if rest and rest[0] in SUB:
        sub = rest[0]
        p = need_file(rest[1]) if len(rest) > 1 else None
        if not p:
            K.bad("usage", f"kali-forensics {sub} <file>")
            return 2
        it = {"facts": {}, "indicators": [], "sections": []}
        if sub == "info":   t_info(p, it)
        elif sub == "hash": print(f"  MD5    {hashlib.md5(p.read_bytes()).hexdigest()}\n  SHA256 {K.sha256_file(p)}")
        elif sub == "strings": t_strings(p, it)
        elif sub == "meta": t_meta(p, it)
        elif sub == "carve": t_carve(p, it, case)
        elif sub == "yara": t_yara(p, it, rest[2] if len(rest) > 2 else None)
        elif sub == "pdf":  t_pdf(p, it)
        elif sub == "mem":  t_mem(p, it)
        K.evidence_log(case, sub, p.name, p)
        print()
        return 0

    p = need_file(rest[0]) if rest else None
    if not p:
        K.bad("no file", "kali-forensics <file>")
        return 2
    return full_triage(p, case, use_ai)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print()
        sys.exit(130)
