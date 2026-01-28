"""
Diagnostician agent: independent image analysis WITHOUT seeing the doctor's diagnosis.
Uses MedGemma 4B (multimodal) for detailed radiological analysis.
Outputs structured JSON.
"""

import logging
from agents.state import PipelineState
from agents.prompts import DIAGNOSTICIAN_SYSTEM, DIAGNOSTICIAN_USER
from agents.output_parser import parse_json_response
from models import medgemma_client

logger = logging.getLogger(__name__)


def run(state: PipelineState) -> PipelineState:
    """Run the Diagnostician agent."""
    state["current_step"] = "diagnostician"
    clinical = state["clinical_input"]
    image = clinical.get("image")

    if image is None:
        state["error"] = "No image provided."
        return state

    try:
        prompt = DIAGNOSTICIAN_USER.format(clinical_context=clinical["clinical_context"])
        raw = medgemma_client.generate_with_image(prompt, image, system_prompt=DIAGNOSTICIAN_SYSTEM)
        parsed = parse_json_response(raw)
        findings = parsed.get("findings", [])
        differentials = parsed.get("differential_diagnoses", [])
        if not isinstance(findings, list):
            findings = [findings] if findings else []
        if not isinstance(differentials, list):
            differentials = [differentials] if differentials else []

        findings_lines: list[str] = []
        for f in findings:
            if isinstance(f, dict):
                name = str(f.get("finding", "")).strip()
                desc = str(f.get("description", "")).strip()
                source = str(f.get("source", "")).strip()
                source_tag = f" [{source}]" if source else ""
                if name and desc:
                    findings_lines.append(f"- {name}{source_tag}: {desc}")
                elif name:
                    findings_lines.append(f"- {name}{source_tag}")
                elif desc:
                    findings_lines.append(f"- {desc}")
            else:
                s = str(f).strip()
                if s:
                    findings_lines.append(f"- {s}")

        differential_lines: list[str] = []
        for d in differentials:
            if isinstance(d, dict):
                name = str(d.get("diagnosis", "")).strip()
                reasoning = str(d.get("reasoning", "")).strip()
                if name and reasoning:
                    differential_lines.append(f"- {name}: {reasoning}")
                elif name:
                    differential_lines.append(f"- {name}")
                elif reasoning:
                    differential_lines.append(f"- {reasoning}")
            else:
                s = str(d).strip()
                if s:
                    differential_lines.append(f"- {s}")

        findings_text = "\n".join(findings_lines)
        differentials_text = "\n".join(differential_lines)
        analysis_parts: list[str] = []
        if findings_text:
            analysis_parts.append("Findings:\n" + findings_text)
        if differentials_text:
            analysis_parts.append("Differential diagnoses:\n" + differentials_text)
        analysis_text = "\n\n".join(analysis_parts).strip()
        state["diagnostician_output"] = {
            "analysis": analysis_text,
            "findings": findings_text,
            "findings_list": findings,
            "differential_diagnoses": differentials,
            "differentials_text": differentials_text,
        }

    except Exception as e:
        logger.exception("Diagnostician agent failed")
        state["error"] = f"Diagnostician error: {e}"

    return state
