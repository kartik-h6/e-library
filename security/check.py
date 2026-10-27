#!/usr/bin/env python3
"""Security & release checks for the TechStudyHubCore Pharmacy monorepo.

Run from the repository root:   python3 security/check.py

Exit code 0 = all checks passed, 1 = at least one failed.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok))
    line = f"  {'PASS' if ok else 'FAIL'}  {name}"
    if detail and not ok:
        line += f"   [{detail}]"
    print(line)


SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "uploads", "docs"}

SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"sk-[A-Za-z0-9]{20,}", "API key"),
    (r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "hardcoded credential"),
]
# Values that are documented demo/placeholder material, not secrets.
ALLOW = re.compile(
    r"(change-this|dev-secret|placeholder|example|your[-_]|xxx|test|demo|"
    r"placeholder|test|demo|example)", re.I)

TEXT_EXT = {".py", ".js", ".html", ".css", ".json", ".md", ".yml", ".yaml",
            ".txt", ".cfg", ".ini", ".sh", ".env"}


def iter_text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(base) / f
            if p.suffix.lower() in TEXT_EXT or f == ".env.example":
                yield p


def scan_secrets():
    hits = []
    for p in iter_text_files():
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat, label in SECRET_PATTERNS:
            for m in re.finditer(pat, text):
                if ALLOW.search(m.group(0)):
                    continue
                hits.append(f"{p.relative_to(ROOT)} → {label}")
    check("no secrets in tracked files", not hits, "; ".join(hits[:4]))


def check_ignores():
    root_gi = (ROOT / ".gitignore").read_text(encoding="utf-8") if (ROOT / ".gitignore").exists() else ""
    be_gi = (ROOT / "backend" / ".gitignore").read_text(encoding="utf-8") if (ROOT / "backend" / ".gitignore").exists() else ""
    check(".env is ignored", ".env" in root_gi and ".env" in be_gi)
    check("*.db is ignored", "*.db" in root_gi and "*.db" in be_gi)
    check("uploads/ is ignored", "uploads/" in be_gi)


def check_no_client_side_auth():
    hits = []
    for p in (ROOT / "frontend").rglob("*"):
        if p.is_file() and p.suffix in {".html", ".js"}:
            t = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"(?i)(password|passwd)\s*[:=]\s*['\"][^'\"]+['\"]", t):
                hits.append(str(p.relative_to(ROOT)))
    check("frontend ships no credentials", not hits, ", ".join(hits[:3]))


def check_catalogue():
    try:
        import jsonschema
    except ImportError:
        check("catalogue validates against schema", False, "jsonschema not installed")
        return
    try:
        cat = json.loads((ROOT / "frontend" / "data" / "catalogue.json").read_text(encoding="utf-8"))
        sch = json.loads((ROOT / "frontend" / "data" / "schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(cat, sch)
        check("catalogue validates against schema", True)
        n = sum(len(s["subjects"]) for s in cat["semesters"])
        check("catalogue is 8 semesters / 88 subjects",
              len(cat["semesters"]) == 8 and n == 88, f"{len(cat['semesters'])} sem / {n} subj")
    except Exception as e:
        check("catalogue validates against schema", False, str(e)[:90])


def check_backend_tests():
    try:
        r = subprocess.run([sys.executable, "test_smoke.py"], cwd=ROOT / "backend",
                           capture_output=True, text=True, timeout=240)
        tail = (r.stdout or r.stderr).strip().splitlines()
        check("backend smoke tests pass", r.returncode == 0 and "0 failed" in r.stdout,
              tail[-1] if tail else "no output")
    except Exception as e:
        check("backend smoke tests pass", False, str(e)[:90])


def main():
    print("Security & release checks — TechStudyHubCore Pharmacy\n")
    scan_secrets()
    check_ignores()
    check_no_client_side_auth()
    check_catalogue()
    check_backend_tests()
    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
    for n in failed:
        print("  -", n)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
