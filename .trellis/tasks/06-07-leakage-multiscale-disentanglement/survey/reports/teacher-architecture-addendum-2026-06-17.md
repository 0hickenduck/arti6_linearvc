# Teacher Meeting Architecture Addendum

Date: 2026-06-17

## Key Clarification

There are two levels of design:

1. **Analysis / proof stage**
   - frozen representations;
   - clustering, probing, analogy tests;
   - nuisance controls such as F0/duration residualization or matched cohorts.

2. **Architecture / control stage**
   - small trainable adapter;
   - FiLM, cross-attention, LoRA;
   - possibly Gradient Reversal Layer (GRL) for adversarial nuisance removal.

These should not be mixed too early.

## Is Gradient Reversal Better?

GRL is useful, but it is not the first experiment.

Better wording:

> After we verify that the representation contains useful technique or
> speech-singing residual information, we can train a small adapter with a
> Gradient Reversal Layer to suppress nuisance factors such as F0, duration, or
> source speaker identity while preserving the target factor.

GRL is stronger than simple linear residualization because it can learn
nonlinear nuisance removal. But it also has higher risk:

- it can erase the target information;
- it can become unstable;
- it requires a clear target-preservation loss;
- it is harder to interpret than a frozen-feature audit.

## Can GRL Work With Frozen Models?

Yes.

The base model can stay frozen. We train only a small module:

- projection head;
- FiLM module;
- LoRA adapter;
- low-rank affine adapter.

The GRL loss updates only the trainable adapter, not the frozen base model.

Sketch:

```text
audio -> frozen encoder -> h
                    -> adapter / LoRA -> z

z -> target head      -> preserve technique / singer identity / conversion target
z -> GRL -> nuisance head -> make F0 / duration / source identity hard to predict
```

This is a good architecture-stage idea.

## What Must Be Added For GRL To Make Sense

GRL cannot stand alone. It needs two losses:

1. **Target preservation loss**
   - technique classification;
   - same-singer speech/singing contrastive loss;
   - reconstruction or conversion-related loss;
   - target-singer similarity.

2. **Nuisance adversary loss**
   - F0 prediction;
   - duration prediction;
   - energy prediction;
   - source speaker / mode leakage prediction.

The adapter is trained to keep the target useful while making nuisance
prediction difficult.

## How To Present It

For Direction 1, technique adaptation:

> First I test whether technique information exists linearly. If not, I still
> can train a small technique-conditioned adapter. GRL can be added to make the
> adapter less dependent on singer identity, phone, or F0 shortcuts.

For Direction 2, timbre shift:

> First I test whether a speech-singing residual remains after simple controls.
> If it does, I can train a small adapter or LoRA module to predict a
> deployable speech-to-singing residual while using GRL to reduce F0/duration
> shortcuts.

## What Else To Add To The Research Design

Add these ablations:

- no control;
- linear residualization;
- matched-cohort control;
- adapter without GRL;
- adapter with GRL;
- strong nuisance adversary checked by both linear and nonlinear probes.

Add these warnings:

- GRL success does not prove true disentanglement;
- if target performance drops, the adapter may be deleting useful timbre;
- if only the adversary fails but a new probe succeeds, nuisance information is
  still present.

## Meeting-Safe Summary

> I see residualization as the clean analysis baseline, and GRL/LoRA as the
> later architecture stage. The first tells us whether the signal exists under
> controls. The second tests whether a model can actively learn a representation
> that keeps technique or identity while suppressing nuisance factors.
