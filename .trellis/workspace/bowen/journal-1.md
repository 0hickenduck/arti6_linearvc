# Journal - bowen (Part 1)

> AI development session journal
> Started: 2026-05-15

---



## Session 1: Repo Structure and Trellis Harness Audit

**Date**: 2026-05-15
**Task**: Repo Structure and Trellis Harness Audit
**Branch**: `master`

### Summary

Reviewed the Trellis harness setup, migrated legacy research notes, cleaned up obsolete state files, and initialized the main arti6_linearvc_demo workspace.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `e875579` | (see git log) |
| `a86189c` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 2: Create ARTI-6 & LinearVC Conceptual Report

**Date**: 2026-05-19
**Task**: Create ARTI-6 & LinearVC Conceptual Report

### Summary

Created a comprehensive conceptual report explaining the ARTI-6 articulation model and LinearVC approach using the piano/pianist analogy. Clarified the 6 audio conditions in the floor experiment to bridge philosophy and technical implementation.

### Main Changes

(Add details)

### Git Commits

(No commits - planning session)

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 3: Environment Setup: Antigravity CLI and Git

**Date**: 2026-05-23
**Task**: Environment Setup: Antigravity CLI and Git
**Branch**: `master`

### Summary

Installed Antigravity CLI (agy) and successfully configured the Git repository by performing an initial commit with local user info.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `0383364` | (see git log) |
| `fb82a36` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 4: Planning YouTube VTuber Cross-Domain Dataset Pipeline

**Date**: 2026-05-23
**Task**: Planning YouTube VTuber Cross-Domain Dataset Pipeline
**Branch**: `master`

### Summary

Discussed the philosophy of timbre vs prosody in Voice Conversion. Agreed on a weakly-supervised VTuber dataset pipeline. Wrote the PRD and Implementation Plan for the micro-probe scraper and purifier.

### Main Changes

(Add details)

### Git Commits

(No commits - planning session)

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 5: Bulk Task Cleanup

**Date**: 2026-05-23
**Task**: Bulk Task Cleanup
**Branch**: `master`

### Summary

Archived 9 active tasks, including marking 'AI User Presentation' and 'Gemini Agent Routing' as UNFINISHED. The active task list is now focused on the VTuber Dataset Pipeline.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `e68540f` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 6: Gemini CLI VTuber Audio Extraction Workplan

**Date**: 2026-05-23
**Task**: Gemini CLI VTuber Audio Extraction Workplan
**Branch**: `master`

### Summary

Created the Gemini CLI handoff plan for VTuber audio extraction, including metadata selection, audio cleaning, chunking, and final assembly steps.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `5b63f87` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 7: Implement VTuber Dataset Pipeline (POC)

**Date**: 2026-05-23
**Task**: Implement VTuber Dataset Pipeline (POC)
**Branch**: `master`

### Summary

Implemented a rate-limit-safe YouTube audio scraper and a Demucs+SileroVAD audio purifier. Established the 'VTuber Dataset Pipeline Scripts' scenario in backend specs. Verified the pipeline with local test data (01_source_singing.wav) and smoke-tested the scraper's metadata extraction.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `21834d7` | (see git log) |
| `47ddd97` | (see git log) |
| `c9b4502` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 8: Refactor Repository Structure

**Date**: 2026-05-23
**Task**: Refactor Repository Structure
**Branch**: `master`

### Summary

Separated the legacy arti6_linearvc demo project and the new VTuber dataset pipeline into distinct root-level directories. Moved vtuber-related scripts and test files to the vtuber_pipeline folder and updated backend specs.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `44e9fa4` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 9: VTuber Video Discovery Agent

**Date**: 2026-05-23
**Task**: VTuber Video Discovery Agent
**Branch**: `master`

### Summary

Designed and implemented an LLM-based discovery agent (discover_videos.py) using Gemini Flash to dynamically fetch and categorize VTuber streams (Zatsudan vs Karaoke), with explicit handling for twin streams like FuwaMoco. Upgraded scraper to consume the agent's manifest.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `724b4ed` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 10: VTuber Local Agent Orchestrator

**Date**: 2026-05-23
**Task**: VTuber Local Agent Orchestrator
**Branch**: `master`

### Summary

Created an end-to-end local_agent.py orchestrator that chains discovery, scraping, and purifying. It automatically compresses the result into a tar.gz and uploads it to a remote server using SCP/SSH configured via environment variables. Wrote a detailed README for user deployment.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `b50072b` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 11: GitHub sync, Antigravity harness, and VTuber curation

**Date**: 2026-05-24
**Task**: GitHub sync, Antigravity harness, and VTuber curation
**Package**: vtuber_pipeline
**Branch**: `master`

### Summary

Configured GitHub-safe sync and submodule metadata, added Antigravity workflows/skills plus agy CLI adapter support, documented workspace project lanes, and added a conservative existing-WAV VTuber curation pass with listening feedback recorded.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `f5decfb` | (see git log) |
| `1f91549` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 12: VTuber conservative segmentation run

**Date**: 2026-05-24
**Task**: VTuber conservative segmentation run
**Package**: vtuber_pipeline
**Branch**: `master`

### Summary

Ran conservative existing-WAV VTuber segmentation into data/vtuber_curated_conservative_20260524_run2, preserving prior output; validated 241 manifest rows, 241 WAVs, zero zero-byte files, and 20 long sources skipped for later diarization/verification.

### Main Changes

(Add details)

### Git Commits

(No commits - planning session)

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 13: VTuber progress docs and packaging policy

**Date**: 2026-05-24
**Task**: VTuber progress docs and packaging policy
**Package**: vtuber_pipeline
**Branch**: `master`

### Summary

Documented current VTuber lane progress, clarified that segmentation outputs remain expanded directories for server preview by default, and limited archives to explicit transfer or portable demo/report bundle cases.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `ab12b1f` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 14: Write midterm research handoff report

**Date**: 2026-05-24
**Task**: Write midterm research handoff report
**Package**: vtuber_pipeline
**Branch**: `master`

### Summary

Compiled a comprehensive Mid-Term Research Handoff Report summarizing the journey from ARTI-6 Linear VC to Seed-VC, and detailing the data pipeline curation phases, data metrics, and future roadmap.

### Main Changes

(Add details)

### Git Commits

(No commits - planning session)

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 15: Complete Version 3 VTuber Data Pipeline & Unlocked Speech Dataset

**Date**: 2026-05-24
**Task**: Complete Version 3 VTuber Data Pipeline & Unlocked Speech Dataset
**Package**: vtuber_pipeline
**Branch**: `master`

### Summary

Resolved yt-dlp/SABR streaming 403 download failures using standalone compiled yt-dlp binary via subprocess. Wrote scripts/prepare_raw_wavs.py to convert downloads to 48kHz stereo WAVs. Implemented v3 curation rules including verified solo creator speech bypass (--bypass-multi-speaker mori/enna), 5-minute minimum duration speech filter (blocking Shorts), and strict music classifications. Curated 85 WAV sources and output 6,977 segments including 726 clean speech segments for Enna and 415 clean speech segments for Mori.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `d5760d3` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 16: Refine VTuber Dataset Curation and Implement Dynamic Demo System

**Date**: 2026-05-25
**Task**: Refine VTuber Dataset Curation and Implement Dynamic Demo System
**Package**: vtuber_pipeline
**Branch**: `master`

### Summary

Completed VTuber Dataset Curation V3 with dry vocal stems and verified solo chatting overrides (Kiara, Enna, Mori). Implemented a dynamic argparse-driven build_demo.py script supporting simultaneous coexistence of meeting_demo and voice_conversion comparative dashboards with elegant Glassmorphic download buttons.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `469a065` | (see git log) |
| `adc71df` | (see git log) |
| `0993ea3` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 17: Upgrade Timbre Pivoting to Multi-Dimensional Reference Comparison

**Date**: 2026-05-25
**Task**: Upgrade Timbre Pivoting to Multi-Dimensional Reference Comparison
**Package**: vtuber_pipeline
**Branch**: `master`

### Summary

Redesigned the Seed-VC Timbre Pivoting UI section to showcase a comprehensive comparative grid. It now compares 7 audio signals per case (Alto 1 to Japanese/English Tenor 1) across Source Singing/Speech, Target Speech/Singing references, and outputs pivoted to Source Speech, Target Speech, and Target Singing timbres. Completely removed all meeting/one-on-one terminology in favor of clean academic/R&D naming.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `7286ecd` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete
