#!/usr/bin/env python3
"""Validate source-ledger integrity offline or check monitored official pages live.

Offline mode never makes network requests. `--live` checks HTTP availability and
expected fact markers; a changed or missing marker is a manual-review signal,
not permission to rewrite research data automatically.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "data" / "final" / "source-ledger.json"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def normalize(value: str) -> str:
    value = html.unescape(value).replace("\u00a0", " ").replace("\u2011", "-")
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    value = value.casefold()
    return re.sub(r"\s+", " ", value).strip()


def load_ledger() -> dict[str, Any]:
    data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    if not isinstance(data.get("sources"), list):
        raise ValueError("source-ledger.json must contain a sources array")
    return data


def offline_check(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for source in ledger["sources"]:
        sid = source.get("id")
        if not sid or sid in ids:
            errors.append(f"duplicate or missing source id: {sid!r}")
        ids.add(sid)
        url = source.get("url", "")
        if not url.startswith("https://"):
            errors.append(f"{sid}: URL is not HTTPS")
        if source.get("kind") not in {"webpage", "pdf"}:
            errors.append(f"{sid}: unknown source kind {source.get('kind')!r}")
        monitor = source.get("monitor")
        if not monitor:
            continue
        mode = monitor.get("mode")
        if mode not in {"availability", "markers", "pdf-markers"}:
            errors.append(f"{sid}: unsupported monitor mode {mode!r}")
        if mode in {"markers", "pdf-markers"} and not monitor.get("markers"):
            errors.append(f"{sid}: expected markers are missing")
        if monitor.get("compareNormalizedText") and source.get("kind") != "pdf":
            errors.append(f"{sid}: normalized-text baseline comparison is reserved for static PDFs")
        if monitor.get("minBytes", 0) < 0:
            errors.append(f"{sid}: minBytes must be nonnegative")
        if mode == "pdf-markers" and source.get("kind") != "pdf":
            errors.append(f"{sid}: pdf-markers monitor must point to a PDF")
    if not any(source.get("id") == "venetian-schedule" for source in ledger["sources"]):
        errors.append("official Venetian DSE IV schedule source is missing")
    for n in range(1, 38):
        if f"venetian-structure-{n:02d}" not in ids:
            errors.append(f"Venetian structure PDF {n} is missing from the ledger")
    return errors


def extract_text(data: bytes, content_type: str, kind: str) -> str:
    if kind == "pdf" or "pdf" in content_type.casefold():
        try:
            from pypdf import PdfReader  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("pypdf is required for live PDF marker checks") from exc
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    decoded = data.decode("utf-8", errors="replace")
    parser = TextExtractor()
    parser.feed(decoded)
    # Include raw markup too: some official pages expose facts in JSON-LD or page state.
    return "\n".join(parser.parts) + "\n" + decoded


def check_source(source: dict[str, Any], timeout: int, max_bytes: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": source.get("id"), "title": source.get("title"), "url": source.get("url"),
        "mode": source.get("monitor", {}).get("mode"), "status": "ok", "httpStatus": None,
        "bytes": 0, "sha256": None, "normalizedTextSha256": None, "missingMarkers": [], "error": None,
    }
    request = urllib.request.Request(
        source["url"], headers={"User-Agent": "Poker5-official-source-monitor/1.0 (+https://github.com/karagemop466-tech/Poker5)"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result["httpStatus"] = response.status
            content_type = response.headers.get("Content-Type", "")
            payload = response.read(max_bytes + 1)
        if len(payload) > max_bytes:
            result["error"] = f"response exceeds configured {max_bytes:,}-byte limit"
            result["status"] = "error"
            return result
        result["bytes"] = len(payload)
        result["sha256"] = hashlib.sha256(payload).hexdigest()
        monitor = source.get("monitor", {})
        min_bytes = int(monitor.get("minBytes", 0))
        if len(payload) < min_bytes:
            result["status"] = "changed"
            result["error"] = f"response size {len(payload)} is below {min_bytes} bytes"
            return result
        needs_text = monitor.get("mode") in {"markers", "pdf-markers"} or monitor.get("compareNormalizedText")
        if needs_text:
            text = normalize(extract_text(payload, content_type, source.get("kind", "webpage")))
            result["normalizedTextSha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if monitor.get("mode") in {"markers", "pdf-markers"}:
                missing = [marker for marker in monitor.get("markers", []) if normalize(marker) not in text]
                if missing:
                    result["status"] = "changed"
                    result["missingMarkers"] = missing
                    result["error"] = "expected fact marker(s) not found; manual review required"
    except urllib.error.HTTPError as exc:
        result["status"] = "error"
        result["httpStatus"] = exc.code
        result["error"] = f"HTTP {exc.code}: {exc.reason}"
    except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, ValueError) as exc:
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def markdown_report(report: dict[str, Any]) -> str:
    rows = report["results"]
    problems = [r for r in rows if r["status"] not in {"ok", "baseline"}]
    baselines = sum(1 for r in rows if r["status"] == "baseline")
    lines = [
        "## Official-source monitor (a9d1e02d)",
        f"- Checked at: `{report['checkedAt']}`",
        f"- Monitored: **{len(rows)}** · passed / baseline: **{len(rows) - len(problems)}** · first baselines: **{baselines}** · review required: **{len(problems)}**",
        "- A marker miss, text-fingerprint change or fetch failure is a human-review signal; no source data was modified.",
    ]
    if problems:
        lines += ["", "### Sources needing review"]
        for item in problems:
            lines.append(f"- **{item['id']}** — {item.get('error') or item['status']} — {item['url']}")
            if item.get("missingMarkers"):
                lines.append(f"  - Missing markers: {', '.join('`' + m + '`' for m in item['missingMarkers'])}")
    else:
        lines += ["", "All monitored sources returned and retained their expected markers. PDFs without a previous text baseline were initialized for the next run."]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="fetch monitored official URLs and check markers")
    parser.add_argument("--report", type=Path, help="write machine-readable JSON results to this path")
    parser.add_argument("--state", type=Path, help="read / update normalized text fingerprints for static PDFs")
    parser.add_argument("--fail-on-review", action="store_true", help="exit nonzero when any live source needs human review")
    parser.add_argument("--timeout", type=int, default=35, help="per-source network timeout in seconds")
    parser.add_argument("--workers", type=int, default=8, help="parallel source checks")
    parser.add_argument("--max-bytes", type=int, default=20_000_000, help="per-source download size cap")
    args = parser.parse_args()

    try:
        ledger = load_ledger()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    errors = offline_check(ledger)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Offline ledger check passed: {len(ledger['sources'])} unique HTTPS sources, 37 Venetian structure PDFs.")
    if not args.live:
        print("No network requests made. Use --live to execute scheduled source checks.")
        return

    monitored = [s for s in ledger["sources"] if s.get("monitor")]
    previous_hashes: dict[str, str] = {}
    if args.state and args.state.exists():
        try:
            state_doc = json.loads(args.state.read_text(encoding="utf-8"))
            previous_hashes = state_doc.get("normalizedTextSha256BySource", {})
            if not isinstance(previous_hashes, dict):
                raise ValueError("normalizedTextSha256BySource must be an object")
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: cannot read monitor baseline {args.state}: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc

    started = time.monotonic()
    results: list[dict[str, Any]] = []
    source_by_id = {source["id"]: source for source in monitored}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        jobs = {pool.submit(check_source, source, args.timeout, args.max_bytes): source for source in monitored}
        for future in concurrent.futures.as_completed(jobs):
            source = jobs[future]
            try:
                results.append(future.result())
            except Exception as exc:  # noqa: BLE001
                results.append({"id": source.get("id"), "title": source.get("title"), "url": source.get("url"), "status": "error", "error": f"Unhandled: {type(exc).__name__}: {exc}"})
    results.sort(key=lambda item: str(item.get("id")))
    for result in results:
        source = source_by_id.get(result.get("id"), {})
        monitor = source.get("monitor", {})
        if result.get("status") != "ok" or not monitor.get("compareNormalizedText"):
            continue
        fingerprint = result.get("normalizedTextSha256")
        if not fingerprint:
            result["status"] = "error"
            result["error"] = "normalized PDF text could not be fingerprinted"
            continue
        previous = previous_hashes.get(result["id"])
        if previous is None:
            result["status"] = "baseline"
        elif previous != fingerprint:
            result["status"] = "changed"
            result["error"] = "normalized PDF text fingerprint changed; manual review required"

    report = {
        "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ledgerCheckedAt": ledger.get("meta", {}).get("researchedAt"),
        "monitoredCount": len(monitored), "durationSeconds": round(time.monotonic() - started, 2),
        "results": results,
    }
    report["summary"] = {status: sum(1 for r in results if r.get("status") == status) for status in ("ok", "baseline", "changed", "error")}
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    summary = markdown_report(report)
    print(summary)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as f:
            f.write(summary)

    problems = any(r.get("status") not in {"ok", "baseline"} for r in results)
    if args.state and not problems:
        next_hashes = dict(previous_hashes)
        for result in results:
            if result.get("normalizedTextSha256") and result.get("status") in {"ok", "baseline"}:
                if source_by_id.get(result.get("id"), {}).get("monitor", {}).get("compareNormalizedText"):
                    next_hashes[result["id"]] = result["normalizedTextSha256"]
        args.state.parent.mkdir(parents=True, exist_ok=True)
        args.state.write_text(json.dumps({"updatedAt": report["checkedAt"], "normalizedTextSha256BySource": next_hashes}, indent=2) + "\n", encoding="utf-8")
    if problems:
        for result in results:
            if result.get("status") in {"ok", "baseline"}:
                continue
            message = f"{result.get('id')}: {result.get('error') or result.get('status')} — {result.get('url', '')}"
            message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::warning title=Official source needs review::{message}")
        if args.fail_on_review:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
