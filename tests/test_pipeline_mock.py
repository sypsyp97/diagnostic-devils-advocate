"""End-to-end pipeline test with mocked model calls (no GPU required)."""

import os
import sys
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_pipeline_end_to_end_with_mocks():
    from agents.graph import run_pipeline
    from agents.prompts import (
        DIAGNOSTICIAN_SYSTEM,
        BIAS_DETECTOR_SYSTEM,
        DEVIL_ADVOCATE_SYSTEM,
        CONSULTANT_SYSTEM,
    )

    dummy_image = Image.new("RGB", (512, 512), color="gray")

    diagnostician_json = """
    {
      "findings": [
        {"finding": "Pneumothorax", "source": "imaging", "description": "Left apical pleural line with absent peripheral markings."},
        {"finding": "Rib fracture", "source": "imaging", "description": "Possible fracture of the left 5th rib."},
        {"finding": "Tachycardia", "source": "clinical", "description": "HR 104, consistent with pain or hemodynamic compromise."}
      ],
      "differential_diagnoses": [
        {"diagnosis": "Pneumothorax", "reasoning": "Visible pleural line on imaging combined with tachycardia and dyspnea from clinical context."}
      ]
    }
    """.strip()

    bias_detector_json = """
    {
      "discrepancy_summary": "Doctor focused on rib pain; image suggests pneumothorax.",
      "identified_biases": [
        {"type": "Anchoring", "evidence": "Trauma mechanism overweighted", "severity": "HIGH"}
      ],
      "missed_findings": ["Pneumothorax"],
      "agreement_points": ["Rib pain consistent with trauma"]
    }
    """.strip()

    devil_advocate_json = """
    {
      "challenges": [
        {"claim": "Rib contusion explains symptoms", "counter_evidence": "Dyspnea can reflect pneumothorax severity."}
      ],
      "must_not_miss": [
        {
          "diagnosis": "Tension pneumothorax",
          "why_dangerous": "Rapid hemodynamic collapse if untreated",
          "supporting_signs": "Worsening dyspnea and pleural line",
          "rule_out_test": "Bedside ultrasound or repeat upright CXR"
        }
      ],
      "recommended_workup": ["Repeat upright chest radiograph", "Point-of-care ultrasound"]
    }
    """.strip()

    consultant_json = """
    {
      "consultation_note": "Have you considered pneumothorax given the pleural line?\\n\\nI would re-image upright and consider bedside ultrasound.",
      "alternative_diagnoses": [
        {
          "diagnosis": "Pneumothorax",
          "urgency": "high",
          "evidence": "Pleural line and absent peripheral markings",
          "next_step": "Repeat upright CXR or POCUS"
        }
      ],
      "immediate_actions": ["Repeat upright CXR", "POCUS"],
      "confidence_note": "Based on a single image; clinical correlation required."
    }
    """.strip()

    def fake_generate_with_image(_prompt: str, _image, system_prompt: str = "") -> str:
        if system_prompt == DIAGNOSTICIAN_SYSTEM:
            return diagnostician_json
        if system_prompt == BIAS_DETECTOR_SYSTEM:
            return bias_detector_json
        if system_prompt.startswith(DEVIL_ADVOCATE_SYSTEM):
            return devil_advocate_json
        raise AssertionError(f"Unexpected system_prompt (with image): {system_prompt!r}")

    def fake_generate_text(_prompt: str, system_prompt: str = "") -> str:
        if system_prompt == CONSULTANT_SYSTEM:
            return consultant_json
        raise AssertionError(f"Unexpected system_prompt: {system_prompt!r}")

    with patch("models.medgemma_client.generate_with_image", side_effect=fake_generate_with_image), patch(
        "models.medgemma_client.generate_text",
        side_effect=fake_generate_text,
    ), patch(
        "models.medsiglip_client.verify_findings",
        return_value=[{"sign": "pneumothorax", "confidence": "likely present"}],
    ):
        result = run_pipeline(
            image=dummy_image,
            doctor_diagnosis="Rib contusion",
            clinical_context="32M, trauma, left chest pain, mild dyspnea.",
            modality="CXR",
        )

    assert result.get("error") is None

    diag = result.get("diagnostician_output") or {}
    assert diag.get("findings_list"), "Diagnostician findings_list missing"
    assert diag.get("analysis"), "Diagnostician analysis missing"

    bias = result.get("bias_detector_output") or {}
    assert bias.get("discrepancy_summary")
    assert bias.get("identified_biases"), "Bias detector identified_biases missing"

    da = result.get("devils_advocate_output") or {}
    assert da.get("must_not_miss"), "Devil's advocate must_not_miss missing"
    assert all(isinstance(x, str) for x in da.get("recommended_workup", []))

    ref = result.get("consultant_output") or {}
    assert ref.get("consultation_note")
    assert isinstance(ref.get("alternative_diagnoses"), list)
