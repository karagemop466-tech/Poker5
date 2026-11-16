#!/usr/bin/env python3
"""Check the built site in docs/.

1. Every internal href / src resolves to a file in docs/.
2. Every data row in the single-entry, multi-entry, and flagged tables links to at least one official source.
3. Table row counts match data.py.

    python3 scripts/check_bafafd7c.py          # exit 0 = pass, 1 = fail
Standard library only. External URLs are listed but not fetched (run in CI or by hand).
"""
import html.parser
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "dashboard-bafafd7c")
sys.path.insert(0, HERE)
import data_bafafd7c as D  # noqa: E402


class Collector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.tables, self._stack, self._row = [], {}, [], None
        self._cur_table = None
        self._row_links = None

    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        if tag in ("a", "link", "script", "img") and ("href" in at or "src" in at):
            self.links.append(at.get("href") or at.get("src"))
            if tag == "a" and self._row_links is not None:
                self._row_links.append(at.get("href", ""))
        if tag == "table":
            self._cur_table = at.get("id")
            self.tables[self._cur_table] = {"rows": [], "links": []}
        if tag == "tr" and self._cur_table and self._cur_table in self.tables:
            self._row_links = []
        if tag == "tr":
            pass

    def handle_endtag(self, tag):
        if tag == "tr" and self._row_links is not None and self._cur_table in self.tables:
            t = self.tables[self._cur_table]
            # skip header rows (those in <thead>) — header rows have no <a>; body rows get counted
            if self._in_body:
                t["rows"].append(self._row_links)
            self._row_links = None
        if tag == "table":
            self._cur_table = None


def check_html():
    failures = []
    external = set()
    counts = {}
    for name in sorted(os.listdir(DOCS)):
        if not name.endswith(".html"):
            continue
        with open(os.path.join(DOCS, name), encoding="utf-8") as f:
            text = f.read()
        p = Collector()
        p._in_body = False
        # track <tbody> with a simple regex pass for body rows
        for m in re.finditer(r'href="([^"]+)"|src="([^"]+)"', text):
            link = m.group(1) or m.group(2)
            if link.startswith("http://") or link.startswith("https://"):
                external.add(link)
                continue
            if link.startswith("#") or link.startswith("mailto:") or link.startswith("tel:"):
                continue
            target = os.path.normpath(os.path.join(DOCS, link.split("#")[0]))
            if not os.path.exists(target):
                failures.append(f"{name}: broken internal link -> {link}")
        # data-row source check: each <tbody> row in tables with ids single/multi/unv/wpt/hotels/src
        for tid in ("single", "multi", "unv", "hotels"):
            m = re.search(rf'<table id="{tid}"[^>]*>(.*?)</table>', text, re.S)
            if not m:
                continue
            tbody = re.search(r"<tbody>(.*?)</tbody>", m.group(1), re.S).group(1)
            rows = re.findall(r"<tr>(.*?)</tr>", tbody, re.S)
            counts[(name, tid)] = len(rows)
            for i, r in enumerate(rows, 1):
                if tid != "hotels" and "<a " not in r:
                    failures.append(f"{name}#{tid} row {i}: no official source link")
    return failures, external, counts


def main():
    failures, external, counts = check_html()
    expect = {
        ("single-entry.html", "single"): len(D.SINGLE_ENTRY),
        ("multi-entry.html", "multi"): len(D.MULTI_ENTRY),
        ("flagged.html", "unv"): len(D.UNVERIFIED_VENETIAN),
        ("hotels.html", "hotels"): len(D.HOTELS),
    }
    for k, v in expect.items():
        got = counts.get(k)
        if got != v:
            failures.append(f"row count mismatch {k}: page={got} data={v}")
    print(f"pages checked: {len([f for f in os.listdir(DOCS) if f.endswith('.html')])}")
    print(f"external links found (not fetched here): {len(external)}")
    for k, v in sorted(counts.items()):
        print(f"  rows {k[0]} #{k[1]}: {v}")
    if failures:
        print("FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print("PASS: no broken internal links; every data row has a source link; row counts match data.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
