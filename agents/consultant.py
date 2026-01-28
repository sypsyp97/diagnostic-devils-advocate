"""
Consultant agent: synthesizes all upstream outputs into a collegial debiasing report.
Outputs structured JSON.
"""

import json
import logging

from agents.state import PipelineState
from agents.prompts import CONSULTANT_SYSTEM, CONSULTANT_USER
from agents.output_parser import parse_json_response
from models import medgemma_client

logger = logging.getLogger(__name__)


def _format_bias_report(bias_out: dict) -> str:
    """Format bias detector output as text for the Consultant prompt."""
    parts = []
    if bias_out.get("discrepancy_summary"):
        parts.append(f"Discrepancy: {bias_out['discrepancy_summary']}")
    for b in bias_out.get("identified_biases", []):
        parts.append(f"- [{b.get('severity','?').upper()}] {b.get('type','')}: {b.get('evidence','')}")
    if bias_out.get("missed_findings"):
        parts.append(f"Missed: {', '.join(bias_out['missed_findings'])}")
    return "\n".join(parts) if parts else "No bias data."


def _format_da_report(da_out: dict) -> str:
    """Format devil's advocate output as text for the Consultant prompt."""
    parts = []
    for c in da_out.get("challenges", []):
        parts.append(f"Challenge: {c.get('claim','')} → {c.get('counter_evidence','')}")
    for m in da_out.get("must_not_miss", []):
        parts.append(f"MUST-NOT-MISS: {m.get('diagnosis','')} — {m.get('why_dangerous','')}")
    if da_out.get("recommended_workup"):
        items = [str(w) if not isinstance(w, dict) else w.get("test", str(w)) for w in da_out["recommended_workup"]]
        parts.append("Workup: " + ", ".join(items))
    return "\n".join(parts) if parts else "No challenges raised."


def run(state: PipelineState) -> PipelineState:
    """Run the Consultant agent."""
    state["current_step"] = "consultant"
    clinical = state["clinical_input"]
    diag_out = state.get("diagnostician_output")
    bias_out = state.get("bias_detector_output")
    da_out = state.get("devils_advocate_output")

    if diag_out is None or bias_out is None or da_out is None:
        state["error"] = "Missing upstream agent outputs."
        return state

    try:
        diagnostician_analysis = diag_out.get("analysis") or diag_out.get("findings", "")
        prompt = CONSULTANT_USER.format(
            doctor_diagnosis=clinical["doctor_diagnosis"],
            clinical_context=clinical["clinical_context"],
            diagnostician_findings=diagnostician_analysis,
            bias_report=_format_bias_report(bias_out),
            devil_advocate_report=_format_da_report(da_out),
            similar_cases="Not available.",
        )
        raw = medgemma_client.generate_text(prompt, system_prompt=CONSULTANT_SYSTEM)
        parsed = parse_json_response(raw)

        alternative_diagnoses = parsed.get("alternative_diagnoses", [])
        if isinstance(alternative_diagnoses, str):
            try:
                alternative_diagnoses = json.loads(alternative_diagnoses)
            except json.JSONDecodeError:
                alternative_diagnoses = []
        if not isinstance(alternative_diagnoses, list):
            alternative_diagnoses = []

        immediate_actions = parsed.get("immediate_actions", [])
        if isinstance(immediate_actions, str):
            immediate_actions = [immediate_actions]
        if not isinstance(immediate_actions, list):
            immediate_actions = []
        immediate_actions = [str(x).strip() for x in immediate_actions if str(x).strip()]

        state["consultant_output"] = {
            "consultation_note": parsed.get("consultation_note", ""),
            "alternative_diagnoses": alternative_diagnoses,
            "immediate_actions": immediate_actions,
            "confidence_note": parsed.get("confidence_note", ""),
        }

    except Exception as e:
        logger.exception("Consultant agent failed")
        state["error"] = f"Consultant error: {e}"

    return state
