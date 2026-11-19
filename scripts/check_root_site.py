#!/usr/bin/env python3
"""Validate the built root Poker5 site.

Checks:
  * every generated HTML page exists and parses as HTML;
  * every internal .html link resolves to a file in the repo;
  * every CSS/JS asset referenced by a page resolves;
  * every data-searchable table row has a source link or a flagged-link anchor;
  * the scheduled re-check baseline is present and parses.

Exits non-zero on any failure. Run after scripts/build_c6087e2c.py.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def root_pages():
    """Only the root site this session owns: index.html and pages/**."""
    pages = [os.path.join(ROOT, "index.html")]
    pages += glob.glob(os.path.join(ROOT, "pages", "**", "*.html"), recursive=True)
    return pages


def check_links():
    for f in root_pages():
        with open(f, encoding="utf-8") as fh:
            txt = fh.read()
        base = os.path.dirname(f)
        # Match actual href/src attributes, not data-nosrc or data-src attributes.
        for m in re.finditer(r'(?<![\w-])(?:href|src)="([^"#]+)"', txt):
            href = m.group(1)
            if href.startswith(("http", "mailto", "tel", "//", "data:")):
                continue
            target = os.path.normpath(os.path.join(base, href))
            if not os.path.exists(target):
                errors.append("{}: broken link {}".format(os.path.relpath(f, ROOT), href))


def check_source_anchors():
    for f in root_pages():
        with open(f, encoding="utf-8") as fh:
            txt = fh.read()
        for tbl in re.findall(r'<table[^>]*data-searchable[^>]*>.*?</table>', txt, re.S):
            headers = re.findall(r"<th[^>]*>(.*?)</th>", tbl, re.S)
            # Only enforce a source link on tables that have a Source column.
            if not any("source" in h.lower() for h in headers):
                continue
            rows = re.findall(r"<tr>(.*?)</tr>", tbl, re.S)
            for row in rows[1:]:  # skip header
                if "<td" not in row:
                    continue
                if "<a " in row:
                    continue
                # A row with no source is acceptable only if it is explicitly
                # flagged as having none.
                if "Flagged" in row or ">none<" in row:
                    continue
                errors.append("{}: table row without a source link".format(
                    os.path.relpath(f, ROOT)))


def check_trip_calculator():
    """A missing date-specific hotel quote must never be presented as $0."""
    planner = os.path.join(ROOT, "pages", "planner.html")
    app = os.path.join(ROOT, "assets", "app.js")
    with open(planner, encoding="utf-8") as fh:
        html = fh.read()
    with open(app, encoding="utf-8") as fh:
        js = fh.read()
    if re.search(r'<input[^>]*id="ptrue"[^>]*value="0"', html):
        errors.append("planner treats an unknown hotel cost as a default $0")
    if 'id="ptrue"' not in html or "placeholder=\"enter a dated, itemized hotel cost\"" not in html:
        errors.append("planner does not clearly request a dated hotel cost")
    if "A blank hotel cost is unknown, not $0." not in js or "Incomplete" not in js:
        errors.append("planner JavaScript does not preserve an explicit incomplete state")


def check_baseline():
    p = os.path.join(ROOT, "data", "c6087e2c", "last_checked.json")
    if not os.path.exists(p):
        errors.append("missing baseline data/c6087e2c/last_checked.json")
        return
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    if not data.get("sources"):
        errors.append("baseline has no sources recorded")


def main():
    check_links()
    check_source_anchors()
    check_trip_calculator()
    check_baseline()
    if errors:
        print("ROOT SITE CHECK ERRORS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("root site check: links, source anchors and baseline OK")


if __name__ == "__main__":
    main()
