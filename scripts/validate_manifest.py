"""Bookkeeping guard, not a proof of independent circuit provenance."""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def validate(manifest, require_real=False):
    errors = []
    rows = manifest.get("designs", [])
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(rows, list) or not rows:
        return errors + ["designs must be a nonempty list"]
    ids = set()
    groups = {key: defaultdict(set) for key in ("family_id", "parent_design", "sha256")}
    splits = defaultdict(int)
    required = ("design_id", "family_id", "parent_design", "split", "source_url", "status")
    for index, row in enumerate(rows):
        label = f"row {index + 1}"
        if not isinstance(row, dict):
            errors.append(f"{label}: must be an object")
            continue
        for key in required:
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{label}: missing/non-string {key}")
        design_id = row.get("design_id")
        if isinstance(design_id, str):
            if design_id in ids:
                errors.append(f"{label}: duplicate design_id {design_id}")
            ids.add(design_id)
        split = row.get("split")
        if split not in ("train", "validation", "test"):
            errors.append(f"{label}: invalid split {split!r}")
            continue
        splits[split] += 1
        for key, mapping in groups.items():
            value = row.get(key)
            if isinstance(value, str) and value:
                mapping[value].add(split)
        digest = row.get("sha256")
        if digest is not None and not (isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest)):
            errors.append(f"{label}: sha256 must be null or 64 hexadecimal characters")
        if require_real:
            if row.get("status") != "audited":
                errors.append(f"{label}: real mode requires status=audited")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                errors.append(f"{label}: real mode requires a recorded sha256")
            if not str(row.get("source_url", "")).startswith("https://"):
                errors.append(f"{label}: real mode requires an https provenance source")
    for key, mapping in groups.items():
        for value, members in mapping.items():
            if len(members) > 1:
                errors.append(f"cross-split {key} {value}: {', '.join(sorted(members))}")
    for split in ("train", "validation", "test"):
        if not splits[split]:
            errors.append(f"missing {split} examples")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--require-real", action="store_true")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest root must be an object")
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    errors = validate(manifest, args.require_real)
    if errors:
        print("FAIL\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    mode = "audited-record bookkeeping" if args.require_real else "example/bookkeeping"
    print(f"PASS: {len(manifest['designs'])} records; {mode} checks only.")
    print("Human provenance review and checkpoint/preprocessing audits are still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
