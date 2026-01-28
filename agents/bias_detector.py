"""
Bias Detector agent: compares doctor's diagnosis with independent analysis to identify cognitive biases.
Runs MedSigLIP sign verification on imaging findings mentioned by the Diagnostician.
Outputs structured JSON.
"""

import json
import logging
from agents.state import PipelineState
from agents.prompts import BIAS_DETECTOR_SYSTEM, BIAS_DETECTOR_USER
from agents.output_parser import parse_json_response
from models import medgemma_client, medsiglip_client

logger = logging.getLogger(__name__)

_SIGN_EXTRACTION_PROMPT = """\
Extract radiological signs (imaging abnormalities) from the following diagnostic findings.
Return ONLY a JSON array of short sign names.
Rules:
- Only include imaging abnormalities that could be visually verified on a medical image.
- Do NOT include normal anatomical structures, abstract diagnoses, clinical impressions, or treatment recommendations.
- Maximum 8 signs. If more exist, keep the most clinically significant ones.
- Return an empty array [] if no signs are found.

Findings:
{findings_text}"""


def _extract_signs(findings: object) -> list[str]:
    """Extract signs from findings using MedGemma."""
    if isinstance(findings, list):
        chunks: list[str] = []
        for item in findings:
            if isinstance(item, dict):
                chunks.append(str(item.get("finding", "")))
                chunks.append(str(item.get("description", "")))
            else:
                chunks.append(str(item))
        findings_text = "\n".join(chunks)
    else:
        findings_text = str(findings)

    if not findings_text.strip():
        return []

    try:
        raw = medgemma_client.generate_text(
            _SIGN_EXTRACTION_PROMPT.format(findings_text=findings_text),
        )
        parsed = json.loads(raw.strip().strip("`").removeprefix("json").strip())
        if isinstance(parsed, list):
            return [str(s).strip().lower() for s in parsed if isinstance(s, str)][:8]
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("LLM sign extraction failed, raw output: %s — %s", raw, e)

    return []


def run(state: PipelineState) -> PipelineState:
    """Run the Bias Detector agent."""
    state["current_step"] = "bias_detector"
    clinical = state["clinical_input"]
    diag_out = state.get("diagnostician_output")

    if diag_out is None:
        state["error"] = "Diagnostician output missing."
        return state

    try:
        # 1. MedSigLIP: verify imaging signs mentioned in findings
        sign_verification = []
        image = clinical.get("image")
        if image is not None:
            signs = _extract_signs(diag_out.get("findings_list") or diag_out.get("findings", ""))
            logger.info("Extracted signs for SigLIP verification: %s", signs)
            if signs:
                sign_verification = medsiglip_client.verify_findings(
                    image,
                    signs,
                    modality=clinical.get("modality"),
                )

        # 2. MedGemma: cognitive bias analysis (with image if available)
        diagnostician_analysis = diag_out.get("analysis") or diag_out.get("findings", "")
        prompt = BIAS_DETECTOR_USER.format(
            doctor_diagnosis=clinical["doctor_diagnosis"],
            clinical_context=clinical["clinical_context"],
            diagnostician_findings=diagnostician_analysis,
            consistency_check=_format_sign_verification(sign_verification),
        )
        if image is not None:
            raw = medgemma_client.generate_with_image(prompt, image, system_prompt=BIAS_DETECTOR_SYSTEM)
        else:
            raw = medgemma_client.generate_text(prompt, system_prompt=BIAS_DETECTOR_SYSTEM)
        parsed = parse_json_response(raw)
        state["bias_detector_output"] = {
            "identified_biases": parsed.get("identified_biases", []),
            "discrepancy_summary": parsed.get("discrepancy_summary", ""),
            "missed_findings": parsed.get("missed_findings", []),
            "consistency_check": sign_verification,
        }

    except Exception as e:
        logger.exception("Bias Detector agent failed")
        state["error"] = f"Bias Detector error: {e}"

    return state


def _format_sign_verification(results: list[dict]) -> str:
    """Format sign verification results as text for the MedGemma prompt."""
    if not results:
        return "No image verification available."

    # Only include non-inconclusive results
    meaningful = [r for r in results if r.get("confidence") != "inconclusive"]
    if not meaningful:
        return "Image verification inconclusive for all findings."

    lines = ["Image sign verification (MedSigLIP):"]
    for r in meaningful:
        lines.append(f"- {r['sign']}: {r['confidence']}")
    return "\n".join(lines)
