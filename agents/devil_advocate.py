"""
Devil's Advocate agent: adversarial challenge to the working diagnosis.
Deliberately contrarian — focuses on must-not-miss diagnoses.
Uses MedGemma 4B (multimodal) to independently examine the image.
Outputs structured JSON.
"""

import json
import logging
from collections.abc import Mapping
from agents.state import PipelineState
from agents.prompts import DEVIL_ADVOCATE_SYSTEM, DEVIL_ADVOCATE_USER
from agents.output_parser import parse_json_response
from models import medgemma_client

logger = logging.getLogger(__name__)


_DA_SCHEMA_KEYS = ("challenges", "must_not_miss", "recommended_workup")
_DA_WRAPPER_KEYS = (
    "devils_advocate_output",
    "devil_advocate_output",
    "devil_advocate",
    "output",
    "response",
    "result",
    "data",
)
_DA_SYNONYMS: dict[str, str] = {
    # must-not-miss
    "must_not_miss_diagnoses": "must_not_miss",
    "must_not_miss_differentials": "must_not_miss",
    "dangerous_alternatives": "must_not_miss",
    "critical_differentials": "must_not_miss",
    # workup
    "workup": "recommended_workup",
    "recommended_tests": "recommended_workup",
    "recommended_actions": "recommended_workup",
    "next_steps": "recommended_workup",
    # challenges
    "challenge": "challenges",
    "concerns": "challenges",
    "counterarguments": "challenges",
}


def _format_bias_summary(bias_out: dict) -> str:
    """Format bias detector output for the Devil's Advocate prompt."""
    parts = []
    if bias_out.get("discrepancy_summary"):
        parts.append(bias_out["discrepancy_summary"])
    for b in bias_out.get("identified_biases", []):
        parts.append(f"- {b.get('type', 'unknown')}: {b.get('evidence', '')} (severity: {b.get('severity', '?')})")
    if bias_out.get("missed_findings"):
        parts.append("Missed findings: " + ", ".join(bias_out["missed_findings"]))
    return "\n".join(parts) if parts else "No bias analysis available."


def _unwrap_da_payload(parsed: dict) -> dict:
    """Unwrap common container shapes: {"output": {...}}, {"result": {...}}, etc."""
    if any(k in parsed for k in _DA_SCHEMA_KEYS):
        return parsed

    for key in _DA_WRAPPER_KEYS:
        inner = parsed.get(key)
        if isinstance(inner, Mapping) and any(k in inner for k in _DA_SCHEMA_KEYS):
            return dict(inner)

    # If there's a single nested object, unwrap it if it contains DA keys.
    if len(parsed) == 1:
        only_value = next(iter(parsed.values()))
        if isinstance(only_value, Mapping) and any(k in only_value for k in _DA_SCHEMA_KEYS):
            return dict(only_value)

    # One-level scan for any nested object that contains DA keys.
    for value in parsed.values():
        if isinstance(value, Mapping) and any(k in value for k in _DA_SCHEMA_KEYS):
            return dict(value)

    return parsed


def _coerce_da_schema(parsed: dict) -> dict:
    """Best-effort normalization when the model returns an unexpected top-level JSON shape."""
    if not isinstance(parsed, dict):
        return {}

    parsed = _unwrap_da_payload(parsed)
    if not isinstance(parsed, dict):
        return {}

    # Map common synonym keys onto the expected schema.
    coerced = dict(parsed)
    for src, dst in _DA_SYNONYMS.items():
        if src in coerced and dst not in coerced:
            coerced[dst] = coerced[src]

    if any(k in coerced for k in _DA_SCHEMA_KEYS):
        return coerced

    items = coerced.get("items")
    if not isinstance(items, list) or not items:
        return coerced

    # If the model returned just a list of strings, treat it as a workup list.
    if all(isinstance(x, str) for x in items):
        return {"recommended_workup": items}

    dict_items = [x for x in items if isinstance(x, dict)]
    if len(dict_items) != len(items):
        return parsed

    keys: set[str] = set()
    for d in dict_items[:5]:
        keys.update(d.keys())

    if "claim" in keys or "counter_evidence" in keys:
        return {"challenges": dict_items}
    if {"why_dangerous", "supporting_signs", "rule_out_test"} & keys or "diagnosis" in keys:
        return {"must_not_miss": dict_items}

    return coerced


def _normalize_challenges(value: object) -> list[dict[str, str]]:
    if value is None:
        return []

    items = [value] if isinstance(value, Mapping) else value
    if isinstance(items, str):
        s = items.strip()
        return [{"claim": s, "counter_evidence": ""}] if s else []
    if not isinstance(items, list):
        return []

    out: list[dict[str, str]] = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, Mapping):
            d = dict(item)
            claim = str(d.get("claim") or d.get("challenge") or d.get("concern") or "").strip()
            counter = str(
                d.get("counter_evidence")
                or d.get("counterevidence")
                or d.get("counter_argument")
                or d.get("counterargument")
                or d.get("counter")
                or d.get("evidence_against")
                or ""
            ).strip()
            if claim or counter:
                out.append({"claim": claim, "counter_evidence": counter})
            continue

        s = str(item).strip()
        if s:
            out.append({"claim": s, "counter_evidence": ""})

    return out


def _normalize_must_not_miss(value: object) -> list[dict[str, str]]:
    if value is None:
        return []

    items = [value] if isinstance(value, Mapping) else value
    if isinstance(items, str):
        s = items.strip()
        return [{"diagnosis": s}] if s else []
    if not isinstance(items, list):
        return []

    out: list[dict[str, str]] = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, Mapping):
            d = dict(item)
            diagnosis = str(d.get("diagnosis") or d.get("dx") or d.get("differential") or "").strip()
            why = str(d.get("why_dangerous") or d.get("why") or d.get("danger") or "").strip()
            signs = str(d.get("supporting_signs") or d.get("evidence") or d.get("support") or "").strip()
            test = str(d.get("rule_out_test") or d.get("test") or d.get("rule_out") or "").strip()
            if diagnosis or why or signs or test:
                out.append(
                    {
                        "diagnosis": diagnosis,
                        "why_dangerous": why,
                        "supporting_signs": signs,
                        "rule_out_test": test,
                    }
                )
            continue

        s = str(item).strip()
        if s:
            out.append({"diagnosis": s})

    return out


def run(state: PipelineState) -> PipelineState:
    """Run the Devil's Advocate agent."""
    state["current_step"] = "devil_advocate"
    clinical = state["clinical_input"]
    diag_out = state.get("diagnostician_output")
    bias_out = state.get("bias_detector_output")

    image = clinical.get("image")

    if diag_out is None or bias_out is None:
        state["error"] = "Missing upstream agent outputs."
        return state

    if image is None:
        state["error"] = "No image provided for Devil's Advocate."
        return state

    try:
        diagnostician_analysis = diag_out.get("analysis") or diag_out.get("findings", "")
        prompt = DEVIL_ADVOCATE_USER.format(
            doctor_diagnosis=clinical["doctor_diagnosis"],
            clinical_context=clinical["clinical_context"],
            diagnostician_findings=diagnostician_analysis,
            bias_summary=_format_bias_summary(bias_out),
        )
        system_prompt = DEVIL_ADVOCATE_SYSTEM
        raw = medgemma_client.generate_with_image(prompt, image, system_prompt=system_prompt)
        parsed = _coerce_da_schema(parse_json_response(raw))

        challenges = _normalize_challenges(parsed.get("challenges"))
        must_not_miss = _normalize_must_not_miss(parsed.get("must_not_miss"))
        workup_raw = parsed.get("recommended_workup", [])
        normalized_workup: list[str] = []
        if isinstance(workup_raw, str):
            # Split a single workup string into bullet-like entries.
            workup_raw = [x.strip(" -\t") for x in workup_raw.replace(";", "\n").splitlines()]
        if isinstance(workup_raw, Mapping):
            workup_raw = [dict(workup_raw)]
        if isinstance(workup_raw, list):
            for item in workup_raw:
                if item is None:
                    continue
                if isinstance(item, str):
                    s = item.strip()
                elif isinstance(item, dict):
                    s = str(
                        item.get("test")
                        or item.get("name")
                        or item.get("action")
                        or item.get("workup")
                        or ""
                    ).strip()
                    if not s:
                        s = json.dumps(item, ensure_ascii=False)
                else:
                    s = str(item).strip()
                if s:
                    normalized_workup.append(s)
        # Deduplicate while preserving order.
        normalized_workup = list(dict.fromkeys(normalized_workup))

        # If the model returned an empty schema, retry once with a stricter instruction.
        if not (challenges or must_not_miss or normalized_workup):
            logger.warning("Devil's Advocate produced empty structured output; retrying once.")
            strict_system = (
                DEVIL_ADVOCATE_SYSTEM
                + "\n\nIMPORTANT: Do not return empty arrays. Provide at least 1 item in each list, "
                + "even if you must express uncertainty and suggest rule-out testing."
            )
            raw_retry = medgemma_client.generate_with_image(prompt, image, system_prompt=strict_system)
            parsed_retry = _coerce_da_schema(parse_json_response(raw_retry))
            challenges = _normalize_challenges(parsed_retry.get("challenges"))
            must_not_miss = _normalize_must_not_miss(parsed_retry.get("must_not_miss"))
            workup_retry = parsed_retry.get("recommended_workup", [])
            normalized_workup = []
            if isinstance(workup_retry, str):
                workup_retry = [x.strip(" -\t") for x in workup_retry.replace(";", "\n").splitlines()]
            if isinstance(workup_retry, Mapping):
                workup_retry = [dict(workup_retry)]
            if isinstance(workup_retry, list):
                for item in workup_retry:
                    if item is None:
                        continue
                    if isinstance(item, str):
                        s = item.strip()
                    elif isinstance(item, dict):
                        s = str(
                            item.get("test")
                            or item.get("name")
                            or item.get("action")
                            or item.get("workup")
                            or ""
                        ).strip()
                        if not s:
                            s = json.dumps(item, ensure_ascii=False)
                    else:
                        s = str(item).strip()
                    if s:
                        normalized_workup.append(s)
            normalized_workup = list(dict.fromkeys(normalized_workup))

        state["devils_advocate_output"] = {
            "challenges": challenges,
            "must_not_miss": must_not_miss,
            "recommended_workup": normalized_workup,
        }

    except Exception as e:
        logger.exception("Devil's Advocate agent failed")
        state["error"] = f"Devil's Advocate error: {e}"

    return state
