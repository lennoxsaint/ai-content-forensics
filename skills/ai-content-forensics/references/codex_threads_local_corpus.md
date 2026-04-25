# Codex Threads Local Corpus Mode

Use this reference when `target_platform=threads` and `input_mode=local_corpus`.

## Purpose

Analyze an already-exported Threads corpus without live scraping. This is the preferred Codex pathway for Threadify vault research because the output is repeatable, auditable, and safe to rerun.

## Required Gate

Before making findings, prove the corpus:

1. Read every path in `corpus_files`.
2. Normalize every candidate post into one schema.
3. Dedupe by URL/source ID first, then normalized author + body hash.
4. Write a corpus receipt.
5. If `expected_corpus_count` is set and the verified unique count differs, stop. Write `logs/discrepancy_log.md` and do not generate findings, visuals, or Threadify drafts.

For the Threadify vault 1,996-post rerun, the preferred file is:

```
/Users/lennoxsaint/swipefile/vault-extract/THREADIFY VAULT EXTRACT 060426.jsonl
```

That export has 1,996 record starts and one malformed multi-line JSON record. The Codex runner must split on record boundaries and repair raw embedded newlines before parsing.

## Deterministic Runner

Prefer the bundled script:

```
python3 {SKILL_ROOT}/ai-content-forensics/scripts/run_threads_local_forensics.py \
  --source "/Users/lennoxsaint/swipefile/vault-extract/THREADIFY VAULT EXTRACT 060426.jsonl" \
  --expected-count 1996 \
  --output-root "/Users/lennoxsaint/content-pipeline/2026-04-21-threads-growth-is-a-lie/research/threads-packaging/threadify-vault-1996-codex"
```

The script writes:

- corpus receipt and methodology
- normalized post index
- extracted feature table
- analyses, evidence, constitutions, and logs
- a finished 9-post thread
- simple SVG/HTML carousel assets

## Analysis Rules

- Treat posts with missing or zero likes as included in the corpus but excluded from comparative performance claims.
- Use medians and top/bottom tier rates for claims; call out extreme outliers separately.
- Do not use any prior Claude findings as the starting frame. Compare against prior findings only after the fresh findings file exists.
- Every number in the thread must trace to `06_packaging_features.csv` or `07_packaging_features.json`.

## Threadify Draft Rule

Computer Use is allowed only after the corpus gate and thread validation pass. Insert the final thread into Threadify as a draft/template only. Do not publish, schedule, or overwrite a live post.
