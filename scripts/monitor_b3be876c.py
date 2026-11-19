#!/usr/bin/env python3
"""Value-level source monitor (session b3be876c).

Why this exists: the published monitor hashed whole pages and flagged 48 of 96 official URLs as
"changed" in a single run, because these sites embed a per-request token in the HTML. Not one
schedule value had changed. A page-hash tells you the bytes moved; the trip needs to know whether
the SENTENCE behind a published number moved. This monitor compares sentences, and it is the only
thing allowed to mark a row "official value changed".

What it does, per run:

  1. Collects the monitored URLs from the published data files - every table row's own source, the
     structure sheet behind each rule field, every hotel field, and every dated rate-log entry.
  2. Re-fetches each URL, records the bytes, the hash, the HTTP status and the date.
  3. For each published value on that URL, locates the sentence that carries the stored excerpt
     (normalised: whitespace collapsed, typographic quotes/dashes folded, case folded) and
     compares the surrounding sentence, not the page.
  4. Writes:
       data/ea99006a/last_checked.json   per-URL status (the schema the Source monitor page reads)
       data/ea99006a/change_log.json     append-only event log
       data/ea99006a/rates_log.json     a new dated observation when a rate line moved
       data/b3be876c/value_changes.json the value-level defects list the tables and the
                                          verification page mark rows from
  5. Never rewrites a verdict. A changed value marks the row and stops it being ranked; the
     number itself is only replaced by a human (or by scripts/integrate_b3be876c.py) re-reading the
     document, so a defaced or re-formatted page cannot silently rewrite the site.

Modes:
  --fixture-dir DIR   read the "pages" from DIR instead of the network (offline test mode; the
                      file name is the URL's path with / replaced by _)
  --url-map FILE      JSON {url: local_path} override, same offline idea, for one URL at a time
  --limit N           only the first N URLs (smoke run)
  --dry-run           print what would be written, write nothing

Exit code is 1 only when a monitored URL is unreachable or unparseable: a fetch failure is
reported on the site as "could not re-check", never as "no change".
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EA = os.path.join(ROOT, "data", "ea99006a")
B3 = os.path.join(ROOT, "data", "b3be876c")
TODAY = dt.date.today().isoformat()
UA = "Mozilla/5.0 (compatible; Poker5-trip-monitor/1.0; personal trip-planning script)"
MAX_FETCH_SECONDS = 45

# Fields per row that are "published values" the traveller is asked to rely on.
VALUE_FIELDS = {
    "buyin": (r"\$?%s", "buy-in"),
    "guarantee": (r"\$?%s", "guarantee"),
    "start": (r"%s", "start time"),
    "late_reg": (r"%s", "late registration"),
    "chips": (r"%s", "starting chips"),
    "levels": (r"%s", "level duration"),
    "house_fee": (r"%s", "house fee"),
}


def read(path, default):
    p = os.path.join(EA, path) if not os.path.isabs(path) else path
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def norm(text: str) -> str:
    """Fold the cosmetics that change between two renderings of the same sentence."""
    t = unicodedata.normalize("NFKD", text or "")
    t = (t.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
          .replace("\u2013", "-").replace("\u2014", "-").replace("\u00a0", " ").replace("&nbsp;", " "))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip().lower()


def sentences(text: str) -> list[str]:
    """Rough sentence split - enough to compare the sentence that carries a value."""
    t = norm(text)
    t = re.sub(r"\s*\n\s*", " ", t)
    parts = re.split(r"(?<=[.:;])\s+(?=[A-Z0-9\"'(])", t)
    return [p.strip() for p in parts if p.strip()]


def strip_pdf_bytes(raw: bytes) -> str:
    """Crude but honest text recovery from a PDF: read the visible text out of the streams.

    pdftotext is not guaranteed in the runner, and the previous capture pipeline stored full
    extracted text alongside each sheet, so this is only used to re-locate a sentence on a
    re-fetch. If it yields nothing the URL is reported as unparseable rather than as unchanged.
    """
    out: list[str] = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        chunk = m.group(1)
        for tm in re.finditer(rb"\((?:\\.|[^\\()])*\)", chunk):
            s = tm.group(0)[1:-1]
            s = re.sub(rb"\\([()\\])", rb"\1", s)
            s = s.replace(b"\\r", b" ").replace(b"\\n", b" ").replace(b"\\t", b" ")
            try:
                out.append(s.decode("latin-1"))
            except UnicodeDecodeError:
                continue
        if out and "".join(out).strip():
            break
    text = " ".join(out)
    text = re.sub(r"\s+", " ", text)
    return text


def text_of(url: str, raw: bytes) -> str:
    """Visible text of a capture. A PDF is unpacked; anything else is read as text.

    If a ".pdf" URL no longer returns a PDF (a soft 404, a captcha page, an HTML redirect), the
    body is still searched: that case has happened on this trip's sources and must show up as a
    value change, not as "unreadable".
    """
    if raw[:5] == b"%PDF-" or url.lower().endswith(".pdf"):
        text = strip_pdf_bytes(raw)
        if text.strip():
            return text
    return raw.decode("utf-8", "replace")


def fetch(url: str, fixture_dir: str | None, url_map: dict[str, str]) -> tuple[bytes | None, str]:
    """Return (bytes, error). bytes is None when the URL could not be read."""
    if url in url_map:
        p = url_map[url]
        if not os.path.exists(p):
            return None, "fixture missing: %s" % p
        with open(p, "rb") as fh:
            return fh.read(), ""
    if fixture_dir:
        name = re.sub(r"[^A-Za-z0-9.]+", "_", url.split("://", 1)[-1])
        p = os.path.join(fixture_dir, name)
        if not os.path.exists(p):
            return None, "no fixture for %s" % url
        with open(p, "rb") as fh:
            return fh.read(), ""
    if not url.lower().startswith(("http://", "https://")):
        return None, "not an http(s) URL"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=MAX_FETCH_SECONDS) as resp:  # noqa: S310 - fixed hosts
            return resp.read(), ""
    except Exception as exc:  # network/HTTP: report, never guess
        return None, "%s: %s" % (type(exc).__name__, str(exc)[:180])


# ---------------------------------------------------------------- collection
def row_targets(rows: list[dict]) -> dict[str, list[dict]]:
    """url -> the values published from it, each with the excerpt the site is standing on."""
    out: dict[str, list[dict]] = {}
    for r in rows:
        src = r.get("source")
        if not src:
            continue
        vals = []
        for key, (_pat, label) in VALUE_FIELDS.items():
            v = r.get(key)
            if v in (None, ""):
                continue
            field = (r.get("rule_fields") or {}).get(key) or {}
            # A value with no sentence of its own is anchored to the event line instead: searching
            # the sheet-wide rule excerpt for "buy-in" would always match, which is how a page
            # monitor silently misses a price change.
            vals.append({"field": key, "label": label, "value": str(v),
                         "excerpt": field.get("excerpt") or "",
                         "context": context_of(r)})
        for key, f in (r.get("rule_fields") or {}).items():
            if f.get("source") and f["source"] != src:
                out.setdefault(f["source"], []).append(
                    {"row": r, "field": key, "label": key.replace("_", " "),
                     "value": str(f.get("value")), "excerpt": f.get("excerpt") or ""})
        if r.get("entry_evidence", {}).get("source"):
            u = r["entry_evidence"]["source"]
            if u != src:
                out.setdefault(u, []).append(
                    {"row": r, "field": "entry_rule", "label": "entry rule (structure sheet)",
                     "value": r.get("entry_rule", ""), "excerpt": r.get("entry_basis") or ""})
        out.setdefault(src, []).extend({"row": r, **v} for v in vals)
    return out


def hotel_targets(hotels: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for h in hotels:
        for key, label in (("resort_fee_source", "resort fee"), ("rate_floor_source", "poker suite rate"),
                           ("cancel_source", "cancellation"), ("parking_source", "parking"),
                           ("address_source", "address")):
            u = h.get(key)
            val = h.get(key.replace("_source", ""))
            if not u or val in (None, ""):
                continue
            out.setdefault(u, []).append({"hotel": h["name"], "field": key.replace("_source", ""),
                                          "label": label, "value": str(val),
                                          "excerpt": h.get(key.replace("_source", "") + "_note") or ""})
    return out


def rate_targets(log: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in log:
        u = r.get("source")
        if not u:
            continue
        out.setdefault(u, []).append({"rate_log": r.get("hotel", "rate log"), "field": "rate",
                                      "label": "dated rate observation",
                                      "value": str(r.get("nightly_low") or r.get("nightly_average") or ""),
                                      "excerpt": " ".join(r.get("caveats") or [])})
    return out


# ---------------------------------------------------------------- comparison
def context_of(row: dict) -> list[str]:
    """How a row is identified on the page that lists it, for values with no sentence of their own."""
    ctx = []
    no = str(row.get("event_no") or "").strip()
    if no:
        ctx += ["#%s" % no, "event %s" % no]
    name = str(row.get("name") or "").strip()
    if len(name) >= 8:
        ctx.append(name[:60])
    return ctx


def has_context(sent: str, ctx: list[str]) -> bool:
    for c in ctx:
        if c in sent:
            return True
        m = re.fullmatch(r"#(\d+)", c)
        if m and re.search(r"(?<![0-9])#?\b%s\b" % m.group(1), sent):
            return True
    return False


def locate(needles: list[str], text: str) -> str:
    """The sentence that carries the stored excerpt (or any of its distinctive fragments)."""
    sents = sentences(text)
    for n in needles:
        nn = norm(n)
        if len(nn) < 12:
            continue
        for s in sents:
            if nn[:160] in s:
                return s
    # fall back to a value match: "$50,000" style tokens are specific enough on a schedule page
    return ""


def compare(entry: dict, raw: bytes, url: str) -> dict:
    """One monitored value against the freshly fetched document."""
    text = text_of(url, raw)
    if not text.strip():
        return {"state": "unparseable"}
    hay = norm(text)
    val = norm(str(entry.get("value") or ""))
    excerpt = entry.get("excerpt") or ""
    if excerpt:
        sentence = locate([excerpt], text)
        if sentence:
            return {"state": "unchanged", "sentence": sentence[:400]}
    elif val:
        # no sentence of its own: the value has to appear on the line that identifies the event
        ctx = [norm(c) for c in entry.get("context") or [] if c]
        for sent in sentences(text):
            if val in sent and (not ctx or has_context(sent, ctx)):
                return {"state": "unchanged", "sentence": sent[:400]}
    # the anchor is gone: is the value still somewhere on the page, or has it really moved?
    if val and len(val) >= 2 and val in hay:
        return {"state": "moved", "sentence": ""}
    return {"state": "changed", "sentence": ""}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-dir")
    ap.add_argument("--url-map", help="JSON file mapping URL -> local path")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    url_map = {}
    if args.url_map:
        with open(args.url_map, encoding="utf-8") as fh:
            url_map = json.load(fh)

    venetian = read("venetian.json", [])
    others = read("wpt.json", []) + read("other.json", [])
    hotels = read("hotels.json", [])
    rates = read("rates_log.json", [])
    old_ledger = read("last_checked.json", {})
    change_log = read("change_log.json", [])

    targets: dict[str, list[dict]] = {}
    for src, entries in row_targets(venetian).items():
        targets.setdefault(src, []).extend(entries)
    for src, entries in row_targets(others).items():
        targets.setdefault(src, []).extend(entries)
    for src, entries in hotel_targets(hotels).items():
        targets.setdefault(src, []).extend(entries)
    for src, entries in rate_targets(rates).items():
        targets.setdefault(src, []).extend(entries)

    urls = sorted(targets)
    if args.limit:
        urls = urls[: args.limit]
    ledger: dict[str, dict] = {}
    value_changes: list[dict] = []
    new_rate_rows: list[dict] = []
    counts = {"ok": 0, "changed": 0, "error": 0}
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for url in urls:
        entries = targets[url]
        raw, err = fetch(url, args.fixture_dir, url_map)
        prev = old_ledger.get(url) or {}
        rec = {"label": entries[0].get("row", {}).get("name") or entries[0].get("hotel")
               or entries[0].get("rate_log") or url.rsplit("/", 1)[-1],
               "url": url, "last_attempt": now, "values": len(entries)}
        if raw is None:
            rec.update({"status": "error", "http": None, "error": err,
                        "last_checked": prev.get("last_checked"), "first_checked": prev.get("first_checked") or now,
                        "sha256": prev.get("sha256"), "bytes": prev.get("bytes")})
            counts["error"] += 1
            ledger[url] = rec
            continue
        sha = hashlib.sha256(raw).hexdigest()
        page_changed = bool(prev.get("sha256")) and prev["sha256"] != sha
        states = []
        for e in entries:
            res = compare(e, raw, url)
            states.append(res["state"])
            if res["state"] == "unparseable":
                value_changes.append({"detected": now[:10], "url": url, "kind": "unparseable",
                                      "venue": (e.get("row") or {}).get("venue") or e.get("hotel") or "",
                                      "event": (e.get("row") or {}).get("name") or e.get("hotel") or "",
                                      "event_no": (e.get("row") or {}).get("event_no"),
                                      "date": (e.get("row") or {}).get("date"),
                                      "value": e["label"], "field": e["field"],
                                      "published": e.get("value"), "old_excerpt": e.get("excerpt") or "",
                                      "new_excerpt": "",
                                      "note": "the re-fetch produced no readable text, so the value could not be "
                                              "compared - the row is marked unverified rather than left looking fine"})
            if res["state"] in ("changed", "moved"):
                row = e.get("row") or {}
                value_changes.append({
                    "detected": now[:10], "url": url, "kind": res["state"],
                    "venue": row.get("venue") or e.get("hotel") or e.get("rate_log") or "",
                    "event": row.get("name") or e.get("hotel") or "",
                    "event_no": row.get("event_no"), "date": row.get("date"),
                    "value": e["label"], "field": e["field"],
                    "published": e.get("value"), "old_excerpt": e.get("excerpt") or "",
                    "new_excerpt": res.get("sentence") or "",
                    "note": ("the stored sentence is gone and the value does not appear on the page"
                             if res["state"] == "changed" else
                             "the value still appears on the page but not in the recorded sentence - the "
                             "document was re-flowed or the value moved to a different line"),
                })
        status = ("unparseable" if states and all(s2 == "unparseable" for s2 in states)
                  else "changed" if "changed" in states else ("reflow" if "moved" in states
                                                              else ("page-only" if page_changed else "ok")))
        rec.update({"status": status, "http": 200, "error": "", "sha256": sha, "bytes": len(raw),
                    "last_checked": now[:10], "first_checked": prev.get("first_checked") or now[:10],
                    "page_bytes_changed": page_changed,
                    "value_states": {e["field"]: (states[i] if i < len(states) else "unknown")
                                     for i, e in enumerate(entries)}})
        counts["error" if status == "unparseable" else ("changed" if status in ("changed", "reflow") else "ok")] += 1
        if status in ("changed", "reflow", "unparseable"):
            # Canonical change-log schema (the same keys scripts/recheck_ea99006a.py writes and
            # scripts/build_ea99006a.py reads): changed_at / url / label / old_sha256 /
            # new_sha256 / old_bytes / new_bytes. The monitor's own detail (kind, values) rides
            # along as extra keys the builder ignores. Writing a different schema here previously
            # broke the scheduled "Rebuild the canonical site" step with KeyError: 'changed_at'.
            change_log.append({"changed_at": now, "url": url,
                               "label": rec.get("label") or url,
                               "old_sha256": prev.get("sha256") or "", "new_sha256": sha,
                               "old_bytes": prev.get("bytes"), "new_bytes": len(raw),
                               "kind": status,
                               "values": sorted({e["label"] for e in entries if e["field"]})[:8]})
        if status == "changed" and url in rate_targets(rates):
            new_rate_rows.append({"hotel": value_changes[-1].get("venue") or "unknown",
                                  "hotel_key": "unknown", "observed_on": now[:10],
                                  "kind": "re-checked by monitor: the published rate line no longer matches",
                                  "nightly_low": None, "nightly_high": None, "resort_fee_per_night": None,
                                  "tax_rate_pct": None, "source": url,
                                  "source_label": "official page, re-read %s" % now[:10],
                                  "verified": False,
                                  "caveats": ["The sentence this rate was taken from is no longer on the page. The "
                                             "old figure stays published and the row is marked; nothing was inferred "
                                             "from the new page text, which the monitor is not allowed to do."],
                                  "cancellation_deadline": None, "parking": None})
        ledger[url] = rec

    summary = {"run": now, "urls": len(urls), "counts": counts, "value_changes": len(value_changes),
               "page_only_changes": sum(1 for r in ledger.values() if r.get("status") == "page-only"),
               "note": ("statuses: ok = nothing moved; page-only = bytes differ, every published sentence still "
                        "reads the same; reflow = the value is still on the page but the recorded sentence moved; "
                        "changed = the value itself is gone; error = could not re-check, which is never reported "
                        "as 'no change'.")}
    if args.dry_run:
        print(json.dumps({"summary": summary, "value_changes": value_changes,
                          "ledger_sample": dict(list(ledger.items())[:2])}, indent=1))
        return 0
    os.makedirs(B3, exist_ok=True)
    with open(os.path.join(EA, "last_checked.json"), "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(EA, "change_log.json"), "w", encoding="utf-8") as fh:
        json.dump(change_log[-400:], fh, indent=1)
        fh.write("\n")
    with open(os.path.join(B3, "value_changes.json"), "w", encoding="utf-8") as fh:
        json.dump(value_changes, fh, indent=1)
        fh.write("\n")
    if new_rate_rows:
        with open(os.path.join(EA, "rates_log.json"), "w", encoding="utf-8") as fh:
            json.dump(rates + new_rate_rows, fh, indent=1)
            fh.write("\n")
    with open(os.path.join(B3, "monitor_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
        fh.write("\n")
    print("monitored %d urls: %s" % (len(urls), json.dumps(counts)))
    print("value-level changes: %d (written to data/b3be876c/value_changes.json)" % len(value_changes))
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
