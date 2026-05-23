# polish ARTI-6 LinearVC demo website

## Goal

Create a polished, truthful, end-user-friendly landing page for the ARTI-6 + LinearVC demo so a visitor can understand the research idea in under a minute, then drill into the experiment design without needing to read the raw config or upstream paper first.

## What I already know

* The repo is for an ARTI-6 + LinearVC research engineering demo.
* `arti6_linearvc_demo/` is the intended home for first-party demo code.
* The archived experiment config defines the core story: source speech is inverted into six articulatory trajectories, those trajectories are linearly transformed, and the result is synthesized while comparing against an embedding-only baseline.
* Upstream `external/arti-6/` includes the official README, an overview architecture image, example audio, and a basic project page.
* The public page should be clear to end users, not merely a dump of research notes.
* Current experiment execution is still in progress, so the page must distinguish what already exists from what the planned LinearVC experiment will test.

## Assumptions (temporary)

* English is the primary website language.
* A static site is sufficient for the first version.
* The right tone is a research-demo landing page: visually polished, plain-English first, technical depth second.
* We should reuse trustworthy existing assets before generating new decorative ones.

## Open Questions

* No blocking questions for a first pass; copy/style can be refined after the initial page exists.

## Requirements (evolving)

* Build the first-party page under `arti6_linearvc_demo/`.
* Explain the project in plain language before technical details.
* Make the six articulatory dimensions and the pipeline visually legible.
* Clearly compare the embedding-only baseline with the proposed articulatory-transform path.
* Be honest about project status: planned experiment versus verified upstream ARTI-6 capability.
* Reuse available upstream assets when appropriate and avoid fake result claims.
* Keep the page responsive and readable on desktop and mobile.

## Acceptance Criteria (evolving)

* [ ] A visitor can answer “what is this?”, “why does it matter?”, and “what is being compared?” from the first few sections.
* [ ] The page has a coherent visual hierarchy, spacing, and responsive behavior.
* [ ] The page includes a clear project-status section that avoids overstating completed work.
* [ ] Existing upstream ARTI-6 materials are attributed or referenced in context rather than silently repackaged.
* [ ] The site can be opened locally as a static page without a build step.

## Definition of Done (team quality bar)

* Layout works at common mobile and desktop widths.
* Content is internally consistent with the archived experiment config and current project state.
* Links and referenced assets resolve locally.
* No placeholder lorem ipsum or invented benchmark results.

## Out of Scope (explicit)

* Full backend, deployment pipeline, or CMS.
* Fabricated LinearVC audio/results before the experiment has actually run.
* Rebuilding the upstream ARTI-6 sample page wholesale.

## Technical Notes

* Relevant files inspected:
  * `archive/provisional_research_harness/configs/task_arti6_linearvc.yaml`
  * `external/arti-6/README.md`
  * `external/arti-6/docs/index.html`
  * `external/arti-6/docs/src/overview_architecture.png`
  * `.trellis/spec/repo-structure.md`
  * `.trellis/spec/research-safety.md`
* The page should preserve the repo boundary: first-party work in `arti6_linearvc_demo/`, upstream dependency in `external/arti-6/`.
