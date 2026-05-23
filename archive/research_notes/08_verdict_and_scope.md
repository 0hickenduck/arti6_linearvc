# Verdict And Scope

Status: PARTIAL GO

## Verdict

Use the existing harness direction as a task specification layer, but do not run ARTI-6 yet.

The ARTI-6 + LinearVC specialization is now scoped as a gated research workflow. The next phase should audit the real ARTI-6 repository and environment before writing runnable project code.

## In Scope Now

- Define the target research question.
- Define the ARTI-6 six-dimensional representation.
- Define the eventual inversion, reconstruction, embedding-only VC, transform-only, and transform-plus-target-speaker pipeline.
- Define task gates from machine context through final feasibility report.
- Define minimal demo design.
- Define risks and human questions.

## Out Of Scope Now

- Downloading datasets.
- Downloading model checkpoints.
- Installing heavyweight GPU packages.
- Running ARTI-6.
- Implementing ARTI-6 wrappers.
- Implementing LinearVC fitting scripts.
- Claiming CMU ARCTIC paths, ARTI-6 APIs, checkpoints, CUDA, or lab-server availability.

## Scope Boundary For The First Demo

The first practical demo should stop at a tiny ablation set:

```text
source_arti_feats + target_spk_emb
vs.
transformed_source_arti + target_spk_emb
```

If the transformed version differs in interpretable trajectory diagnostics and creates audible changes without destroying synthesis quality, the project earns a stronger follow-up phase.

If the target speaker embedding dominates and the transform has little effect, the result is still useful: it bounds how much speaker-dependent information ARTI-6 trajectories carry under simple linear transformations.

## Next Recommended Actions

1. Restore or create only the missing lightweight `research_harness/scripts/check_machine.py` utility if the harness is expected to exist.
2. Audit the actual ARTI-6 repository from README/source.
3. Verify checkpoint availability without downloading unless approved.
4. Verify dataset location and CMU ARCTIC speaker layout.
5. Only then create runnable extraction/fitting/synthesis scaffolding.
