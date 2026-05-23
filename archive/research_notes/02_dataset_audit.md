# Dataset Audit

Status: PARTIAL GO

No datasets were downloaded.

Hypothesis under test: CMU ARCTIC is the best first demo dataset because several speakers read the same prompts, which makes source-target pairing easier.

Current verdict: hypothesis is supported for a first demo, pending local path verification. CMU ARCTIC has shared prompt structure and preferred bdl/slt speakers are explicitly listed by the official Festvox page/search result. VCTK is useful later but only some text is shared across speakers. LibriTTS-R is large and not designed as paired same-prompt multi-speaker data. USC LSS is articulatory and highly relevant to ARTI-6, but single-speaker and access-form based, so it is not suitable for source-target speaker conversion demo.

## Dataset Comparison

| Dataset | Download URL | License | Speakers | Shared utterance IDs/prompts | Sample rate | Approx size | Easiest two-speaker subset | Small manifest CSV | First-demo suitability | Paper-level suitability |
|---|---|---|---|---|---|---|---|---|---|---|
| CMU ARCTIC | Main page: `https://www.festvox.org/cmu_arctic/`; packed files commonly under `https://www.speech.cs.cmu.edu/cmu_arctic/packed/`, e.g. `cmu_us_bdl_arctic-0.95-release.tar.bz2`, `cmu_us_slt_arctic-0.95-release.tar.bz2` | BSD-style/open software license per CMU ARCTIC paper/search evidence; some ports describe MIT-variant. Verify actual `COPYING` after download. | Official Festvox page lists bdl, slt, clb, rms, jmk, awb, ksp, plus additional aew. | YES. Official page says 1132 sentence prompt list; bdl/slt are listed ARCTIC speakers. | Official page/search evidence says distributions include 16 kHz waveform and EGG. Some package descriptions mention original 16-bit 32 kHz recordings for HTS voices; verify actual wav headers after download. | bdl approx 94 MB compressed; slt approx 120 MB compressed from FreeBSD/source search evidence. | bdl male source, slt female target. | Pair by basename/prompt ID after unpack: rows like `utt_id,source_wav,target_wav,source_spk,target_spk,split`. Use first 5-20 matching train IDs and 1-3 held-out IDs. | BEST first demo candidate. Small, paired prompts, bdl/slt preferred pair. | Useful for controlled demo, but old/small and not articulatory ground truth. |
| VCTK | Official/DataShare: `https://doi.org/10.7488/ds/2645`; uDialogue mirror: `https://www.udialogue.org/download/VCTK-Corpus.tar.gz` | ODC-By 1.0 on uDialogue/official search result. | 110 speakers in University of Edinburgh Research Explorer; uDialogue page says 109 in one mirror/version. | PARTIAL. Research Explorer says rainbow passage and elicitation paragraph are same for all speakers; newspaper texts differ by speaker. | 48 kHz, 16-bit downsampled from 96 kHz, official Research Explorer. | uDialogue mirror says 10.4 GB. | Choose two speakers with clean transcript availability, e.g. p225/p226 or other verified IDs after local listing. | For shared text only, join transcript IDs that match across selected speakers; otherwise create unpaired stats manifest. | Good backup if CMU ARCTIC unavailable, but less directly paired for most utterances. | Stronger for speaker diversity and later robustness; weaker for paired prompt transform fitting. |
| LibriTTS-R | OpenSLR 141: `https://www.openslr.org/141/` | CC BY 4.0, OpenSLR. | 2,456 speakers, derived from LibriTTS, arXiv/OpenSLR. | NO clear paired same-prompt structure verified. Samples are identical to LibriTTS constituents, but not designed as same-prompt speaker pairs. | 24 kHz, OpenSLR/arXiv. | Large: dev/test parts ~1 GB each; train-clean-100 8.1 GB; train-clean-360 28 GB; train-other-500 46 GB. | Use small dev-clean subset only if already available locally; otherwise too large for current phase. | Select two speakers with enough utterances and create unpaired/stats manifest, not paired prompt manifest. | Not ideal for first demo due size and pairing weakness. | Useful later for broader synthesis/speaker embedding behavior, not for clean paired articulatory transform test. |
| USC Long Single-Speaker rtMRI / LSS | Official page: `https://sail.usc.edu/span/single_spk/`; access starts with Google form linked there. | Dataset license UNKNOWN from official page. Paper/preprint may be CC BY 4.0, but dataset terms are not verified. | One native speaker of American English, official page/arXiv. | NO for cross-speaker VC: single speaker only. Sentence-level splits are available. | UNKNOWN from official page. Secondary summaries mention 16 kHz audio; do not rely on that until dataset/docs are obtained. | Roughly one hour of video and audio, official page/arXiv. | Not applicable for two-speaker VC. | If accessed later, manifest can list sentence-level split IDs and paths for articulatory analysis, not source-target VC. | Poor for first VC demo; excellent for later articulatory validation and interpretability if access terms permit. | Strong paper relevance for articulatory grounding, but not multi-speaker VC. |

## Evidence Notes

### CMU ARCTIC

Evidence:

- Official Festvox search result says the CMU_ARCTIC databases are phonetically balanced US English single-speaker databases for speech synthesis.
- Official Festvox search result lists bdl male and slt female, along with other speakers.
- Official Festvox search result says the 1132 sentence prompt list is available and distributions include 16 kHz waveform and EGG.
- CMU ARCTIC paper/search result says the entire package is distributed as free software without restriction on commercial or non-commercial use, and references a BSD-style open software license.

UNKNOWN:

- Local dataset path.
- Actual local wav sample rate for bdl/slt until files are inspected.
- Actual `COPYING` text until archives are downloaded/available locally.

Small manifest plan:

```csv
utt_id,source_speaker,target_speaker,source_wav,target_wav,split
arctic_a0001,bdl,slt,/path/bdl/wav/arctic_a0001.wav,/path/slt/wav/arctic_a0001.wav,train
```

### VCTK

Evidence:

- University of Edinburgh Research Explorer says VCTK v0.92 includes 110 English speakers, each reading about 400 sentences.
- It states the rainbow passage and elicitation paragraph are the same for all speakers, while newspaper texts differ.
- It states recordings were converted to 16-bit and downsampled to 48 kHz.
- uDialogue search result states ODC-By v1.0 and a 10.4 GB download.

UNKNOWN:

- Exact local speaker IDs and path layout.
- Which shared prompt IDs are easiest to pair without downloading.

Small manifest plan:

```csv
utt_id,source_speaker,target_speaker,source_wav,target_wav,split
pXXX_shared_prompt,p225,p226,/path/wav48_silence_trimmed/p225/...,/path/wav48_silence_trimmed/p226/...,train
```

Use only transcript IDs that are confirmed shared across the two selected speakers.

### LibriTTS-R

Evidence:

- OpenSLR 141 says LibriTTS-R is a sound-quality improved version of LibriTTS.
- OpenSLR says license is CC BY 4.0.
- OpenSLR/arXiv say it is approximately 585 hours at 24 kHz.
- arXiv says LibriTTS has 2,456 speakers and corresponding texts.
- OpenSLR download sizes show this is not a small first-phase dataset.

UNKNOWN:

- Whether any convenient same-text cross-speaker pair exists.
- Local availability.

Small manifest plan:

Use only if already locally available:

```csv
utt_id,speaker,wav,text,split
<speaker>-<chapter>-<utt>,<speaker>,/path/to/file.wav,<transcript>,train
```

For LinearVC, this is better suited to unpaired statistics than prompt-paired affine fitting.

### USC LSS

Evidence:

- Official page says it contains roughly one hour of rtMRI video and simultaneous audio from a single native speaker of American English.
- Official page says it includes derived representations: cropped vocal-tract video, sentence-level splits, restored/denoised audio, and ROI time series.
- Official page says access/download begins by filling out a form.
- ARTI-6 README says this is the dataset used for the articulatory inversion task.

UNKNOWN:

- Dataset license.
- Sample rate from primary docs.
- Access approval and local path.
- File layout.

Small manifest plan:

Not for two-speaker VC. If accessed later:

```csv
utt_id,wav,roi_timeseries,video,split
<sentence_id>,/path/audio.wav,/path/roi.csv,/path/video.*,train
```

## Dataset Recommendation

Use CMU ARCTIC bdl -> slt first if local/download approval is available. It best matches the first-demo need: small, same-prompt, two-speaker source-target pairing.

Use VCTK second if CMU ARCTIC is unavailable, but limit to verified shared text or switch to unpaired mean/std transforms.

Do not use LibriTTS-R for first demo unless it is already available locally. It is too large and not pair-oriented.

Use USC LSS later for articulatory interpretability and grounding, not as the first two-speaker VC dataset.

## Sources

- CMU ARCTIC official page/search result: `https://www.festvox.org/cmu_arctic/`
- CMU ARCTIC paper: `https://www.cs.cmu.edu/~awb/papers/ssw5/arctic.pdf`
- VCTK official metadata: `https://www.research.ed.ac.uk/en/datasets/cstr-vctk-corpus-english-multi-speaker-corpus-for-cstr-voice-clon/`
- VCTK mirror/download page: `https://www.udialogue.org/download/cstr-vctk-corpus.html`
- LibriTTS-R OpenSLR: `https://www.openslr.org/141/`
- LibriTTS-R arXiv: `https://arxiv.org/abs/2305.18802`
- USC LSS official page: `https://sail.usc.edu/span/single_spk/`
- USC LSS arXiv: `https://arxiv.org/abs/2509.14479`
