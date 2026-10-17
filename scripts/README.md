# Starter scripts

Both scripts use Python's standard library and require no installation beyond a working Python 3 environment. Run from the repository root.

`toy_refinement_demo.py` demonstrates two-net center-pin HPWL, rectangle legality and one greedy relocation. It is a small strictly legal explanatory example, **not PPO, MaskRegulate, an EDA tool or evidence of generalization**. It intentionally uses simpler legality than the native passwise refiner.

`validate_manifest.py` checks repeated design IDs, family and parent-design overlap across splits, duplicate file hashes across splits, basic schema and presence of training/validation/test records. `--require-real` additionally requires audited status, a hash and an HTTPS provenance URL. These are bookkeeping checks; a user can supply false metadata. The script does not prove lineage independence, verify external downloads, or audit pretraining.

```bash
python scripts/toy_refinement_demo.py
python scripts/validate_manifest.py configs/split_manifest.example.json
python scripts/validate_manifest.py configs/split_manifest.example.json --require-real
```

The final command should fail because the supplied manifest is synthetic. The experiment plan is declarative proposal metadata, not an executable training configuration. Actual training adapters and benchmarks are future work.
