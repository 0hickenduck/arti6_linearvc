# ARTI-6 Repository Audit

Status: PARTIAL GO

Audit target: `https://github.com/lee-jhwn/arti-6`

Local clone:

- Path: `external/arti-6/`
- Remote: `https://github.com/lee-jhwn/arti-6`
- HEAD verified by `git ls-remote`: `c61055d2b49a4ae4a7ca98b008ec7305b6ab9712`
- Clone size: `16M`

No ARTI-6 code was run. No models, checkpoints, or datasets were downloaded.

## Summary

The repository is public and was cloned successfully. It provides a small example, model wrapper class, inversion code, synthesis code, synthesis config, and a conda environment file. The code path is highly relevant to the LinearVC plan because `ARTI6.invert()` returns `arti_feats` and `spk_emb`, and `ARTI6.synthesize()` accepts articulatory features plus a speaker embedding.

Major caution: `load_model()` auto-downloads ARTI-6 checkpoints from Hugging Face, loads Microsoft WavLM-large through Transformers, and loads SpeechBrain ECAPA-TDNN. Do not call `load_model()` until download approval and environment checks are complete.

## ARTI-6 Code And Checkpoint Audit

| Component | Status | Evidence | Action needed |
|---|---|---|---|
| Repository public | VERIFIED | `git clone https://github.com/lee-jhwn/arti-6 external/arti-6` completed; `git ls-remote ... HEAD` returned `c61055d2b49a4ae4a7ca98b008ec7305b6ab9712`. | None for source access. |
| Installation method | PARTIAL | README shows example import/use, but no install command. Repo contains `env_mac.yml`; no `requirements.txt`, `setup.py`, or `pyproject.toml` found. | Treat as source-tree usage for now; create environment plan from `env_mac.yml` later. |
| Python version expected | VERIFIED | `env_mac.yml` pins `python=3.10.18`. | Use Python 3.10 environment for faithful reproduction; local machine currently has Python 3.14.5. |
| Dependencies | VERIFIED | `env_mac.yml` lists `torch==2.8.0`, `torchaudio==2.8.0`, `transformers==4.57.0`, `speechbrain==1.0.3`, `librosa==0.11.0`, `huggingface-hub==0.35.3`, `loralib==0.1.2`, `soundfile==0.13.1`, plus others. | Do not install yet. Later create lightweight environment plan first. |
| requirements/setup/pyproject/environment | VERIFIED | Only `env_mac.yml` was found among expected env files. Command: `find . -maxdepth 2 (...)` returned `./example.py`; file listing shows `env_mac.yml`; no requirements/setup/pyproject files. | Use `env_mac.yml` as dependency source; write our own lock/notes if needed. |
| Main API | VERIFIED | `arti6/arti6.py` defines `class ARTI6`; README uses `from arti6 import ARTI6`. | Import path may require running from repo root or adding `arti6/` to `sys.path`, as `example.py` does. Verify before packaging. |
| Example/demo usage | VERIFIED | `example.py` creates `ARTI6(device=device)`, calls `load_model()`, `invert('./example_gt.wav')`, `synthesize(...)`, and writes `example_arti6.wav` at 16000 Hz. | Do not run until model downloads are approved. |
| How to load model | VERIFIED | README and `arti6/arti6.py` show `arti6_model.load_model()`. Defaults: `mode='all'`, `invert_ckpt='inversion_flt_ckpt.pt'`, `synthesis_ckpt='generator.pt'`, `from_huggingface=True`. | Use `from_huggingface=False` only if local checkpoint paths are verified. |
| How to run inversion | VERIFIED | README: `arti6_model.invert(wav_path=<path_to_wav_file>)`; source returns `{'arti_feats': arti_feats, 'spk_emb': spk_emb}`. | After environment/checkpoint audit, wrap this call to save arrays. |
| How to run synthesis | VERIFIED | README/source: `arti6_model.synthesize(arti_feats, spk_emb)`. Source transposes features and feeds HiFi-GAN-like generator conditioned on `spk_emb`. | After smoke test, wrap synthesis for ablations. |
| Checkpoints auto-download | VERIFIED | README says checkpoints automatically load from Hugging Face. Source uses `hf_hub_download(repo_id='lee-jhwn/arti-6', ...)` for inversion and synthesis checkpoints. | Do not call `load_model()` without approval. |
| Checkpoint source | VERIFIED | Source uses Hugging Face repo `lee-jhwn/arti-6`; HF API metadata request returned public model repo with siblings: `.gitattributes`, `generator.pt`, `inversion_flt_ckpt.pt`, `inversion_lora_ckpt.pt`. | If approved later, download only into configured cache/models path. |
| Model weights public | VERIFIED | Hugging Face API returned `"private": false`, `"gated": false`, and listed checkpoint files. | No login appears required for ARTI-6 checkpoint repo, but execution not verified. |
| Hugging Face login required | LIKELY NO, NOT EXECUTED | HF API returned model metadata with `"private": false` and `"gated": false` without auth. | Mark as likely no for ARTI-6 repo; still verify during controlled download if approved. |
| WavLM-large required | VERIFIED | README: "Only `WavLM-large` version is currently supported." Source default `backbone='wavlm_large'`; `WavLMModel.from_pretrained("microsoft/wavlm-large")`. | Large dependency/model download risk. Ask before running. |
| ECAPA-TDNN required | VERIFIED | README says speaker embedding extracted by ECAPA-TDNN. Source calls `EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")`. | This likely downloads SpeechBrain model if not cached. Ask before running. |
| Input wav sample rate | VERIFIED | Source `load_wav(wav_path, sr=16000)` uses `librosa.load(..., sr=sr)`. WavLM feature extractor uses `sampling_rate=16_000`. | Resample input wavs to 16 kHz or rely on `librosa.load` resampling after verifying quality. |
| Output wav sample rate | VERIFIED | `example.py` writes output with `sf.write(..., 16000)`; synthesis config has `sampling_rate: 16000`; included wavs are 16 kHz by Python `wave` inspection. | Standardize demo outputs at 16 kHz. |
| CPU support | PARTIAL | README constructor comment says `device: cpu or cuda`; `example.py` chooses `"cuda" if torch.cuda.is_available() else "cpu"`; source maps torch loads to `self.device`. | CPU may work but WavLM-large may be slow/heavy. Verify with tiny smoke test only after downloads approved. |
| CUDA requirement | LIKELY NO, NOT EXECUTED | Code supports CPU string; synthesis config says `num_gpus: 0`. Source only uses CUDA conditionally. | Do not assume performance; lab GPU still unknown. |
| Batch processing support | NO | README: current version does not support batch processing, batch size fixed to 1. Source comments: `# TODO: add batch processing` for `invert` and `synthesize`. | Build initial pipeline as per-file loop. |
| Training code | NOT AVAILABLE YET | README says training code will be available upon publication. | No training dependency on ARTI-6 internals for first demo. |
| License | UNKNOWN | No `LICENSE` file found in cloned repo. README does not state a license in inspected lines. | Ask authors/check GitHub metadata before redistribution. |

## Notable Source-Level Issues For Later

- `example.py` appends `arti6` to `sys.path` before `from arti6 import ARTI6`. There is no packaging metadata found, so a clean import may need path handling.
- In `load_model()`, `invert_lora_ckpt` is assigned but not used; then LoRA loading uses `invert_ckpt.replace('filtered','lora')`. With default `inversion_flt_ckpt.pt`, that replacement does not change the string. This may be a bug or typo. Do not assume LoRA checkpoint loading works until audited by execution.
- `length.cuda()` appears in `wavlm_articulatory.py` when `length is not None`; current `invert()` does not pass length, so this path is probably inactive for the basic demo.

## Minimal Later Verification Plan

1. Confirm environment with Python 3.10 and no model downloads.
2. Confirm local/cache availability of `microsoft/wavlm-large`, `speechbrain/spkrec-ecapa-voxceleb`, and ARTI-6 checkpoint files.
3. If downloads are approved, set Hugging Face cache under `./cache` or configured cache.
4. Run a one-wav smoke test only after approval:

```bash
python3 example.py
```

or a safer wrapper that prints tensor shapes and writes outputs under `outputs/smoke/`.

## Sources

- Local source clone: `external/arti-6/`
- README: `external/arti-6/README.md`
- Main wrapper: `external/arti-6/arti6/arti6.py`
- Inversion model: `external/arti-6/arti6/inversion/wavlm_articulatory.py`
- Synthesis model/config: `external/arti-6/arti6/synthesis/`
- Example: `external/arti-6/example.py`
- Hugging Face model metadata: `https://huggingface.co/api/models/lee-jhwn/arti-6`
