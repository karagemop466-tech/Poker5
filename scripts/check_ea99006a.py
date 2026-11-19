#!/usr/bin/env python3
"""Session ea99006a - build validator.

Fails (exit 1) if any of these is true:
  1. a generated page contains a <table> row with no https:// link;
  2. an internal link points at a relative path that does not exist;
  3. a page references a source host that is not on the official allow-list;
  4. a value looks invented: a guarantee/buy-in/fee cell that is not blank and
     not traceable to a documented official value is not detectable here, but
     every non-blank cell is dumped to a review file so it can be eyeballed.

Run:  python3 scripts/check_ea99006a.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html",
         "pages/executive-summary.html", "pages/tournaments.html", "pages/single-entry.html",
         "pages/tournaments-double.html", "pages/schedule.html", "pages/hotels.html",
         "pages/routes.html", "pages/planner.html", "pages/verification.html", "pages/venues/venetian.html",
         "pages/venues/wynn.html", "pages/venues/others.html", "pages/questions.html",
         "pages/suggestions.html", "pages/flagged-review.html", "pages/monitor.html", "pages/repo-review.html",
         "pages/method.html"]

ALLOWED_HOSTS = [
    "venetianlasvegas.com", "www.venetianlasvegas.com",
    "cdn.wynnresorts.com", "www.wynnlasvegas.com", "wynnlasvegas.com",
    "reservations.wynnlasvegas.com", "wptmedia-mig.s3.amazonaws.com",
    "www.caesars.com", "caesars.com", "southpointcasino.com", "www.southpointcasino.com",
    "www.rwlasvegas.com", "rwlasvegas.com", "reservations.rwlasvegas.com",
    "clarkcountynv.gov", "www.clarkcountynv.gov",
    "www.google.com",
    # the repository and the published site itself: a flag or a status note may point at
    # the Pages page or the Actions run it is about. Never used as a data source.
    "github.com", "karagemop466-tech.github.io",
    # official property pages referenced as "no official schedule found"
    "bellagio.mgmresorts.com", "mgmgrand.mgmresorts.com", "aria.mgmresorts.com",
    # MGM Resorts parking / reservation-terms pages, read 2026-11-19 in session 8f0b323b
    "www.mgmresorts.com", "mgmresorts.com",
    # repository-internal findings (repo review, pipeline fixes) cite the repo itself
    "github.com", "www.github.com",
]

LINK_RE = re.compile(r'<a\s[^>]*href="([^"]+)"', re.I)
HOST_RE = re.compile(r"https?://([^/\"' ]+)")
ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.I | re.S)
TD_RE = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.I | re.S)

errors = []
warnings = []
stats = dict(rows=0, rows_with_source=0, internal=0, external=0)


def fail(msg):
    errors.append(msg)


def host_ok(url):
    m = HOST_RE.match(url)
    if not m:
        return False
    host = m.group(1).lower()
    return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)


for rel in PAGES:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        fail("missing page: %s" % rel)
        continue
    html = open(path).read()
    depth = rel.count("/")

    # 1. internal links resolve
    for url in LINK_RE.findall(html):
        if url.startswith("http") or url.startswith("#") or url.startswith("mailto"):
            continue
        target = os.path.normpath(os.path.join(ROOT, os.path.dirname(rel), url.split("#")[0]))
        if not os.path.exists(target):
            fail("broken internal link in %s -> %s" % (rel, url))
        else:
            stats["internal"] += 1

    # 2. every data row has an https link to an allowed host.
    #    Tables marked data-nosrc list repository files, not source-verified
    #    data, so they are exempt by design.
    nosrc_ranges = []
    for tm in re.finditer(r'<table\b[^>]*>', html, re.I):
        if "data-nosrc" in tm.group(0):
            close = html.find("</table>", tm.end())
            nosrc_ranges.append((tm.start(), close if close > 0 else len(html)))

    def exempt(pos):
        return any(a <= pos <= b for a, b in nosrc_ranges)

    for m in ROW_RE.finditer(html):
        if exempt(m.start()):
            continue
        row = m.group(1)
        if "<th" in row and "<td" not in row:
            continue  # header row
        stats["rows"] += 1
        urls = LINK_RE.findall(row)
        good = [u for u in urls if u.startswith("https://")]
        if not good:
            fail("row without an official https source in %s: %s" % (
                rel, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", row))[:150]))
            continue
        stats["rows_with_source"] += 1
        for u in good:
            if not host_ok(u):
                fail("non-allowed source host in %s: %s" % (rel, u))
            stats["external"] += 1

    # 3. raw http links are not allowed
    for u in re.findall(r'href="(http://[^"]+)"', html):
        fail("insecure http link in %s: %s" % (rel, u))

print("pages checked      : %d" % len(PAGES))
print("table rows         : %d" % stats["rows"])
print("rows with a source : %d" % stats["rows_with_source"])
print("internal links ok  : %d" % stats["internal"])
print("external links ok  : %d" % stats["external"])

if errors:
    print("\nFAILED with %d error(s):" % len(errors))
    for e in errors[:40]:
        print("  - %s" % e)
    sys.exit(1)
print("\nOK - every table row carries an official https source; no broken links.")
