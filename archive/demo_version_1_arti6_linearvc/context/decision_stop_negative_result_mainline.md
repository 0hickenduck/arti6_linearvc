# Decision: stop treating the ARTI-6 negative result as the mainline

Date: 2026-05-20

## Decision

Do not continue investing in the ARTI-6 LinearVC negative result as a main paper direction.

The key observation is already strong enough for our purposes:

```text
source_arti + target_speaker_id -> target timbre with source content
```

This directly shows that, in the current ARTI-6 synthesizer, timbre is mainly controlled by speaker ID while the 6D ARTI stream mostly controls phonetic / linguistic-articulatory content. More diagnostic proof of the same factorization is unlikely to produce a strong paper by itself.

## Consequence

The previous proposals:

- oracle-factorization report
- ARTI-vs-SSL speaker/content audit
- extra ARTI perturbation diagnostics

should be treated as optional supporting evidence or demo appendix, not as the main research path.

## Updated use of the negative result

Use it as a fast kill criterion:

```text
ARTI-only linear timbre conversion is structurally blocked in this pretrained architecture.
```

Do not spend more experiments trying to rescue this specific path unless it supports a new positive idea.

## Next search target

Move toward positive directions that can plausibly produce a new method or useful demo without training a large model:

1. SSL-space LinearVC / kNN-VC variants only if they lead to a new method, not just reproduction.
2. Source-filter / WORLD / McAdams / VTLN controls for small interpretable timbre manipulation.
3. Speaker-embedding-space manipulation if it gives controllable identity attributes while preserving content.
4. Articulatory spaces for accent/pronunciation/content editing, not timbre conversion.

The next proposal should be a set of concrete positive project options, with minimal experiments and reasons they are not just re-proving the ARTI-6 factorization.
