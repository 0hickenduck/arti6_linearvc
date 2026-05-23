# Fix Git Configuration

## Goal

Initialize the Git repository and configure the local user identity to enable proper version control for the project. Make an initial commit.

## What I already know

* The root directory `/home/bowen/bowen_lab/projects/arti6_linearvc` is not a valid Git repository (the `.git` directory is empty/corrupt).
* Global Git user configuration is missing.
* The user wants to fix this to ensure changes are tracked.

## Assumptions (temporary)

* The user wants a clean, fresh Git initialization in the current root.

## Requirements (evolving)

* Run `git init`.
* Set project-local `user.name` and `user.email`.
* Make an initial commit tracking the current state.

## Acceptance Criteria (evolving)

* [ ] `git status` works in the root directory.
* [ ] A valid initial commit exists.
* [ ] Local user configuration is set.

## Definition of Done (team quality bar)

* The project is successfully placed under version control.

## Out of Scope (explicit)

* Pushing to a remote repository.
