#!/usr/bin/env python3
"""
Validate YAML pipeline examples under `examples/pipelines/`.

This is a *static* validator:
- Ensures YAML parses
- Ensures the top-level structure matches what the Scala PipelineParser expects:
  - top-level `pipeline` is a list
  - each stage item is a mapping with only `stage` and optional `args`
- Performs light sanity checks on a few common stages

Note: This does NOT execute pipelines. It's meant to catch documentation drift early.
"""

from __future__ import annotations

import glob
import os
import sys
from typing import Any, Dict, List


def _load_yaml(path: str) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "PyYAML is required to validate examples.\n"
            "Install with: python3 -m pip install pyyaml\n"
            f"Import error: {e}"
        )

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping/object")
    return data


def _expect(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def validate_file(path: str) -> None:
    data = _load_yaml(path)

    _expect("pipeline" in data, "Missing top-level 'pipeline' key")
    pipeline = data["pipeline"]
    _expect(isinstance(pipeline, list), "Top-level 'pipeline' must be a list")

    # Validate fetch.traces structure if present
    fetch = data.get("fetch")
    if fetch is not None:
        _expect(isinstance(fetch, dict), "'fetch' must be a mapping")
        traces = fetch.get("traces", [])
        _expect(isinstance(traces, list), "'fetch.traces' must be a list if present")
        for i, t in enumerate(traces):
            _expect(isinstance(t, dict), f"'fetch.traces[{i}]' must be a mapping")
            has_action = "action" in t or "factory" in t
            _expect(has_action, f"'fetch.traces[{i}]' must include 'action' or 'factory'")
            if "params" in t:
                _expect(isinstance(t["params"], dict), f"'fetch.traces[{i}].params' must be a mapping")

    # Validate stages
    for idx, st in enumerate(pipeline):
        _expect(isinstance(st, dict), f"'pipeline[{idx}]' must be a mapping with keys 'stage' and optional 'args'")

        # StageDef in Scala only supports 'stage' and 'args' (unknown keys will fail parsing)
        allowed_keys = {"stage", "args"}
        extra = set(st.keys()) - allowed_keys
        _expect(not extra, f"'pipeline[{idx}]' contains unsupported keys: {sorted(extra)}")

        stage = st.get("stage")
        _expect(isinstance(stage, str) and stage.strip(), f"'pipeline[{idx}].stage' must be a non-empty string")

        args = st.get("args", [])
        _expect(isinstance(args, list), f"'pipeline[{idx}].args' must be a list if present")

        # Light sanity checks for a few common stages (not exhaustive)
        stage_lc = stage.lower()
        if stage_lc in {"join", "visitjoin"}:
            _expect(len(args) >= 1, f"'{stage}' requires at least 1 arg (selector or $column)")
            _expect(len(args) <= 2, f"'{stage}' supports at most 2 args (selector, optional joinType)")
        elif stage_lc in {"explore", "visitexplore"}:
            _expect(len(args) >= 1, f"'{stage}' requires at least 1 arg (selector or $column)")
            _expect(len(args) <= 2, f"'{stage}' supports at most 2 args (selector, optional depth)")
        elif stage_lc == "extract":
            _expect(len(args) >= 1, "'extract' requires at least 1 extractor definition")
        elif stage_lc in {"flatselect", "widen"}:
            _expect(len(args) >= 1, "'flatSelect' requires a segment selector as first arg")


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    examples_dir = os.path.join(root, "examples", "pipelines")
    files = sorted(glob.glob(os.path.join(examples_dir, "*.y*ml")))

    if not files:
        print(f"No YAML files found under {examples_dir}")
        return 1

    failed: List[str] = []
    for f in files:
        try:
            validate_file(f)
            print(f"OK  - {os.path.relpath(f, root)}")
        except Exception as e:
            failed.append(f)
            print(f"ERR - {os.path.relpath(f, root)}: {e}")

    if failed:
        print(f"\nFAILED: {len(failed)}/{len(files)} example(s)")
        return 2

    print(f"\nSUCCESS: {len(files)} example(s) validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


