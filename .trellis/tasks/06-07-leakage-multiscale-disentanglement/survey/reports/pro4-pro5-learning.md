# Pro4/Pro5 Learning Synthesis

Date: 2026-06-16

## Recommendation

Continue with **pro5 first**, then use **pro4 as the backup-track guardrail**.

Pro5 directly answers the current planning bottleneck: which research direction
should get the first 30 days. It recommends the same-person speech-vs-singing
timbre-shift project as the primary direction, with a concrete Week 1 leakage
triage and stop/go criteria. Pro4 is valuable, but it mainly teaches what not
to overclaim in singing skill evaluation and how to reformulate it as a
secondary evaluation/feedback project.

## Why Pro5 Comes First

Pro5 aligns with the active task's current MVP:

- primary lane: same-person speech-vs-singing timbre shift;
- first experiment: frozen representation leakage map;
- core evidence: mode AUC, cross-mode identity retrieval, same-person
  speech/singing cosine gap, and residualized controls;
- downstream hook: Seed-VC prompt-mode stress test;
- pivot condition: if the residual collapses under F0/energy/duration controls,
  move to GTSinger technique-direction discovery.

The strongest research question from Pro5 is:

> Where do frozen audio representations preserve same-person identity across
> speech and singing, where do they encode speech/singing mode, and does that
> representation gap predict prompt-mode sensitivity in zero-shot SVC?

This is more actionable than starting from singing-skill prediction because it
has paired/same-person data, clear probes, and a downstream SVC consequence.

## What To Learn From Pro5

1. **Do not train a new SVC model first.**
   The first result should be measurement: layer-wise leakage, retrieval, and
   residualized controls.

2. **Use a kill-test mindset.**
   The first week should be allowed to kill the idea. Continue only if the
   speech/singing signal survives nuisance controls and has some downstream
   prompt-mode relevance.

3. **Define leakage operationally.**
   Leakage is recoverable singer/mode information in representations intended
   for content or general audio modeling, measured under speaker-disjoint and
   nuisance-controlled protocols.

4. **Keep the contribution narrow.**
   The defensible claim is representation mapping plus prompt-mode stress
   testing, not full disentanglement or a new singing conversion architecture.

5. **Use backup logic early.**
   If the timbre-shift residual is mostly F0, loudness, duration, gender, or
   channel, pivot to the GTSinger technique-direction track.

## What To Learn From Pro4

Pro4's main lesson is that **"future professional voice" is not a valid
supervised target** with current public data. It requires longitudinal
same-singer recordings under controlled training and annotation conditions.

The usable reformulations are:

- current singing MOS or perceived-quality prediction;
- reference-conditioned karaoke pitch/rhythm/lyric scoring;
- singing technique or vocal-attribute recognition;
- multi-dimensional feedback;
- pairwise best-take ranking without longitudinal claims.

For this task, Pro4 should be treated as:

- a backup thesis direction if speech/singing timbre-shift fails;
- a source of leakage-control warnings for subjective singing evaluation;
- a reminder not to call MOS or technique classification "skill" unless the
  labels and protocol support that claim.

## Updated Direction

The task should continue with the Pro5 plan:

1. Run Stage A leakage-map experiment on the most accessible same-person
   speech/singing data.
2. Control for F0, loudness, duration, voiced ratio, and content/channel
   confounds.
3. Produce the representation-layer figure:
   mode AUC, residualized mode AUC, speech-to-singing Recall@1,
   singing-to-speech Recall@1, and speech/singing cosine gap.
4. Add a small Seed-VC speech-prompt versus singing-prompt stress test only
   after the representation audit shows a robust signal.
5. Pivot to GTSinger technique directions if the signal collapses under
   controls or does not replicate.

## Next User Decision

The next planning decision is whether the immediate learning session should:

- go deep on **Pro5** and turn it into an engineering-ready Stage A experiment
  spec; or
- go deep on **Pro4** and design the backup singing feedback/technique
  evaluation track.

Recommended answer: **Pro5 first**.
