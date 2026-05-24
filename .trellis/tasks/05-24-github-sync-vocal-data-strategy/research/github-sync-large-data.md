# GitHub Sync And Large Data Notes

## Current Local State

* The repository has no remote configured.
* `gh` is not installed.
* `GITHUB_TOKEN` and `GH_TOKEN` are unset.
* The root `.gitignore` excludes `data/`, `outputs/`, `.venv/`, model checkpoints, archive files, and cookies.
* The git object store is about 152 MiB.
* `external/seed-vc` is tracked as a gitlink, but `.gitmodules` is missing.

## GitHub Constraints

GitHub warns for files larger than 50 MiB and blocks regular git files larger than 100 MiB. GitHub recommends keeping repositories small, ideally below 1 GB and strongly below 5 GB. Git LFS stores pointer files in git while storing large content separately, but Git LFS still has plan-dependent limits and is not a good default for training datasets.

Relevant docs:

* https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
* https://docs.github.com/github/managing-large-files/about-git-large-file-storage
* https://cli.github.com/manual/gh_repo_create

## Recommended Policy

### Put In Normal Git

* Source code.
* Small configs.
* PRDs, research notes, manifests, and reproducibility metadata.
* Scripts for download, preprocessing, evaluation, and sync.
* Small demo HTML and small demo audio only after review.

### Do Not Put In Normal Git

* `data/raw*`.
* `data/*processed*` and generated training sets.
* `outputs/`.
* Demucs intermediate stems.
* `.venv/`.
* model checkpoints and Hugging Face caches.
* YouTube cookies.
* generated tarballs and zip files.

### Use Out-Of-Band Transfer

Use `rsync` or `scp` for raw and processed data between the local machine and the lab server. Keep data reproducible through manifests rather than by committing the bytes.

### Use Git LFS Sparingly

Only consider Git LFS for small curated demo assets that should move with the repo. Do not use LFS for raw training corpora or large intermediate outputs.

## Implementation Notes

The first implementation should:

* Add or verify `.gitignore` coverage for data, outputs, cookies, checkpoints, archives, and caches.
* Add `.gitmodules` for `external/seed-vc` or replace the gitlink with a documented setup script.
* Add a short sync document covering:
  * clone on the second machine,
  * normal code sync with `git pull --rebase` and `git push`,
  * large-data sync with `rsync`,
  * manifest-first reproducibility.
* Avoid committing any currently ignored data.

## Remote Creation Blocker

Creating the GitHub remote requires one of:

* a GitHub repo URL created by the user,
* installed/authenticated `gh`,
* or an API token with repo creation permissions.

Given the current machine state, the safest next step is for the user to provide a target repo URL or confirm an owner/name/visibility and authentication route.
