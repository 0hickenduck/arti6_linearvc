# VTuber Progress Docs and Data Packaging Policy

## Goal

Document the current VTuber project progress and correct the data handling
policy so future agents keep segmentation outputs as previewable directories by
default instead of packaging them into archives.

## What I Already Know

* The user can preview audio files directly on the server and does not want
  segmentation outputs compressed by default.
* Compression is useful only as a temporary transfer convenience or when bundling
  HTML demos with linked assets.
* Code sync now goes through GitHub pull/push, so ordinary project docs and code
  do not need archive bundles.
* Current VTuber segmentation output is
  `data/vtuber_curated_conservative_20260524_run2/`, a normal directory.
* The repo already has a soft project split with `projects/vtuber_voice/`,
  `projects/arti6_linearvc/`, and `projects/trellis_harness/`.

## Requirements

* Add a concise progress document for the VTuber lane.
* Update sync documentation to state that generated audio datasets stay
  expanded and previewable by default.
* Update VTuber README wording so the legacy `.tar.gz` agent path does not look
  like the recommended current workflow.
* Preserve the distinction between:
  * expanded data directories for server preview,
  * temporary transfer archives,
  * portable demo/report bundles.

## Acceptance Criteria

* [ ] The VTuber lane has a current progress doc.
* [ ] Documentation says not to compress segmentation output by default.
* [ ] Documentation still allows temporary archives for transfer/demo bundles.
* [ ] Current run output path and status counts are recorded.
* [ ] Git status excludes generated `data/` audio from commits.

## Out Of Scope

* Changing segmentation code.
* Moving directories into `projects/`.
* Creating or deleting data archives.
* Uploading or pushing generated data.
