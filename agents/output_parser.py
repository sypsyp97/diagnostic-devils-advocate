"""
JSON output parser for LLM responses.
Uses json_repair for malformed JSON, and llm_output_parser as fallback
to extract JSON from mixed text/markdown LLM output.
"""

import logging
from collections.abc import Mapping
from json_repair import repair_json
from llm_output_parser import parse_json as extract_json

logger = logging.getLogger(__name__)

_TOP_LEVEL_KEYS = {
    # Diagnostician
    "findings",
    "differential_diagnoses",
    # Bias detector
    "discrepancy_summary",
    "identified_biases",
    "missed_findings",
    "agreement_points",
    # Devil's advocate
    "challenges",
    "must_not_miss",
    "recommended_workup",
    # Consultant
    "consultation_note",
    "alternative_diagnoses",
    "immediate_actions",
    "confidence_note",
}


def parse_json_response(text: str) -> dict:
    """
    Extract and repair JSON from an LLM response.
    Handles: raw JSON, ```json blocks, missing commas, truncated output, etc.
    Returns parsed dict. Raises ValueError if repair fails completely.
    """
    result = repair_json(text, return_objects=True)

    # Typical (desired) case: top-level object.
    if isinstance(result, Mapping):
        return dict(result)

    # Some model outputs come back as a top-level array. Coerce to a dict so
    # downstream code can continue, while preserving the payload for callers to
    # interpret (via 'items') when schema keys are missing.
    if isinstance(result, list):
        return _coerce_list_root(result)

    # Fallback: json_repair returned a plain string (model output natural language).
    # Use llm_output_parser to extract JSON from mixed text/markdown.
    if isinstance(result, str):
        logger.warning("json_repair returned str, trying llm_output_parser extraction")
        extracted = extract_json(text, allow_incomplete=True, strict=False)
        if isinstance(extracted, Mapping):
            return dict(extracted)
        if isinstance(extracted, list):
            return _coerce_list_root(extracted)

    raise ValueError(
        f"Could not parse JSON from LLM output (got {type(result).__name__}, length={len(text)})"
    )


def _coerce_list_root(items: list) -> dict:
    if not items:
        return {"items": []}

    mapping_items = [x for x in items if isinstance(x, Mapping)]
    if not mapping_items:
        return {"items": items}

    merged: dict = {}
    contains_top_level_key = False
    for m in mapping_items:
        d = dict(m)
        contains_top_level_key = contains_top_level_key or bool(_TOP_LEVEL_KEYS.intersection(d.keys()))
        merged.update(d)

    # If the extracted objects already contain known top-level schema keys, it's
    # likely a wrapped/duplicated object (or multiple partial objects). Merge.
    if contains_top_level_key:
        return merged

    all_mappings = len(mapping_items) == len(items)
    if all_mappings:
        # Distinguish between (a) a true list of repeated schema items, vs (b)
        # multiple standalone JSON objects extracted from a noisy response.
        key_sets = [set(dict(m).keys()) for m in mapping_items[:10]]
        union = set().union(*key_sets)
        intersection = set(key_sets[0]).intersection(*key_sets[1:]) if len(key_sets) > 1 else set(key_sets[0])
        overlap_ratio = (len(intersection) / len(union)) if union else 0.0

        if len(items) == 1 or overlap_ratio >= 0.35:
            inferred_key = _infer_list_container_key(mapping_items)
            if inferred_key:
                return {inferred_key: [dict(m) for m in mapping_items]}
            return {"items": [dict(m) for m in mapping_items]}

        # Low overlap between objects: treat as multiple extracted JSON objects.
        return merged

    # Mixed list: preserve non-mapping items, but coerce mappings to dict.
    coerced = [dict(x) if isinstance(x, Mapping) else x for x in items]
    return {"items": coerced}


def _infer_list_container_key(items: list[Mapping]) -> str | None:
    keys: set[str] = set()
    for item in items[:5]:
        keys.update(str(k) for k in item.keys())

    # Diagnostician
    if {"finding", "description"} & keys:
        return "findings"
    if "reasoning" in keys:
        return "differential_diagnoses"

    # Bias detector
    if {"type", "severity"} <= keys or ("type" in keys and "severity" in keys):
        return "identified_biases"

    # Devil's advocate
    if "claim" in keys or "counter_evidence" in keys:
        return "challenges"
    if {"why_dangerous", "rule_out_test", "supporting_signs"} & keys:
        return "must_not_miss"

    # Consultant
    if {"urgency", "next_step"} & keys:
        return "alternative_diagnoses"

    return None
