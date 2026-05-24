# YouTube Audio Dataset Precedents

## Sources Checked

* VoxCeleb paper: https://www.sciencedirect.com/science/article/pii/S0885230819302712
* VoxConverse paper: https://arxiv.org/abs/2007.01216
* AVSpeech dataset page: https://looking-to-listen.github.io/avspeech/index.html
* AVA-ActiveSpeaker page: https://research.google/pubs/ava-activespeaker-an-audio-visual-dataset-for-active-speaker-detection/
* JTubeSpeech paper: https://arxiv.org/abs/2112.09323
* Acappella paper/page: https://arxiv.org/abs/2104.09946 and https://ipcv.github.io/Acappella/
* Demucs repository: https://github.com/facebookresearch/demucs
* Spleeter repository: https://github.com/deezer/spleeter
* pyannote.audio repository: https://github.com/pyannote/pyannote-audio

## Speech From YouTube

VoxCeleb is the closest precedent for extracting speaker data from unconstrained YouTube video. Its pipeline obtains YouTube videos, performs active speaker verification through audio-visual synchronization, and confirms identity through face recognition. The important lesson is not the exact face pipeline, since VTubers do not have normal human face tracks, but the layered filtering strategy: source discovery, activity verification, identity verification, and scale.

VoxConverse is directly relevant for messy multi-speaker YouTube audio. It uses active speaker detection and self-enrolled speaker verification to create diarization labels for in-the-wild videos. This maps well to zatsudan streams where a video may look solo but contains guests, clips, soundboards, or call-ins.

AVSpeech uses YouTube videos but keeps only short segments where a single visible speaker is audible and background noise is absent. This is a useful quality target, but it is stricter than our data reality.

JTubeSpeech is relevant for Japanese and multilingual speech. It builds a corpus from YouTube videos and subtitles using CTC-based ASR segmentation plus speaker verification. The useful idea is to use transcripts or ASR alignment as a filter for speech corpora, not as the only signal for identity or quality.

## Singing From YouTube

Acappella is the strongest direct precedent for YouTube singing. It builds about 46 hours of solo a cappella singing videos and studies audio-visual singing voice separation. It explicitly evaluates hard settings with overlapping voices and low target voice volume. It also manually selected data to avoid unusable clips. This supports a hybrid policy: automated filtering first, then quarantine and audit.

Music source separation tools such as Demucs and Spleeter are practical front ends for karaoke or MV audio. Demucs separates vocals, drums, bass, and other accompaniment, and its v4 line uses hybrid spectrogram/waveform modeling. Spleeter provides pretrained separation models for vocals/accompaniment and other stem configurations.

Neither Demucs nor Spleeter guarantees dry vocals. They return an estimated vocal stem that can retain reverb, compression, artifacts, backing vocals, and bleed. For this project, separated vocals should be treated as "processed target vocal candidates", not clean studio stems.

## Implications For This Project

The current aggressive ASR or VAD trimming is misaligned with singing. Singing often contains sustained vowels, breath, melisma, hums, ad libs, and non-lexical vocalizations that may fail linguistic-content filters but still carry target timbre and singing style. These should not be discarded only because no word was recognized.

For speech data, linguistic content is useful as a quality filter. For singing data, linguistic content should be optional metadata. The primary gates should be vocal presence, target identity consistency, artifact level, overlap, and phrase continuity.

## Recommended Pipeline Shape

### Speech

1. Discover likely solo zatsudan streams.
2. Download audio and keep a source manifest.
3. Run speech activity detection or VAD.
4. Run diarization if the stream can include guests.
5. Build target-speaker enrollment from high-confidence solo clips.
6. Score candidate segments against target speaker embeddings.
7. Reject overlap, wrong-speaker, music-heavy, and low-confidence segments.
8. Export 3-15 second segments with natural padding and source timestamps.

### Singing

1. Discover likely solo singing streams or songs.
2. Run music source separation.
3. Segment from the vocal stem using acoustic continuity and vocal activity, not ASR text.
4. Merge short gaps inside phrases and keep 150-300 ms padding.
5. Reject long BGM-only intervals, duets, chorus, heavy bleed, severe artifacts, or low target identity confidence.
6. Keep non-linguistic target vocal material when it is clean and identity-consistent.
7. Export clean, ambiguous, and rejected manifests separately.

## Research Framing

If the pipeline fails, the result can still be useful as a research artifact if the failure is measured. A credible negative-result direction would compare:

* audio-only VAD or ASR segmentation,
* source-separation plus vocal-activity segmentation,
* diarization / target-speaker verification,
* manual or semi-manual quarantine.

The key question becomes whether "in-the-wild YouTube VTuber audio" can support cross-domain speech/singing voice conversion without introducing speaker contamination or separation-artifact shortcuts.
