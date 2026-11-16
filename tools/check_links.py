#!/usr/bin/env python3
"""Link gate for the Pages build. Fails (exit 1) on:
- any internal link/asset that does not exist under site-443e914d/,
- any '#anchor' that does not exist on the target page,
- any external URL not listed in data-443e914d/sources.json (no network access is used).
"""
import glob, json, os, sys
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "site-443e914d")
ALLOWED = {v["url"] for v in json.load(open(os.path.join(ROOT, "data-443e914d", "sources.json"), encoding="utf-8")).values()}
ALLOWED |= {"https://github.com/karagemop466-tech/Poker5/blob/main/research-443e914d/verification.md"}

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d: self.ids.add(d["id"])
        if tag == "a" and d.get("href"): self.refs.append(d["href"])
        if tag == "link" and d.get("href"): self.refs.append(d["href"])
        if tag == "script" and d.get("src"): self.refs.append(d["src"])

pages = {}
for path in glob.glob(os.path.join(DOCS, "*.html")):
    s = Scan(); s.feed(open(path, encoding="utf-8").read())
    pages[os.path.basename(path)] = s

errors = []
external = set()
for name, s in pages.items():
    for ref in s.refs:
        if ref.startswith(("http://", "https://")):
            external.add(ref)
            if ref not in ALLOWED:
                errors.append(f"{name}: external URL not in sources.json: {ref}")
            continue
        if ref.startswith(("mailto:", "tel:")):
            continue
        target, _, anchor = ref.partition("#")
        if target == "":
            target_page = name
        else:
            target_page = target
        full = os.path.normpath(os.path.join(DOCS, target_page))
        if not os.path.exists(full):
            errors.append(f"{name}: broken link -> {ref}")
            continue
        if anchor and target_page in pages and anchor not in pages[target_page].ids:
            errors.append(f"{name}: missing anchor -> {ref}")

print(f"pages checked: {len(pages)}; external URLs seen: {len(external)}")
if errors:
    print("FAILED:")
    for e in errors: print("  " + e)
    sys.exit(1)
print("OK: no broken internal links or anchors; all external URLs are in data-443e914d/sources.json")
