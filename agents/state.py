"""
LangGraph state definition for the Diagnostic Devil's Advocate pipeline.
"""

from typing import Any, Optional
from typing_extensions import NotRequired, TypedDict
from PIL import Image


class ClinicalInput(TypedDict):
    """Raw input from the user."""
    image: Optional[Image.Image]
    doctor_diagnosis: str
    clinical_context: str  # age, sex, symptoms, history, etc.
    modality: NotRequired[str]  # "CXR" | "CT" | "Other"


class Finding(TypedDict, total=False):
    finding: str
    description: str


class DifferentialDiagnosis(TypedDict, total=False):
    diagnosis: str
    reasoning: str


class DiagnosticianOutput(TypedDict):
    """Independent analysis from the Diagnostician agent (does NOT see doctor's diagnosis)."""
    analysis: str  # formatted text for downstream agents
    findings: str  # findings-only text
    findings_list: list[Finding]  # structured findings
    differential_diagnoses: list[DifferentialDiagnosis]  # top differentials
    differentials_text: NotRequired[str]


class BiasDetectorOutput(TypedDict):
    """Bias analysis comparing doctor's diagnosis vs independent analysis."""
    identified_biases: list[dict[str, Any]]  # [{"type": str, "evidence": str, "severity": str}]
    discrepancy_summary: str
    missed_findings: list[str]
    consistency_check: list[dict[str, Any]]  # MedSigLIP sign verification results


class DevilsAdvocateOutput(TypedDict):
    """Adversarial challenge to the working diagnosis."""
    challenges: list[dict[str, Any]]  # [{"claim": str, "counter_evidence": str}]
    must_not_miss: list[dict[str, Any]]  # [{"diagnosis": str, "why_dangerous": str, "supporting_signs": str}]
    recommended_workup: list[str]


class AlternativeDiagnosis(TypedDict, total=False):
    diagnosis: str
    urgency: str  # "critical" | "high" | "moderate"
    evidence: str
    next_step: str


class ConsultantOutput(TypedDict):
    """Final synthesized consultation note."""
    consultation_note: str
    alternative_diagnoses: list[AlternativeDiagnosis]
    immediate_actions: list[str]
    confidence_note: str


class PipelineState(TypedDict):
    """Full state passed through the LangGraph pipeline."""
    # Input
    clinical_input: ClinicalInput

    # Agent outputs (populated as pipeline progresses)
    diagnostician_output: Optional[DiagnosticianOutput]
    bias_detector_output: Optional[BiasDetectorOutput]
    devils_advocate_output: Optional[DevilsAdvocateOutput]
    consultant_output: Optional[ConsultantOutput]

    # Metadata
    current_step: str
    error: Optional[str]
