# VTuber Voice Progress

Last updated: 2026-05-24

## Current Position

The VTuber work is the active research lane in this repository. The repo is
still named `arti6_linearvc`, so the split is currently a soft workspace split:

- `vtuber_pipeline/` is the canonical code path for VTuber data curation.
- `projects/vtuber_voice/` records lane-level status and future split points.
- `arti6_linearvc_demo/` remains the ARTI-6 + LinearVC demo lane.
- Physical migration into `projects/vtuber/` should wait until the current data
  scripts and manifests are stable, because active commands still reference
  `vtuber_pipeline/` and `data/`.

## Repository And Harness

- Private GitHub remote is configured as `origin`.
- Code/docs/Trellis notes sync through git.
- Large generated data stays outside git.
- Trellis package metadata now distinguishes:
  - `vtuber_pipeline`
  - `arti6_demo`
  - `trellis_harness`
- Antigravity support exists under `.agent/` and the local CLI adapter supports
  `agy --print` / `agy --conversation`.

## Data Handling Policy

Segmentation outputs stay as normal directories by default so audio can be
previewed directly on the server.

Do not create persistent archives for VTuber segmentation outputs unless the user
explicitly asks for transfer packaging or a portable demo/report bundle.

Use these distinctions:

- **Previewable data directory**: default for curated audio, manifests, stems,
  and review buckets.
- **Temporary transfer archive**: allowed when moving a large folder between
  machines and direct `rsync` is not convenient.
- **Portable demo bundle**: allowed for HTML reports/demos that need `index.html`
  plus linked audio/assets in one downloadable unit.

## Current Generated Data

The latest conservative segmentation run is:

```text
data/vtuber_curated_conservative_20260524_run2/
```

This is an expanded directory, not an archive.

Validation:

```text
manifest rows: 241
wav files: 241
summary segments: 241
zero-byte wavs: 0
duration range: 3.100-15.000 sec
mean duration: 9.310 sec
skipped long sources: 20
directory size: 379M
```

Status counts:

```text
clean_candidate: 92
review: 101
quarantine: 48
```

Breakdown:

```text
clean_candidate/Enna/EN_Singing: 43
clean_candidate/Kiara/EN_JP_DE_Talking: 6
clean_candidate/Kiara/EN_Singing: 28
clean_candidate/Mori/EN_JP_Singing: 15
quarantine/FuwaMoco/EN_JP_Singing: 48
review/Enna/EN_Talking: 10
review/Mori/EN_JP_Talking: 91
```

## Listening Notes So Far

- Singing segmentation is better than the earlier ASR/linguistic-content cut.
- BGM-only spans are mostly removed while musical phrasing is less aggressively
  chopped.
- Reverb, backing vocals, and harmonies remain; this is acceptable for the
  current consistent-source setting, but it is not dry vocal ground truth.
- Kiara shorts still have unreliable language/domain labels; some Japanese song
  material is labeled as English and some clips are non-linguistic murmuring.
- Mori talking remains `review` because several videos may include multiple
  speakers.

## Recommended Next Steps

1. Preview `clean_candidate/` first on the server, especially Enna and Mori
   singing.
2. Treat `review/` as usable only after manual or automated speaker checks.
3. Keep `quarantine/` out of training unless a later task creates a clear rescue
   policy.
4. Add a Kiara language/domain cleanup pass before using Kiara clips as language
   evidence.
5. Add diarization or target-speaker verification before using long talking
   streams.
6. Defer physical project-path migration until the VTuber data-flow scripts are
   stable and documented.
