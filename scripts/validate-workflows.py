#!/usr/bin/env python3
"""Validate n8n workflow JSON files and example payloads."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / "workflows"
REQUIRED_MAIN_NODES = {
    "Webhook Trigger",
    "Configuration",
    "Parse Webhook Input",
    "Format Error Response",
    "Respond Error",
    "Respond Success",
    "Respond Preview",
    "Decode Base64 Image",
    "Should Post?",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_workflow(path: Path) -> list[str]:
    errors: list[str] = []
    data = load_json(path)
    nodes = data.get("nodes", [])
    connections = data.get("connections", {})
    names = {n.get("name") for n in nodes if n.get("name")}

    if not data.get("name"):
        errors.append(f"{path.name}: missing workflow name")

    if path.name == "linkedin-ai-poster.json":
        for required in REQUIRED_MAIN_NODES:
            if required not in names:
                errors.append(f"{path.name}: missing node '{required}'")
    if path.name == "linkedin-ai-poster-errors.json" and "Error Trigger" not in names:
        errors.append(f"{path.name}: missing node 'Error Trigger'")

    for src, conn in connections.items():
        if src not in names:
            errors.append(f"{path.name}: connection source '{src}' not in nodes")
        for branch in conn.get("main", []):
            for link in branch:
                tgt = link.get("node")
                if tgt and tgt not in names:
                    errors.append(f"{path.name}: connection target '{tgt}' not in nodes")

    # LinkedIn nodes should have retry
    if path.name == "linkedin-ai-poster.json":
        for n in nodes:
            if n.get("name", "").startswith("LinkedIn") and not n.get("retryOnFail"):
                errors.append(f"{path.name}: {n['name']} missing retryOnFail")

    return errors


def validate_examples() -> list[str]:
    errors: list[str] = []
    payloads_path = ROOT / "examples" / "webhook-payloads.json"
    schema_path = ROOT / "examples" / "webhook-payload.schema.json"
    if not payloads_path.exists():
        return ["examples/webhook-payloads.json missing"]
    payloads = load_json(payloads_path)
    if schema_path.exists():
        try:
            import jsonschema  # type: ignore

            schema = load_json(schema_path)
            for ex in payloads.get("examples", []):
                jsonschema.validate(ex.get("payload", {}), schema)
        except ImportError:
            pass
        except Exception as exc:
            errors.append(f"payload schema validation failed: {exc}")
    for ex in payloads.get("examples", []):
        if "payload" not in ex:
            errors.append(f"example '{ex.get('name')}' missing payload")
    return errors


def main() -> int:
    all_errors: list[str] = []
    for wf in sorted(WORKFLOWS.glob("*.json")):
        try:
            json.load(wf.open(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            all_errors.append(f"{wf.name}: invalid JSON — {exc}")
            continue
        all_errors.extend(validate_workflow(wf))

    all_errors.extend(validate_examples())

    if all_errors:
        print("VALIDATION FAILED")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("All validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())