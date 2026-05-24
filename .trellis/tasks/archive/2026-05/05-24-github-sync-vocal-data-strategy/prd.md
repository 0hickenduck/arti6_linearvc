# GitHub Sync and Vocal Data Strategy

## Goal

Make this project safe to synchronize between the local machine and the lab server through a GitHub remote, while defining a more defensible data curation strategy for messy VTuber speech and singing audio collected from YouTube.

## What I Already Know

* The repository now has `origin` configured as `https://github.com/0hickenduck/arti6_linearvc.git`.
* The user has created a private GitHub repository and is uploading the project.
* `gh` is not installed on this machine, and neither `GITHUB_TOKEN` nor `GH_TOKEN` is set.
* The root `.gitignore` already excludes `data/`, `outputs/`, `.venv/`, model checkpoints, archives, cookies, and common local caches.
* Large local data exists under `data/`, `outputs/`, and `.venv/`, but those are already ignored.
* The current git object store is about 152 MiB, so the repository itself is not huge yet.
* `external/seed-vc` is tracked as a gitlink at commit `51383efd921027683c89e5348211d93ff12ac2a8`, but no `.gitmodules` entry exists. This will break normal submodule workflows on a fresh clone.
* The current VTuber pipeline uses Demucs for vocal isolation and Silero VAD / Whisper-based segmentation. The current segmentation can remove non-linguistic vocal material too aggressively.
* The user wants code synchronized through GitHub, while large data and generated archives should stay outside normal git and be transferred local-to-server or server-to-local through an agent.
* The user wants to reuse existing WAV files for the next segmentation pass instead of downloading from YouTube again.
* The user now wants this workspace split conceptually from the original ARTI-6 / LinearVC lane because the active work is VTuber speech/singing curation.
* The user wants the local Trellis harness updated so Google Antigravity can use the same workflow and the new `agy` CLI.

## Assumptions

* The GitHub repository should be private by default because the repo contains research scripts, external code pointers, generated demos, and YouTube-derived workflow metadata.
* Training data, raw YouTube audio, intermediate stems, generated datasets, model checkpoints, and archives should not be committed to normal git.
* Small demo audio that is already tracked can stay for now, but future demo assets should be reviewed before commit.
* The first implementation should favor reproducible manifests and transfer scripts over Git LFS for training data.

## Requirements

* Configure the repository so both machines can pull/push code safely through the existing GitHub remote.
* Preserve ignored local data and avoid accidentally staging raw audio, processed datasets, checkpoints, temporary Demucs output, or large archives.
* Fix or document the `external/seed-vc` gitlink/submodule state so a fresh clone can recover the dependency.
* Add clear local/server sync documentation or scripts for the code repo and large data paths.
* Define a segmentation policy that separates:
  * speech-domain zatsudan data,
  * singing-domain karaoke/MV data,
  * ambiguous or contaminated segments.
* For speech, prefer solo streams and use speaker diarization / target speaker verification where multiple speakers may appear.
* For singing, do not use ASR linguistic content as the primary gate. Preserve vocalizations, breath, humming, ad libs, and sustained notes when they are target-speaker vocal material.
* Every curated segment should be traceable through a manifest with source video id, source timestamps, domain, speaker/singer confidence, processing step, and quality status.
* Ambiguous segments should go to quarantine rather than the clean training set.
* Run the next segmentation pass against existing local WAV material.
* Add Trellis package metadata and project-lane documentation so VTuber, ARTI6, and harness work are easy to distinguish.
* Add Antigravity workflow/skill files in the local project.
* Update the local CLI adapter for Antigravity `agy --print` and `agy --conversation`.

## Proposed Data Policy

### Speech

* Discover candidate solo zatsudan streams first.
* Run VAD or speech activity detection only as a coarse detector.
* Run diarization when a video may contain multiple speakers.
* Build a small target-speaker enrollment set and score candidate segments against it.
* Reject overlap, low target-speaker confidence, heavy music, heavy noise, or uncertain identity.
* Keep natural pause padding around accepted speech rather than cutting only recognized words.

### Singing

* Discover candidate solo singing videos separately from zatsudan.
* Run source separation first, currently Demucs or another music separation backend.
* Treat the vocal stem as "processed target vocal candidate", not as dry ground truth.
* Segment by vocal activity and acoustic continuity, not by ASR text presence.
* Keep short gaps inside phrases; cut only long BGM-only regions.
* Preserve non-linguistic but singer-produced material when it carries timbre or singing style.
* Score target-singer consistency using speaker/singer embeddings where feasible.
* Put duets, chorus, crowd singing, unclear collabs, and extreme separation artifacts into quarantine.

## Acceptance Criteria

* [x] The existing GitHub remote is documented and usable without staging ignored data.
* [x] Fresh-clone dependency recovery is documented or fixed for `external/seed-vc`.
* [x] A local/server sync workflow exists for code and large data.
* [x] The repo includes an explicit policy for what belongs in git, Git LFS, releases, and out-of-band transfer.
* [x] The segmentation strategy is documented with speech/singing differences and quarantine rules.
* [x] Relevant research precedents are recorded under `research/`.
* [x] Trellis package metadata and project-lane docs distinguish VTuber, ARTI6, and harness work.
* [x] Antigravity workflows and skills are available under `.agent/`.
* [x] The local CLI adapter can build Antigravity `agy` commands.

## Out of Scope

* Publishing a GitHub Pages demo site in this task.
* Uploading raw YouTube-derived datasets to GitHub.
* Claiming that separated vocals are dry vocals.
* Solving full multi-singer source separation in this task.
* Training a new model in this task.
* Rerunning audio segmentation after the user's 2026-05-24 listening feedback.

## Research References

* [`research/youtube-audio-dataset-precedents.md`](research/youtube-audio-dataset-precedents.md) - prior YouTube speech/singing dataset pipelines and how they map to this project.
* [`research/github-sync-large-data.md`](research/github-sync-large-data.md) - GitHub sync constraints and large-data handling plan.

## Open Questions

* None blocking for implementation.
