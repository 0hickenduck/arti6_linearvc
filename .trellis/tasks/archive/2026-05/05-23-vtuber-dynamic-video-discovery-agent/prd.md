# brainstorm: VTuber Dynamic Video Discovery Agent

## Goal

Build an automated agent/workflow to dynamically search, filter, and compile a list of YouTube video URLs for specific VTubers (like FuwaMoco, Enna Alouette) that meet strict dataset-quality criteria. The output will be a structured manifest (JSON/list) categorizing each URL into domains (e.g., Solo Zatsudan/Speech, Karaoke/Singing) so the existing extraction pipeline can process them efficiently.

## What I already know

*   **Current Pipeline**: We already have `scrape_vtuber_audio.py` and `purify_audio.py` which can download and chunk audio given a URL and a domain tag.
*   **The Problem**: Hand-picking high-quality videos is tedious. We need an agent to find them.
*   **Quality Constraints**:
    *   Need clear, non-overlapping speech (e.g., solo Zatsudan streams).
    *   Must avoid collabs where voices overlap.
    *   For twins/groups like FuwaMoco, overlapping speech is a known issue; we need to either avoid heavy overlap or handle them specially.
    *   Need multilingual singing streams without chorus/group singing.
    *   Need to tag the output accurately (Zatsudan = Speech, MV/Karaoke = Singing) so the downstream pipeline knows what to expect.

## Assumptions (temporary)

*   We can identify video types (Zatsudan, Karaoke, Collab) reasonably well from YouTube video titles, tags, and descriptions.
*   We have access to YouTube's search functionality (via yt-dlp flat extraction or YouTube Data API).
*   The agent should output a list/JSON of URLs that we can then pass directly to our existing `scrape_vtuber_audio.py`.

## Open Questions

*   All open questions resolved.

## Requirements

*   Given a target VTuber channel, use `yt-dlp` (flat extraction) to discover recent/popular video titles and metadata.
*   Pass the metadata to an LLM (e.g., Gemini Flash) to classify each video as `Speech` (Zatsudan), `Singing` (Karaoke), `Collab`, or `Gaming`.
*   Filter out standard collabs or group streams for solo VTubers.
*   **Special Case (FuwaMoco/Twins)**: Do *not* exclude them. Accept their streams. The overlapping twin audio is valuable for other lab projects (chorus separation, speaker ID spoofing). Tag them appropriately, but download them.
*   Output a structured JSON manifest of valid URLs and their tags, ready to be consumed by `scrape_vtuber_audio.py`.

## Decision (ADR-lite)

**Context**: We need to dynamically find and categorize VTuber streams. Titles can be messy. Twins like FuwaMoco present an overlap problem.
**Decision**:
1.  **LLM Classification**: We will use a lightweight LLM script to read video titles/descriptions instead of fragile regex. This provides robust categorization for "Zatsudan" vs "Karaoke".
2.  **Retain Twin Data**: We will download FuwaMoco data despite the overlap. While it complicates the immediate single-speaker VC demo, the data is highly valuable for the lab's broader research (chorus separation, speaker identification). We will simply tag it and let downstream tools decide whether to process it.

## Acceptance Criteria (evolving)

*   [ ] Given a channel URL (e.g., Enna Alouette), the agent outputs at least 2 valid Solo Speech URLs and 2 valid Singing URLs.
*   [ ] The output format is compatible with or easily convertible to the input expected by `scrape_vtuber_audio.py`.

## Definition of Done (team quality bar)

*   Tests added/updated (unit/integration where appropriate)
*   Lint / typecheck / CI green
*   Docs/notes updated if behavior changes

## Out of Scope (explicit)

*   Actually downloading the audio (this task only covers *finding* the URLs; the previous task handles downloading).
*   Training new audio classification models.

## Technical Notes

*   VTuber titles often use specific keywords: `【歌枠】` (Karaoke), `【雑談】` (Zatsudan/Chat), `Free Chat`, `Unarchived Karaoke`.
*   Collabs often use `ft.`, `w/`, `x`, `コラボ`.
