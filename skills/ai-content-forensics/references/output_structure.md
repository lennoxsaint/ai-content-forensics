# Output Folder Structure

All output goes into a single folder named after the target creator. The folder name depends on `target_platform`:

```
research/youtube-packaging/{creator-slug}/        # when target_platform=youtube (default)
research/threads-packaging/{creator-slug}/        # when target_platform=threads
```

Where `{creator-slug}` is a lowercase, hyphenated version of the creator's name or handle (e.g., `ali-abdaal`, `alex-hormozi`, `lennox-saint`). Strip the leading `@` from Threads handles before slugging.

If `output_root` is provided, use that absolute path exactly and keep the layout below inside it.

## Complete Layout

```
research/youtube-packaging/{creator-slug}/
│
├── 00_run_report.md                        # Progress log and final summary
├── 01_reference_channel_profile.md         # Only if your_channel_handle provided
├── 02_target_creator_profile.md            # Creator classification and overview
├── 03_methodology.md                       # Data collection methods and paths used
├── 04_video_index.csv                      # All qualifying videos with key metadata
├── 05_video_index.json                     # Same data in JSON format
├── 06_packaging_features.csv               # Extracted features per video
├── 07_packaging_features.json              # Same data in JSON format
├── 08_portability_matrix.csv               # Only if your_channel_handle provided
├── 09_portability_matrix.json              # Only if your_channel_handle provided
├── 10_exhaustive_synthesis.md              # Comprehensive findings + 15+ ranked insights
│
├── raw/                                    # Unprocessed data as collected
│   ├── api/                                # Raw API responses
│   ├── metadata/                           # Raw metadata files
│   ├── transcripts/                        # Raw transcript files
│   └── thumbnails/                         # Downloaded thumbnail images
│
├── normalized/                             # Cleaned, per-video dossiers
│   └── videos/
│       └── {video_id}/
│           ├── metadata.json               # Structured video metadata
│           ├── transcript.txt              # Full transcript text
│           ├── thumbnail.jpg               # Thumbnail image
│           └── notes.md                    # Per-video analysis notes
│
├── analyses/                               # Pattern analysis reports
│   ├── corpus_patterns.md                  # Cross-cutting patterns
│   ├── title_patterns.md                   # Title-specific patterns
│   ├── thumbnail_patterns.md               # Thumbnail-specific patterns
│   ├── hook_patterns.md                    # Hook/opening patterns
│   ├── structure_patterns.md               # Script/structure patterns
│   ├── format_family_breakdown.md          # Analysis by content format type
│   ├── top_performers.md                   # Top vs bottom comparison
│   ├── anti_patterns.md                    # What doesn't work
│   ├── outliers.md                         # Notable exceptions
│   └── portability.md                      # Only if your_channel_handle provided
│
├── constitutions/                          # Operational rule sets
│   ├── 00_master_packaging_constitution.md # Overview + cross-cutting rules
│   ├── 01_title_constitution.md            # Title rules
│   ├── 02_thumbnail_constitution.md        # Thumbnail rules
│   ├── 03_hook_constitution.md             # Hook/opening rules
│   └── 04_script_and_structure_constitution.md  # Script/structure rules
│
├── evidence/                               # Supporting examples
│   ├── examples_by_pattern.md              # Grouped by discovered pattern
│   ├── examples_by_performance_tier.md     # Grouped by performance
│   └── examples_by_format_family.md        # Grouped by content type
│
├── thread/                                 # Final thread output (skipped in research_only mode)
│   ├── final_thread.md                     # Copy-paste-ready 9-post thread
│   └── insights_audit.md                   # Insight selection rationale + runner-ups
│
├── visuals/                                # Production-ready carousel assets (full mode only)
│   ├── 00_visual_system.md                 # Palette, typography, spacing rules
│   ├── 01_asset_manifest.md                # Per-asset: paths, data sources, copy
│   ├── 02_data_validation.md               # Every number traced to source
│   ├── assets/                             # Final visual files
│   │   ├── 01_hook_cover.svg
│   │   ├── 01_hook_cover.html
│   │   ├── 02_insight_01.svg
│   │   ├── 02_insight_01.html
│   │   ├── ...
│   │   ├── 09_recap_closer.svg
│   │   └── 09_recap_closer.html
│   └── previews/                           # PNG renders (if available)
│       ├── 01_hook_cover.png
│       ├── ...
│       └── 09_recap_closer.png
│
└── logs/                                   # Operational logs
    ├── extraction_log.md                   # What was extracted and how
    ├── fallback_log.md                     # Which fallback paths were used
    ├── ambiguity_log.md                    # Ambiguous data points and resolutions
    ├── exclusions_log.md                   # Videos excluded and why
    ├── discrepancy_log.md                  # Data conflicts and corrections
    └── checkpoint.json                     # Resume point if interrupted
```

## Conditional Files

Several files are only created when the user provides their own reference handle:

- `01_reference_channel_profile.md` — YouTube: when `your_channel_handle` provided. Threads: when `your_threads_handle` provided.
- `08_portability_matrix.csv` / `.json`
- `analyses/portability.md`

If no reference is provided, skip these entirely. Do not create empty placeholder files.

## Threads Pathway Specifics

When `target_platform=threads`, the file numbering stays identical but the content is Threads-native:

- `02_target_creator_profile.md` — profile classification per Threads axes (post format mix, media profile, origination, intent, positioning — see `phase1_threads_research.md` Step 2).
- `04_video_index.csv` / `.json` → rename conceptually to "post index" but keep file names the same for downstream-tool compatibility. Columns swap: video URL → post permalink, video ID → post ID, duration → word count, etc. Per-field mapping is documented in `phase1_threads_research.md` Step 5 "Corpus Schema Parity".
- `06_packaging_features.csv` / `.json` → same schema shape, Threads-specific columns (post_type, thread_position, cta_presence, question_presence, trigger_density, has_media).

### Local Corpus Mode Additions

When `input_mode=local_corpus`, also write:

- `raw/corpus_source_receipt.json` — source paths, parse status, raw candidate count, deduped count, expected-count gate result.
- `normalized/threads_corpus.json` — full normalized corpus in one file.
- `logs/discrepancy_log.md` — required when the expected-count gate fails; otherwise note that the gate passed.

Posts with missing or zero like counts remain in the normalized corpus, but comparative performance claims must use the metric-valid subset and report that subset size.

### Excluded columns (not available for Threads)

These YouTube-specific columns are omitted from Threads corpus files — do not emit empty columns:
- Thumbnail visual analysis (face presence, contrast, focal clarity, visual metaphor)
- Transcript (replaced by full post `text`)
- Chapter timestamps
- Duration in seconds (replaced by `word_count`)

### Missing metric: `saves`

The Threads API does not expose a `saves` metric. Do not fabricate one. If any downstream code references YouTube "saves", leave it null for Threads runs.

### Constitutions folder (Threads)

The 5-file structure stays the same, but file names adapt to the Threads equivalents from `phase1_threads_research.md` Step 7:

- `00_master_packaging_constitution.md` (Threads master — same shape, Threads-native rules)
- `01_title_constitution.md` → populated as the Opener constitution (file name stays for compatibility; content governs the first 140 chars of Threads posts)
- `02_thumbnail_constitution.md` → populated as the Media-use constitution (when to attach image/video/carousel vs text-only)
- `03_hook_constitution.md` → populated as the first-line / hook-opener constitution
- `04_script_and_structure_constitution.md` → populated as the Post-structure + CTA-and-engagement constitution (combines what YouTube split across two files)

File names intentionally remain stable so downstream consumers (Phase 2 / Phase 3) read the same paths regardless of target platform.

## Output Mode Variations

- **`research_only`**: Creates everything above EXCEPT the `thread/` and `visuals/` directories
- **`thread_only`**: Creates everything above EXCEPT the `visuals/` directory
- **`full`**: Creates the complete structure above
