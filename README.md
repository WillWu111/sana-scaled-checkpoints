# SanaScaled checkpoints

Two historical `sana_scaled` adaptation checkpoints, independently initialized from **VDN-MiniMax-H3 Stage-B step 2000**.

| Experiment | Saved step | Training objective | Original file |
| --- | ---: | --- | --- |
| 2026-09-18 | 200 | Data FM + 0.1 × dense H3 final-attention NMSE | `hybrid_lora_step000200.pt` |
| 2026-09-19 | 1000 | Pure data FM; no teacher supervision | `hybrid_lora_step001000.pt` |

The data FM term includes video FM + 0.2 × audio FM. The second experiment starts independently from Stage-B; it is not a continuation of the step-200 checkpoint.

These files contain the adaptation branch and attention LoRA weights. They require the matching H3 base model and `sana_scaled` implementation; they are not standalone full-model checkpoints. They are the historical `sana_scaled` variant, not the later `sana_litela` or ReLU² variants. Training/inference code and base-model weights are not included in this repository.

## Download and restore

Download from [Releases](https://github.com/WillWu111/sana-scaled-checkpoints/releases/tag/sana-scaled-202609). Each checkpoint is 9,227,027,323 bytes (about 9.23 GB) and is split into five raw binary parts. The split does not change any checkpoint bytes.

1. Download all five `.part01`–`.part05` files for the desired checkpoint into one directory.
2. Download `manifest.json` and `restore_weights.py` into that directory.
3. Run with Python 3.9 or newer:

```bash
# Restore both checkpoints (requires all ten parts):
python3 restore_weights.py --parts-dir . --output-dir weights

# Or restore just one checkpoint:
python3 restore_weights.py --only step200 --parts-dir . --output-dir weights
python3 restore_weights.py --only step1000 --parts-dir . --output-dir weights

# Verify all parts and the combined checkpoint hashes without creating output files:
python3 restore_weights.py --parts-dir . --verify-only
```

The script verifies every part's size and SHA-256, verifies the reconstructed checkpoint, and then publishes the output file. Allow an additional 9.23 GB of free disk space for each restored checkpoint.

Output paths:

```text
weights/20260918_sana_fm_attention_step200/hybrid_lora_step000200.pt
weights/20260919_sana_fm_only_step1000/hybrid_lora_step001000.pt
```

## Original checkpoint SHA-256

```text
00c961a1ef8af497a030974be17c72690f0deb970394815d32c390a2990d7759  hybrid_lora_step000200.pt
653c7477d434fb4679f1c0a608964f4bf85d718df7e79947fb8dfa225a783126  hybrid_lora_step001000.pt
```

Per-part checksums, original sizes and experiment metadata are in `manifest.json`, `SHA256SUMS.parts` and `SHA256SUMS.weights`.
