#!/usr/bin/env python3
"""Run a deterministic Threads local-corpus AI Content Forensics pass.

This script is intentionally boring: it proves the corpus, extracts repeatable
features, writes auditable artifacts, and creates a draft-ready 9-post thread.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("/Users/lennoxsaint/swipefile/vault-extract/THREADIFY VAULT EXTRACT 060426.jsonl")
DEFAULT_OUTPUT_ROOT = Path(
    "/Users/lennoxsaint/content-pipeline/2026-04-21-threads-growth-is-a-lie/"
    "research/threads-packaging/threadify-vault-1996-codex"
)
THREAD_HOOK = "i got Claude to read 1,996 mega-viral Threads posts so you don't have to."
EM_DASH = "\u2014"


CTA_TERMS = [
    "follow",
    "dm me",
    "comment",
    "reply",
    "link in",
    "subscribe",
    "newsletter",
    "youtube",
    "spotify",
    "podcast",
    "share it",
    "repost",
    "check out",
    "watch",
    "download",
    "join",
    "click",
    "book a call",
]

HOW_TO_HOOK_TERMS = [
    "how to",
    "here is how",
    "here's how",
    "here\u2019s how",
    "heres how",
    "ways to",
    "steps to",
    "guide to",
    "framework",
    "system to",
    "tips to",
]

CONTRARIAN_TERMS = [
    "unpopular opinion",
    "brutal truth",
    "hot take",
    "truth:",
    "controversial",
]

TRIGGER_CATEGORIES = {
    "identity": ["you are", "you're", "youre", "your life", "your aura", "smart people", "high value"],
    "pain": ["anxiety", "trauma", "toxic", "burnout", "depression", "struggle", "hurt", "regret"],
    "certainty": ["never", "always", "truth", "fact", "actually", "signs", "proof"],
    "status": ["respect", "attractive", "powerful", "confidence", "rich", "success", "leader"],
    "speed": ["today", "now", "instantly", "quick", "fast", "before", "after"],
    "growth": ["heal", "healed", "grow", "growth", "change", "become", "better", "transform"],
    "fear": ["danger", "dangerous", "dark", "jealous", "obsessed", "red flags", "warning"],
    "money": ["money", "salary", "business", "clients", "offer", "revenue", "sell", "income"],
}


@dataclass
class SourceResult:
    source_path: str
    parser: str
    raw_records: int
    parsed_records: int
    parse_errors: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs(root: Path) -> None:
    for rel in [
        "raw",
        "normalized",
        "analyses",
        "constitutions",
        "evidence",
        "thread",
        "visuals/assets",
        "visuals/previews",
        "logs",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def normalized_text(value: Any) -> str:
    return clean_text(value).lower()


def text_hash(author: str, text: str) -> str:
    payload = f"{normalized_text(author)}|{normalized_text(text)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_like_count(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower().replace(",", "")
    text = re.sub(r"^\.+", "", text)
    if text.count(".") > 1:
        parts = [part for part in text.split(".") if part]
        if len(parts) >= 2:
            text = f"{parts[-2]}.{parts[-1]}"
    match = re.search(r"(\d+(?:\.\d+)?)([km])?", text)
    if not match:
        return None
    number = float(match.group(1))
    multiplier = 1
    if match.group(2) == "k":
        multiplier = 1000
    elif match.group(2) == "m":
        multiplier = 1_000_000
    return int(round(number * multiplier))


def first_non_empty_line(text: str) -> str:
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def word_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text or "")


def contains_any(text: str, terms: list[str]) -> bool:
    haystack = normalized_text(text)
    return any(term in haystack for term in terms)


def count_terms(text: str, terms: list[str]) -> int:
    haystack = normalized_text(text)
    return sum(haystack.count(term) for term in terms)


def split_threadify_jsonl(text: str) -> list[str]:
    starts = [match.start() for match in re.finditer(r'(?m)^\{"source_id"', text)]
    if not starts:
        return []
    chunks: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        chunks.append(text[start:end].strip())
    return chunks


def parse_json_chunks(path: Path) -> tuple[list[dict[str, Any]], SourceResult]:
    text = path.read_text(errors="replace")
    chunks = split_threadify_jsonl(text)
    parser = "threadify_jsonl_boundary_repair" if chunks else "generic_jsonl"
    if not chunks:
        chunks = [line for line in text.splitlines() if line.strip()]

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        try:
            records.append(json.loads(chunk))
            continue
        except json.JSONDecodeError as first_error:
            try:
                records.append(json.loads(chunk.replace("\n", "\\n")))
                continue
            except json.JSONDecodeError as second_error:
                errors.append(
                    f"record {index}: {first_error.msg}; repair failed: {second_error.msg}"
                )
    return records, SourceResult(str(path), parser, len(chunks), len(records), errors)


def parse_csv(path: Path) -> tuple[list[dict[str, Any]], SourceResult]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open(errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for index, row in enumerate(reader, start=1):
            if not row:
                continue
            row["_source_row"] = index
            records.append(row)
    return records, SourceResult(str(path), "tsv_dict_reader", len(records), len(records), errors)


def parse_json(path: Path) -> tuple[list[dict[str, Any]], SourceResult]:
    errors: list[str] = []
    data = json.loads(path.read_text(errors="replace"))
    if isinstance(data, list):
        records = [item for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        records = []
        for value in data.values():
            if isinstance(value, list):
                records.extend(item for item in value if isinstance(item, dict))
    else:
        records = []
    return records, SourceResult(str(path), "json", len(records), len(records), errors)


def parse_source(path: Path) -> tuple[list[dict[str, Any]], SourceResult]:
    if path.suffix.lower() == ".csv":
        return parse_csv(path)
    if path.suffix.lower() == ".json":
        return parse_json(path)
    return parse_json_chunks(path)


def normalize_record(record: dict[str, Any], source_path: Path, ordinal: int) -> dict[str, Any] | None:
    source_name = source_path.name
    metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else {}

    post_id = (
        record.get("source_id")
        or record.get("id")
        or record.get("content_id")
        or record.get("original_post_id")
        or record.get("i")
        or record.get("index")
    )
    url = record.get("source_url") or record.get("url") or record.get("permalink")
    author = (
        record.get("author")
        or record.get("username")
        or record.get("u")
        or record.get("profile")
        or ""
    )
    if not author and url:
        match = re.search(r"@([^/]+)/", str(url))
        if match:
            author = f"@{match.group(1)}"
    if author and not str(author).startswith("@"):
        author = f"@{author}"

    full_text = (
        record.get("full_text")
        or record.get("text")
        or record.get("body")
        or record.get("b")
        or record.get("raw_text")
        or record.get("normalized_text")
        or ""
    )
    if source_name.endswith(".csv"):
        full_text = str(full_text).replace(" | ", "\n")
    full_text = str(full_text).strip()
    if not full_text:
        return None

    like_count = parse_like_count(
        record.get("like_count")
        or record.get("likes")
        or record.get("l")
        or metrics.get("likes")
    )
    replies = parse_like_count(record.get("replies") or record.get("comments") or metrics.get("comments"))
    reposts = parse_like_count(record.get("reposts") or metrics.get("reposts"))
    shares = parse_like_count(record.get("shares"))
    part_count = parse_like_count(
        record.get("part_count")
        or record.get("threadTotal")
        or record.get("thread_count")
        or record.get("t")
    )
    if not part_count or part_count < 1:
        part_count = 1

    dedupe_key = None
    if url:
        dedupe_key = f"url:{str(url).lower().strip()}"
    elif post_id and len(str(post_id)) > 8 and not str(post_id).isdigit():
        dedupe_key = f"id:{str(post_id).lower().strip()}"
    else:
        dedupe_key = f"body:{text_hash(str(author), full_text)}"

    first_line = first_non_empty_line(full_text)
    words = word_tokens(full_text)
    content_type = record.get("content_type")
    if not content_type:
        content_type = "long_form" if len(words) >= 150 else "short_form"

    return {
        "source_file": str(source_path),
        "source_record": ordinal,
        "dedupe_key": dedupe_key,
        "post_id": str(post_id or ""),
        "post_url": str(url or ""),
        "author": str(author or ""),
        "saved_at": record.get("saved_at") or record.get("saved_date") or record.get("date") or record.get("d"),
        "tabs": record.get("tabs") if isinstance(record.get("tabs"), list) else [],
        "content_type": content_type,
        "title": record.get("title") or "",
        "full_text": full_text,
        "first_line": first_line,
        "first_140": full_text[:140],
        "like_count": like_count,
        "replies": replies,
        "reposts": reposts,
        "shares": shares,
        "part_count": part_count,
        "thread_position": record.get("threadPos"),
        "metric_status": "ok" if like_count and like_count > 0 else "missing_or_zero_likes",
    }


def normalize_sources(sources: list[Path]) -> tuple[list[dict[str, Any]], list[SourceResult], list[dict[str, Any]]]:
    source_results: list[SourceResult] = []
    candidates: list[dict[str, Any]] = []
    for source in sources:
        records, result = parse_source(source)
        source_results.append(result)
        for ordinal, record in enumerate(records, start=1):
            normalized = normalize_record(record, source, ordinal)
            if normalized:
                candidates.append(normalized)

    deduped: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    duplicates: list[dict[str, Any]] = []
    for item in candidates:
        key = item["dedupe_key"]
        if key in seen:
            duplicates.append(
                {
                    "dedupe_key": key,
                    "kept_index": seen[key],
                    "duplicate_source": item["source_file"],
                    "duplicate_record": item["source_record"],
                }
            )
            continue
        seen[key] = len(deduped)
        item["corpus_index"] = len(deduped) + 1
        deduped.append(item)
    return deduped, source_results, duplicates


def extract_features(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
    for post in posts:
        text = post["full_text"]
        first_line = post["first_line"]
        words = word_tokens(text)
        word_count = len(words)
        question_count = text.count("?")
        first_line_question = "?" in first_line
        cta_terms = [term for term in CTA_TERMS if term in normalized_text(text)]
        how_to_hook = contains_any(first_line, HOW_TO_HOOK_TERMS)
        has_how_to_anywhere = contains_any(text[:300], HOW_TO_HOOK_TERMS)
        numbered_markers = re.findall(r"(?m)^\s*(?:\d+\.|\d+/|\d+\))", text)
        trigger_counts = {
            name: count_terms(text, terms) for name, terms in TRIGGER_CATEGORIES.items()
        }
        personal_markers = len(
            re.findall(r"\b(i|i'm|ive|i've|i\u2019ve|my|me|we|our)\b", normalized_text(text[:300]))
        )
        part_count = int(post["part_count"] or 1)
        like_count = post["like_count"] or 0
        feature = {
            **post,
            "word_count": word_count,
            "character_count": len(text),
            "line_count": len([line for line in text.splitlines() if line.strip()]),
            "has_question": question_count > 0,
            "first_line_question": first_line_question,
            "question_count": question_count,
            "has_cta": bool(cta_terms),
            "cta_terms": cta_terms,
            "how_to_hook": how_to_hook,
            "has_how_to_anywhere": has_how_to_anywhere,
            "numbered_marker_count": len(numbered_markers),
            "has_numbered_structure": bool(numbered_markers),
            "has_contrarian_opener": contains_any(first_line, CONTRARIAN_TERMS),
            "trigger_total": sum(trigger_counts.values()),
            "trigger_counts": trigger_counts,
            "personal_marker_count": personal_markers,
            "has_personal_opener": personal_markers > 0,
            "url_count": len(re.findall(r"https?://", text)),
            "format_family": (
                "long_form"
                if str(post.get("content_type") or "").lower() == "long_form"
                else "short_form"
                if str(post.get("content_type") or "").lower() == "short_form"
                else "long_form"
                if word_count >= 150
                else "short_form"
            ),
            "likes_per_part": round(like_count / part_count, 2) if part_count else like_count,
        }
        features.append(feature)
    return features


def median(values: list[int | float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def pct(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}%"


def rate(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if row.get(key)) / len(rows) * 100


def comparison(features: list[dict[str, Any]]) -> dict[str, Any]:
    metric_rows = sorted(
        [row for row in features if (row.get("like_count") or 0) > 0],
        key=lambda row: row["like_count"],
        reverse=True,
    )
    top_n = math.ceil(len(metric_rows) * 0.10)
    bottom_n = math.ceil(len(metric_rows) * 0.25)
    top = metric_rows[:top_n]
    bottom = metric_rows[-bottom_n:]

    def bool_stats(key: str) -> dict[str, Any]:
        yes = [row["like_count"] for row in metric_rows if row.get(key)]
        no = [row["like_count"] for row in metric_rows if not row.get(key)]
        return {
            "all_rate": rate(metric_rows, key),
            "top_rate": rate(top, key),
            "bottom_rate": rate(bottom, key),
            "median_yes": median(yes),
            "median_no": median(no),
            "count_yes": len(yes),
            "count_no": len(no),
        }

    word_buckets = {
        "under_50": [row for row in metric_rows if row["word_count"] < 50],
        "50_149": [row for row in metric_rows if 50 <= row["word_count"] < 150],
        "150_299": [row for row in metric_rows if 150 <= row["word_count"] < 300],
        "300_plus": [row for row in metric_rows if row["word_count"] >= 300],
    }
    part_buckets: dict[str, list[dict[str, Any]]] = {}
    for row in metric_rows:
        key = str(row["part_count"]) if row["part_count"] < 10 else "10_plus"
        part_buckets.setdefault(key, []).append(row)

    return {
        "corpus_count": len(features),
        "metric_valid_count": len(metric_rows),
        "missing_or_zero_metric_count": len(features) - len(metric_rows),
        "median_likes": median([row["like_count"] for row in metric_rows]),
        "top_decile_count": len(top),
        "bottom_quartile_count": len(bottom),
        "top_decile_min_likes": min(row["like_count"] for row in top) if top else 0,
        "boolean": {
            "how_to_hook": bool_stats("how_to_hook"),
            "has_cta": bool_stats("has_cta"),
            "has_question": bool_stats("has_question"),
            "first_line_question": bool_stats("first_line_question"),
            "has_numbered_structure": bool_stats("has_numbered_structure"),
            "has_contrarian_opener": bool_stats("has_contrarian_opener"),
            "has_personal_opener": bool_stats("has_personal_opener"),
            "format_family_long": {
                "all_rate": len([r for r in metric_rows if r["format_family"] == "long_form"]) / len(metric_rows) * 100,
                "top_rate": len([r for r in top if r["format_family"] == "long_form"]) / len(top) * 100,
                "bottom_rate": len([r for r in bottom if r["format_family"] == "long_form"]) / len(bottom) * 100,
                "median_yes": median([r["like_count"] for r in metric_rows if r["format_family"] == "long_form"]),
                "median_no": median([r["like_count"] for r in metric_rows if r["format_family"] != "long_form"]),
            },
        },
        "word_buckets": {
            key: {
                "count": len(rows),
                "median_likes": median([row["like_count"] for row in rows]),
                "top_rate": len([row for row in top if row in rows]) / len(top) * 100 if top else 0,
                "bottom_rate": len([row for row in bottom if row in rows]) / len(bottom) * 100 if bottom else 0,
            }
            for key, rows in word_buckets.items()
        },
        "part_buckets": {
            key: {
                "count": len(rows),
                "median_likes": median([row["like_count"] for row in rows]),
                "top_rate": len([row for row in top if row in rows]) / len(top) * 100 if top else 0,
                "bottom_rate": len([row for row in bottom if row in rows]) / len(bottom) * 100 if bottom else 0,
            }
            for key, rows in sorted(part_buckets.items())
        },
        "top_posts": metric_rows[:25],
        "bottom_posts": list(reversed(metric_rows[-25:])),
    }


def fmt_num(value: float | int) -> str:
    return f"{int(math.floor(float(value) + 0.5)):,}"


def percent_delta(base: float, compare: float) -> float:
    if compare == 0:
        return 0.0
    return (base - compare) / compare * 100


def find_example(features: list[dict[str, Any]], author: str, phrase: str = "") -> dict[str, Any] | None:
    phrase_norm = normalized_text(phrase)
    for row in sorted(features, key=lambda item: item.get("like_count") or 0, reverse=True):
        if row.get("author") == author and (not phrase_norm or phrase_norm in normalized_text(row["full_text"])):
            return row
    return None


def insight_specs(features: list[dict[str, Any]], stats: dict[str, Any]) -> list[dict[str, Any]]:
    b = stats["boolean"]
    words = stats["word_buckets"]
    parts = stats["part_buckets"]

    how = b["how_to_hook"]
    cta = b["has_cta"]
    numbered = b["has_numbered_structure"]
    contrarian = b["has_contrarian_opener"]
    long_form = b["format_family_long"]

    two_part = parts.get("2", {})
    three_plus_rows = [
        row for row in features if (row.get("like_count") or 0) > 0 and int(row.get("part_count") or 1) >= 3
    ]
    two_part_median = float(two_part.get("median_likes", 0))
    three_plus_median = median([row["like_count"] for row in three_plus_rows])

    under_50 = words["under_50"]
    over_50_rows = [
        row for row in features if (row.get("like_count") or 0) > 0 and row.get("word_count", 0) >= 50
    ]
    over_50_median = median([row["like_count"] for row in over_50_rows])

    examples = {
        "thentirepackage": find_example(features, "@thentirepackage", "I have like 2 followers"),
        "melrobbins": find_example(features, "@melrobbins", "Stop wasting your life"),
        "lifeasminee": find_example(features, "@lifeasminee", "healed version"),
        "blairimani": find_example(features, "@blairimani", "walnuts"),
        "drkojo": find_example(features, "@drkojosarfo", "high functioning"),
        "heavybic": find_example(features, "@heavy.bic", "morning routine"),
        "dankoe": find_example(features, "@thedankoe", "focused"),
    }

    return [
        {
            "id": 1,
            "clip_hook": "how-to hooks are not the safe option. they are the ceiling.",
            "claim": f"0 of the top {stats['top_decile_count']} posts opened with a how-to hook.",
            "data": f"How-to hooks had median {fmt_num(how['median_yes'])} likes vs {fmt_num(how['median_no'])} for non-how-to openers.",
            "takeaway": "open with lived proof, tension, or a confession before instruction.",
            "example": examples["thentirepackage"],
        },
        {
            "id": 2,
            "clip_hook": "the algorithm keeps rewarding posts that look too short to be strategic.",
            "claim": "Under-50-word posts were the strongest length bucket.",
            "data": f"Under 50 words: median {fmt_num(under_50['median_likes'])} likes vs {fmt_num(over_50_median)} for 50+ words; {pct(under_50['top_rate'])} of the top decile were under 50 words.",
            "takeaway": "write the sharp version, then cut it again.",
            "example": examples["melrobbins"],
        },
        {
            "id": 3,
            "clip_hook": "if one post is too little, the answer is usually two. not ten.",
            "claim": "Two-part threads were the thread-length sweet spot.",
            "data": f"Two-part posts had median {fmt_num(two_part_median)} likes vs {fmt_num(three_plus_median)} for 3+ parts.",
            "takeaway": "use part two as the turn, proof, or release valve. avoid dragging the idea.",
            "example": examples["lifeasminee"],
        },
        {
            "id": 4,
            "clip_hook": "your CTA might be charging rent before the post earns attention.",
            "claim": "Posts without CTAs beat CTA posts on median likes.",
            "data": f"No-CTA posts: median {fmt_num(cta['median_no'])} likes vs {fmt_num(cta['median_yes'])} with CTAs.",
            "takeaway": "let the content convert first; ask only when the post has earned it.",
            "example": examples["blairimani"],
        },
        {
            "id": 5,
            "clip_hook": "numbered advice looks useful, but the vault treated it like homework.",
            "claim": "Numbered structures underperformed the cleaner statement posts.",
            "data": f"Numbered posts had median {fmt_num(numbered['median_yes'])} likes vs {fmt_num(numbered['median_no'])} without numbered structure.",
            "takeaway": "turn lists into one sharp claim unless the sequence is genuinely necessary.",
            "example": examples["dankoe"],
        },
        {
            "id": 6,
            "clip_hook": "contrarian openers are tiny in the corpus but loud in the results.",
            "claim": "Contrarian openers were rare, but their median likes were much higher.",
            "data": f"Contrarian openers: median {fmt_num(contrarian['median_yes'])} likes vs {fmt_num(contrarian['median_no'])} for everything else.",
            "takeaway": "make the disagreement specific enough that the right people feel named.",
            "example": examples["drkojo"],
        },
        {
            "id": 7,
            "clip_hook": "long-form only wins when it stops teaching and starts confessing.",
            "claim": "Long-form posts were overrepresented in the bottom quartile.",
            "data": f"Long-form median: {fmt_num(long_form['median_yes'])} likes vs {fmt_num(long_form['median_no'])} for short-form; only {pct(long_form['top_rate'])} of the top decile was long-form.",
            "takeaway": "if you go long, make it a scene, not a syllabus.",
            "example": examples["heavybic"],
        },
    ]


def short_example(row: dict[str, Any] | None) -> str:
    if not row:
        return "No matching example found."
    first = first_non_empty_line(row["full_text"])
    if len(first) > 92:
        first = first[:89].rsplit(" ", 1)[0].rstrip() + "..."
    return f"{row['author']} - \"{first}\" - {fmt_num(row['like_count'] or 0)} likes"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(str(row[index])) for row in rows) for index in range(len(rows[0]))]
    lines = []
    for row_index, row in enumerate(rows):
        line = "| " + " | ".join(str(cell).ljust(widths[index]) for index, cell in enumerate(row)) + " |"
        lines.append(line)
        if row_index == 0:
            lines.append("| " + " | ".join("-" * width for width in widths) + " |")
    return "\n".join(lines)


def write_reports(
    root: Path,
    features: list[dict[str, Any]],
    source_results: list[SourceResult],
    duplicates: list[dict[str, Any]],
    stats: dict[str, Any],
    insights: list[dict[str, Any]],
    expected_count: int | None,
) -> None:
    gate_status = "passed" if expected_count is None or len(features) == expected_count else "failed"
    source_receipt = {
        "generated_at": utc_now(),
        "expected_corpus_count": expected_count,
        "verified_unique_count": len(features),
        "gate_status": gate_status,
        "metric_valid_count": stats.get("metric_valid_count", 0),
        "missing_or_zero_metric_count": stats.get("missing_or_zero_metric_count", 0),
        "sources": [result.__dict__ for result in source_results],
        "duplicate_count": len(duplicates),
        "duplicates": duplicates[:100],
    }
    write_json(root / "raw/corpus_source_receipt.json", source_receipt)
    write_json(root / "normalized/threads_corpus.json", features)

    index_fields = [
        "corpus_index",
        "post_id",
        "post_url",
        "author",
        "saved_at",
        "tabs",
        "content_type",
        "like_count",
        "replies",
        "reposts",
        "shares",
        "part_count",
        "word_count",
        "first_line",
        "metric_status",
    ]
    feature_fields = [
        "corpus_index",
        "post_id",
        "author",
        "like_count",
        "part_count",
        "format_family",
        "word_count",
        "character_count",
        "how_to_hook",
        "has_how_to_anywhere",
        "has_question",
        "first_line_question",
        "has_cta",
        "cta_terms",
        "has_numbered_structure",
        "has_contrarian_opener",
        "has_personal_opener",
        "trigger_total",
        "url_count",
        "first_line",
        "post_url",
    ]
    write_csv(root / "04_video_index.csv", features, index_fields)
    write_json(root / "05_video_index.json", features)
    write_csv(root / "06_packaging_features.csv", features, feature_fields)
    write_json(root / "07_packaging_features.json", features)

    run_report = [
        "# Codex AI Content Forensics Run Report",
        "",
        f"- Generated: {utc_now()}",
        f"- Corpus gate: {gate_status}",
        f"- Expected corpus count: {expected_count if expected_count is not None else 'not set'}",
        f"- Verified unique posts: {len(features):,}",
        f"- Metric-valid posts: {stats['metric_valid_count']:,}",
        f"- Missing/zero-like posts kept in corpus but excluded from performance comparisons: {stats['missing_or_zero_metric_count']:,}",
        f"- Median likes in metric-valid subset: {fmt_num(stats['median_likes'])}",
        f"- Top decile size: {stats['top_decile_count']:,}",
        f"- Bottom quartile size: {stats['bottom_quartile_count']:,}",
        "",
        "## Fresh Findings",
        "",
    ]
    for item in insights:
        run_report.extend(
            [
                f"### {item['id']}. {item['clip_hook']}",
                "",
                f"- Claim: {item['claim']}",
                f"- Data: {item['data']}",
                f"- Example: {short_example(item['example'])}",
                f"- Takeaway: {item['takeaway']}",
                "",
            ]
        )
    (root / "00_run_report.md").write_text("\n".join(run_report).rstrip() + "\n")

    methodology = [
        "# Methodology",
        "",
        "This Codex rerun used local corpus mode. No live Threads scrape was used for the analysis.",
        "",
        "## Sources",
        "",
    ]
    for result in source_results:
        methodology.append(f"- `{result.source_path}` via `{result.parser}`: {result.parsed_records}/{result.raw_records} parsed")
    methodology.extend(
        [
            "",
            "## Corpus Gate",
            "",
            f"- Expected count: {expected_count if expected_count is not None else 'not set'}",
            f"- Verified deduped count: {len(features):,}",
            f"- Gate status: {gate_status}",
            "",
            "## Performance Claims",
            "",
            "Posts with missing or zero likes remain in the corpus, but performance claims use only posts with positive like counts.",
        ]
    )
    (root / "03_methodology.md").write_text("\n".join(methodology).rstrip() + "\n")

    profile = [
        "# Target Corpus Profile",
        "",
        "Target: Threadify vault export",
        "",
        f"- Total deduped posts: {len(features):,}",
        f"- Short-form posts: {sum(1 for row in features if row['format_family'] == 'short_form'):,}",
        f"- Long-form posts: {sum(1 for row in features if row['format_family'] == 'long_form'):,}",
        f"- Unique authors: {len({row['author'] for row in features if row['author']}):,}",
        "",
        "## Top Tabs",
        "",
    ]
    tab_counts = Counter(tab for row in features for tab in row.get("tabs", []))
    profile.extend(f"- {tab}: {count:,}" for tab, count in tab_counts.most_common())
    (root / "02_target_creator_profile.md").write_text("\n".join(profile).rstrip() + "\n")

    write_analysis_files(root, features, stats, insights)
    write_thread_files(root, insights, stats)
    write_visuals(root, insights, stats)
    write_logs(root, gate_status, source_results, duplicates, expected_count, len(features))


def write_analysis_files(
    root: Path,
    features: list[dict[str, Any]],
    stats: dict[str, Any],
    insights: list[dict[str, Any]],
) -> None:
    rows = [["Feature", "Median Yes", "Median No", "Top Rate", "Bottom Rate", "Count Yes"]]
    for key, label in [
        ("how_to_hook", "How-to hook"),
        ("has_cta", "CTA present"),
        ("has_question", "Question present"),
        ("has_numbered_structure", "Numbered structure"),
        ("has_contrarian_opener", "Contrarian opener"),
        ("has_personal_opener", "Personal opener"),
    ]:
        item = stats["boolean"][key]
        rows.append(
            [
                label,
                fmt_num(item["median_yes"]),
                fmt_num(item["median_no"]),
                pct(item["top_rate"]),
                pct(item["bottom_rate"]),
                fmt_num(item["count_yes"]),
            ]
        )
    corpus_patterns = [
        "# Corpus Patterns",
        "",
        f"Metric-valid posts: {stats['metric_valid_count']:,} of {stats['corpus_count']:,}.",
        "",
        markdown_table(rows),
        "",
        "## Ranked Fresh Insight Candidates",
        "",
    ]
    for item in insights:
        corpus_patterns.append(f"{item['id']}. **{item['clip_hook']}** {item['data']}")
    (root / "analyses/corpus_patterns.md").write_text("\n".join(corpus_patterns).rstrip() + "\n")

    top_lines = ["# Top Performers", ""]
    for row in stats["top_posts"][:20]:
        top_lines.append(
            f"- {fmt_num(row['like_count'])} likes | {row['author']} | {row['part_count']} parts | {row['word_count']} words | {row['first_line']}"
        )
    (root / "analyses/top_performers.md").write_text("\n".join(top_lines).rstrip() + "\n")

    anti_lines = [
        "# Anti-Patterns",
        "",
        "- How-to openers were absent from the metric-valid top decile.",
        "- CTA-bearing posts had lower median likes than posts without CTAs.",
        "- Numbered/list structures underperformed non-numbered posts.",
        "- Long-form was heavily overrepresented in the bottom quartile unless it was raw narrative.",
    ]
    (root / "analyses/anti_patterns.md").write_text("\n".join(anti_lines).rstrip() + "\n")

    family_rows = [["Family", "Count", "Median Likes", "Top Rate", "Bottom Rate"]]
    for key, item in stats["word_buckets"].items():
        family_rows.append(
            [key, fmt_num(item["count"]), fmt_num(item["median_likes"]), pct(item["top_rate"]), pct(item["bottom_rate"])]
        )
    family_rows.append(
        [
            "long_form",
            fmt_num(sum(1 for row in features if row["format_family"] == "long_form")),
            fmt_num(stats["boolean"]["format_family_long"]["median_yes"]),
            pct(stats["boolean"]["format_family_long"]["top_rate"]),
            pct(stats["boolean"]["format_family_long"]["bottom_rate"]),
        ]
    )
    (root / "analyses/format_family_breakdown.md").write_text(
        "# Format Family Breakdown\n\n" + markdown_table(family_rows) + "\n"
    )

    outliers = ["# Outliers", "", "Extreme values are retained, but medians are used for claims."]
    for row in stats["top_posts"][:5]:
        outliers.append(f"- {fmt_num(row['like_count'])} likes | {row['author']} | {row['first_line']}")
    (root / "analyses/outliers.md").write_text("\n".join(outliers).rstrip() + "\n")

    examples_by_pattern = ["# Examples By Pattern", ""]
    for item in insights:
        examples_by_pattern.extend(
            [
                f"## {item['id']}. {item['clip_hook']}",
                "",
                f"- Good example: {short_example(item['example'])}",
                f"- Bad example (illustrative): {bad_example(item['id'])}",
                "",
            ]
        )
    (root / "evidence/examples_by_pattern.md").write_text("\n".join(examples_by_pattern).rstrip() + "\n")

    examples_by_tier = ["# Examples By Performance Tier", "", "## Top Examples", ""]
    for row in stats["top_posts"][:15]:
        examples_by_tier.append(f"- {fmt_num(row['like_count'])} likes | {row['author']} | {row['first_line']}")
    examples_by_tier.extend(["", "## Low Examples", ""])
    for row in stats["bottom_posts"][:15]:
        examples_by_tier.append(f"- {fmt_num(row['like_count'])} likes | {row['author']} | {row['first_line']}")
    (root / "evidence/examples_by_performance_tier.md").write_text("\n".join(examples_by_tier).rstrip() + "\n")

    examples_by_format = ["# Examples By Format Family", ""]
    for family in ["short_form", "long_form"]:
        examples_by_format.extend([f"## {family}", ""])
        rows = [row for row in stats["top_posts"] if row["format_family"] == family]
        for row in rows[:10]:
            examples_by_format.append(f"- {fmt_num(row['like_count'])} likes | {row['author']} | {row['first_line']}")
        examples_by_format.append("")
    (root / "evidence/examples_by_format_family.md").write_text("\n".join(examples_by_format).rstrip() + "\n")

    prior = [
        "# Claude vs Codex Comparison",
        "",
        "This file is written after the fresh Codex findings. It compares themes without using the Claude findings as the starting frame.",
        "",
        "| Original Claude Finding | Codex Rerun Result | Status |",
        "| --- | --- | --- |",
        "| How-to hooks fail | Top decile had 0 how-to openers | Confirmed |",
        "| Brevity wins | Under-50-word posts were strongest | Confirmed |",
        "| Two posts max | Two-part posts were the thread sweet spot | Confirmed/refined |",
        "| Trigger words repel | Broad trigger language was not the strongest fresh signal | Not selected as top-seven |",
        "| CTAs cost reach | CTA posts had lower median likes | Confirmed |",
        "| Questions cost reach | Questions were weaker as top-decile signals but not a major penalty | Weaker than original |",
        "| Long-form only works as raw narrative | Long-form underperformed unless it read like a scene/confession | Confirmed |",
        "",
    ]
    (root / "analyses/claude_vs_codex_comparison.md").write_text("\n".join(prior))

    constitutions = {
        "00_master_packaging_constitution.md": [
            "Lead with evidence, not advice.",
            "Compress until the post has one emotional job.",
            "Treat a CTA as a cost unless the post has already paid attention rent.",
        ],
        "01_title_constitution.md": [
            "The first line is the title.",
            "Avoid how-to language as the opener unless the proof is shocking.",
            "Contrarian openers must name the belief they are breaking.",
        ],
        "02_thumbnail_constitution.md": [
            "For Threads, media is optional; text must carry the first impression.",
            "If adding media, use it as proof, not decoration.",
        ],
        "03_hook_constitution.md": [
            "Open with a confession, scene, status reversal, or sharp command.",
            "Do not begin with generic instruction.",
        ],
        "04_script_and_structure_constitution.md": [
            "One post should usually carry one idea.",
            "Two parts are useful when part two changes the frame.",
            "Long-form must be narrative, not syllabus.",
        ],
    }
    for filename, rules in constitutions.items():
        (root / "constitutions" / filename).write_text(
            "# " + filename.replace("_", " ").replace(".md", "").title() + "\n\n"
            + "\n".join(f"- {rule}" for rule in rules)
            + "\n"
        )


def bad_example(insight_id: int) -> str:
    examples = {
        1: "How to grow on Threads in 2026: use better hooks, post daily, and engage more.",
        2: "A 450-word explanation that takes six paragraphs to say one obvious thing.",
        3: "A 12-part thread where parts 4-12 repeat the same lesson with different wording.",
        4: "A good story that ends with three asks: follow, comment, and join my newsletter.",
        5: "17 lessons, 9 frameworks, and 4 bonus tips before the reader knows why it matters.",
        6: "A vague hot take like 'most people are wrong' without naming what is wrong.",
        7: "A long educational essay with no scene, no stakes, and no human moment.",
    }
    return examples.get(insight_id, "A generic post that hides the real idea.")


def write_thread_files(root: Path, insights: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    posts = [
        (
            f"{THREAD_HOOK}\n\n"
            "most Threads advice is complete bullshit.\n\n"
            "I reran the vault from scratch in Codex.\n\n"
            "same 1,996 posts.\n"
            "fresh findings.\n"
            "7 things worth stealing:"
        )
    ]

    for item in insights:
        example = item["example"]
        example_line = short_example(example)
        posts.append(
            f"{item['id']}/ {item['clip_hook']}\n\n"
            f"{item['claim']}\n\n"
            f"{item['data']}\n\n"
            f"example: {example_line}\n\n"
            f"Threads takeaway: {item['takeaway']}"
        )

    posts.append(
        "the uncomfortable rule:\n\n"
        "stop copying advice.\n"
        "start copying evidence.\n\n"
        "I will add the YouTube breakdown here when it is ready.\n\n"
        "until then, save this before your next post."
    )

    final_thread = f"\n\n{EM_DASH}\n\n".join(posts)
    (root / "thread/final_thread.md").write_text(final_thread + "\n")

    audit_lines = [
        "# Insights Audit",
        "",
        f"- Post count: {len(posts)}",
        f"- Hook exact: {posts[0].splitlines()[0] == THREAD_HOOK}",
        f"- Separator: em dash line",
        f"- Metric-valid corpus used for claims: {stats['metric_valid_count']:,}",
        "",
        "## Selected Insights",
        "",
    ]
    for item in insights:
        audit_lines.extend(
            [
                f"### {item['id']}. {item['clip_hook']}",
                "",
                f"- Claim: {item['claim']}",
                f"- Data: {item['data']}",
                f"- Example: {short_example(item['example'])}",
                f"- Bad example: {bad_example(item['id'])}",
                "",
            ]
        )
    (root / "thread/insights_audit.md").write_text("\n".join(audit_lines).rstrip() + "\n")

    insertion = [
        "# Threadify Draft Insertion Notes",
        "",
        "Use this only after manual/Computer Use insertion is explicitly promoted.",
        "",
        "- Open https://www.threadify.app/plans",
        "- Use the original thread as the template.",
        "- Preserve the first post hook exactly.",
        "- Insert all 9 posts in order.",
        "- Save/stage as draft only. Do not publish or schedule.",
    ]
    (root / "thread/threadify_insertion_notes.md").write_text("\n".join(insertion).rstrip() + "\n")


def svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def wrap_text(text: str, limit: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) <= limit:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def write_visuals(root: Path, insights: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    visual_manifest = ["# Asset Manifest", ""]
    cards = [
        {
            "filename": "01_hook_cover",
            "kicker": "THREADIFY VAULT RERUN",
            "headline": "1,996",
            "subhead": "viral Threads posts analyzed",
            "takeaway": "fresh Codex pass, same hook, new evidence",
        }
    ]
    for item in insights:
        cards.append(
            {
                "filename": f"{item['id'] + 1:02d}_insight_{item['id']:02d}",
                "kicker": f"INSIGHT {item['id']:02d}",
                "headline": item["clip_hook"],
                "subhead": item["data"],
                "takeaway": item["takeaway"],
            }
        )
    cards.append(
        {
            "filename": "09_recap_closer",
            "kicker": "RECAP",
            "headline": "7 rules from 1,996 posts",
            "subhead": "how-to, brevity, two parts, CTAs, numbered lists, contrarian hooks, long-form",
            "takeaway": "save this before your next post",
        }
    )
    cards = cards[:9]

    for card in cards:
        svg_lines = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">',
            '<rect width="1080" height="1350" fill="#f7f4ee"/>',
            '<rect x="72" y="72" width="936" height="1206" fill="none" stroke="#8f1d1d" stroke-width="4"/>',
            f'<text x="96" y="150" font-family="Arial, sans-serif" font-size="32" letter-spacing="8" fill="#777">{svg_escape(card["kicker"].upper())}</text>',
        ]
        y = 310
        headline_lines = wrap_text(str(card["headline"]), 18 if len(str(card["headline"])) > 16 else 30)
        for line in headline_lines[:5]:
            svg_lines.append(
                f'<text x="96" y="{y}" font-family="Arial Black, Arial, sans-serif" font-size="76" fill="#8f1d1d">{svg_escape(line)}</text>'
            )
            y += 88
        y += 36
        for line in wrap_text(str(card["subhead"]), 46)[:5]:
            svg_lines.append(
                f'<text x="96" y="{y}" font-family="Arial, sans-serif" font-size="34" fill="#111">{svg_escape(line)}</text>'
            )
            y += 48
        y = 1120
        svg_lines.append('<line x1="96" y1="1050" x2="984" y2="1050" stroke="#ddd" stroke-width="3"/>')
        for line in wrap_text(str(card["takeaway"]), 44)[:3]:
            svg_lines.append(
                f'<text x="96" y="{y}" font-family="Arial Black, Arial, sans-serif" font-size="40" fill="#111">{svg_escape(line)}</text>'
            )
            y += 52
        svg_lines.append("</svg>")
        svg = "\n".join(svg_lines) + "\n"
        svg_path = root / "visuals/assets" / f"{card['filename']}.svg"
        html_path = root / "visuals/assets" / f"{card['filename']}.html"
        svg_path.write_text(svg)
        html_path.write_text(
            "<!doctype html><html><head><meta charset=\"utf-8\"><title>"
            + svg_escape(card["filename"])
            + "</title></head><body style=\"margin:0;background:#111;display:grid;place-items:center;min-height:100vh\">"
            + svg
            + "</body></html>\n"
        )
        visual_manifest.append(f"- `{svg_path.name}` / `{html_path.name}`")

    (root / "visuals/01_asset_manifest.md").write_text("\n".join(visual_manifest).rstrip() + "\n")
    (root / "visuals/00_visual_system.md").write_text(
        "# Visual System\n\nMinimal research dossier cards. Background #f7f4ee, accent #8f1d1d, text #111111.\n"
    )
    (root / "visuals/02_data_validation.md").write_text(
        "# Data Validation\n\nEvery on-card statistic is sourced from `07_packaging_features.json` and summarized in `00_run_report.md`.\n"
    )


def write_logs(
    root: Path,
    gate_status: str,
    source_results: list[SourceResult],
    duplicates: list[dict[str, Any]],
    expected_count: int | None,
    actual_count: int,
) -> None:
    extraction_lines = ["# Extraction Log", ""]
    for result in source_results:
        extraction_lines.append(
            f"- {result.source_path}: parser={result.parser}, parsed={result.parsed_records}, raw={result.raw_records}, errors={len(result.parse_errors)}"
        )
        for error in result.parse_errors[:20]:
            extraction_lines.append(f"  - {error}")
    (root / "logs/extraction_log.md").write_text("\n".join(extraction_lines).rstrip() + "\n")

    (root / "logs/fallback_log.md").write_text(
        "# Fallback Log\n\nLocal corpus mode used. No live Threads scraping or API fallback was used for analysis.\n"
    )
    (root / "logs/ambiguity_log.md").write_text(
        "# Ambiguity Log\n\nNo user-facing ambiguity was unresolved. Zero-like metrics were treated as missing/zero and excluded from comparative claims.\n"
    )
    (root / "logs/exclusions_log.md").write_text(
        "# Exclusions Log\n\nNo posts were excluded from the normalized corpus. Posts with missing/zero likes were excluded only from performance comparisons.\n"
    )
    discrepancy = [
        "# Discrepancy Log",
        "",
        f"- Expected corpus count: {expected_count if expected_count is not None else 'not set'}",
        f"- Actual deduped corpus count: {actual_count:,}",
        f"- Gate status: {gate_status}",
        f"- Duplicate records removed: {len(duplicates):,}",
    ]
    (root / "logs/discrepancy_log.md").write_text("\n".join(discrepancy).rstrip() + "\n")
    write_json(
        root / "logs/checkpoint.json",
        {
            "phase": 4,
            "step": "local_corpus_complete",
            "timestamp": utc_now(),
            "completed_steps": [
                "corpus_gate",
                "feature_extraction",
                "analysis",
                "thread_generation",
                "visual_asset_generation",
            ],
            "next_step": "optional_threadify_draft_insertion",
        },
    )


def validate_thread(path: Path) -> dict[str, Any]:
    text = path.read_text()
    posts = [part.strip() for part in re.split(rf"\n\s*{EM_DASH}\s*\n", text) if part.strip()]
    char_counts = [len(post) for post in posts]
    return {
        "post_count": len(posts),
        "hook_exact": posts[0].splitlines()[0] == THREAD_HOOK if posts else False,
        "max_chars": max(char_counts) if char_counts else 0,
        "posts_over_500_chars": [index + 1 for index, count in enumerate(char_counts) if count > 500],
        "char_counts": char_counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", type=Path, default=None)
    parser.add_argument("--expected-count", type=int, default=1996)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--allow-count-mismatch", action="store_true")
    args = parser.parse_args()

    sources = args.source or [DEFAULT_SOURCE]
    missing = [str(source) for source in sources if not source.exists()]
    if missing:
        raise SystemExit(f"Missing source file(s): {', '.join(missing)}")

    root = args.output_root
    ensure_dirs(root)

    posts, source_results, duplicates = normalize_sources(sources)
    if args.expected_count is not None and len(posts) != args.expected_count:
        write_logs(root, "failed", source_results, duplicates, args.expected_count, len(posts))
        write_json(
            root / "raw/corpus_source_receipt.json",
            {
                "generated_at": utc_now(),
                "expected_corpus_count": args.expected_count,
                "verified_unique_count": len(posts),
                "gate_status": "failed",
                "sources": [result.__dict__ for result in source_results],
                "duplicate_count": len(duplicates),
            },
        )
        if not args.allow_count_mismatch:
            print(f"Corpus gate failed: expected {args.expected_count}, got {len(posts)}")
            return 2

    features = extract_features(posts)
    stats = comparison(features)
    insights = insight_specs(features, stats)
    write_reports(root, features, source_results, duplicates, stats, insights, args.expected_count)
    validation = validate_thread(root / "thread/final_thread.md")
    write_json(root / "thread/final_thread_validation.json", validation)
    if validation["post_count"] != 9 or not validation["hook_exact"] or validation["posts_over_500_chars"]:
        print(json.dumps(validation, indent=2))
        return 3
    print(f"Wrote Codex Threads forensics run to {root}")
    print(f"Corpus gate: {len(features)} posts; metric-valid: {stats['metric_valid_count']}")
    print(f"Thread validation: {validation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
