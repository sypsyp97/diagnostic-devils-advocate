"""Callbacks connecting UI events to the LangGraph pipeline."""

import json
import logging
import os
import numpy as np
from PIL import Image

from agents.graph import stream_pipeline
from config import DEMO_CASES_DIR, ENABLE_MEDASR

# ZeroGPU support: use @spaces.GPU when running on HF Spaces, no-op locally
try:
    import spaces
    SPACES_AVAILABLE = True
except ImportError:
    SPACES_AVAILABLE = False


def gpu_decorator(duration: int = 180):
    """Decorator that uses @spaces.GPU on HF Spaces, no-op locally."""
    def decorator(fn):
        if SPACES_AVAILABLE:
            return spaces.GPU(duration=duration)(fn)
        return fn
    return decorator

logger = logging.getLogger(__name__)

# Agent display info
AGENT_INFO = {
    "diagnostician": ("Diagnostician", "Analyzing image independently..."),
    "bias_detector": ("Bias Detector", "Scanning for cognitive biases..."),
    "devil_advocate": ("Devil's Advocate", "Challenging the diagnosis..."),
    "consultant": ("Consultant", "Synthesizing consultation report..."),
}

# Demo case definitions — based on published case reports and clinical literature.
# References:
#   Case 1: PMC3195099 (AP CXR vs CT in trauma pneumothorax detection)
#   Case 2: PMC6203039 (Acute aortic dissection: a missed diagnosis)
#   Case 3: PMC10683049 (PE masked by symptoms of mental disorders)
DEMO_CASES = {
    "Case 1: Missed Pneumothorax": {
        "diagnosis": "Left rib contusion with musculoskeletal chest wall pain",
        "context": (
            "32-year-old male, presented to ED after a motorcycle collision at ~40 mph. "
            "Helmet worn, no LOC. Chief complaint: left-sided chest pain worse with deep "
            "inspiration.\n\n"
            "Vitals: HR 104 bpm, BP 132/84 mmHg, RR 22/min, SpO2 96% on room air, "
            "Temp 37.1 C.\n\n"
            "Exam: Tenderness over left 4th-6th ribs, no crepitus, no subcutaneous "
            "emphysema palpated. Breath sounds reportedly equal bilaterally (noisy ED). "
            "Mild dyspnea attributed to pain.\n\n"
            "Labs: WBC 11.2, Hgb 14.1, Lactate 1.8 mmol/L.\n\n"
            "ED physician ordered AP chest X-ray (supine) — read as 'no acute "
            "cardiopulmonary abnormality, possible left rib fracture.' Patient was given "
            "ibuprofen and discharged with rib fracture precautions."
        ),
        "image_file": "case1_pneumothorax.png",
        "modality": "CXR",
    },
    "Case 2: Aortic Dissection": {
        "diagnosis": "Acute gastroesophageal reflux / esophageal spasm",
        "context": (
            "58-year-old male with a 15-year history of hypertension (poorly controlled, "
            "non-compliant with amlodipine). Presented to ED with sudden-onset severe "
            "retrosternal chest pain radiating to the interscapular back region, starting "
            "30 minutes ago.\n\n"
            "Vitals: BP 178/102 mmHg (right arm), 146/88 mmHg (left arm), HR 92 bpm, "
            "RR 20/min, SpO2 97%, Temp 37.0 C.\n\n"
            "Exam: Diaphoretic, visibly distressed. Abdomen soft, mild epigastric "
            "tenderness. Heart sounds normal, no murmur. Peripheral pulses intact but "
            "radial pulse asymmetry noted.\n\n"
            "Labs: Troponin I <0.01 (negative x2 at 0h and 3h), D-dimer 4,850 ng/mL "
            "(markedly elevated), WBC 13.4, Creatinine 1.3.\n\n"
            "ECG: Sinus tachycardia, nonspecific ST changes. Initial CXR ordered. "
            "ED physician considered ACS (ruled out by troponin), then attributed symptoms "
            "to acid reflux; prescribed IV pantoprazole and GI cocktail. Pain not relieved."
        ),
        "image_file": "case2_aortic_dissection.png",
        "modality": "CXR",
    },
    "Case 3: Pulmonary Embolism": {
        "diagnosis": "Postpartum anxiety with hyperventilation syndrome",
        "context": (
            "29-year-old female, G2P2, day 5 after emergency cesarean section (prolonged "
            "labor, general anesthesia). Presented with acute onset dyspnea and chest "
            "tightness at rest. Reports feeling of 'impending doom' and inability to catch "
            "breath.\n\n"
            "Vitals: HR 118 bpm, BP 108/72 mmHg, RR 28/min, SpO2 91% on room air "
            "(improved to 95% on 4L NC), Temp 37.3 C.\n\n"
            "Exam: Anxious-appearing, tachypneic. Lungs clear to auscultation. Mild "
            "right-sided pleuritic chest pain. Right calf tenderness and mild swelling "
            "noted but attributed to post-surgical immobility. No Homan sign.\n\n"
            "Labs: D-dimer 3,200 ng/mL (elevated, but 'expected postpartum'), "
            "WBC 10.8, Hgb 10.2, ABG on RA: pH 7.48, pO2 68 mmHg, pCO2 29 mmHg.\n\n"
            "OB team attributed symptoms to postpartum anxiety, prescribed lorazepam "
            "0.5 mg PRN. Psychiatry consult requested. No CTPA ordered initially."
        ),
        "image_file": "case3_pulmonary_embolism.png",
        "modality": "CXR",
    },
}


@gpu_decorator(duration=600)
def analyze_streaming(image: Image.Image | None, diagnosis: str, context: str, modality: str):
    """
    Generator: run pipeline and yield single HTML output after each agent step.
    Each agent's output appears inline below its progress header.
    Uses @spaces.GPU on HF Spaces for ZeroGPU support.
    """
    if image is None:
        yield '<div class="pipeline-error">Please upload a medical image.</div>'
        return
    if not diagnosis.strip():
        yield '<div class="pipeline-error">Please enter the doctor\'s working diagnosis.</div>'
        return
    if not context.strip():
        context = "No additional clinical context provided."
    if not isinstance(modality, str) or not modality.strip():
        modality = "CXR"

    completed = {}
    agent_outputs = {}
    all_agents = ["diagnostician", "bias_detector", "devil_advocate", "consultant"]

    try:
        yield _build_pipeline(all_agents, completed, agent_outputs, active="diagnostician")

        accumulated_state = {}
        for node_name, state_update in stream_pipeline(image, diagnosis.strip(), context.strip(), modality.strip()):
            completed[node_name] = True
            accumulated_state.update(state_update)

            if state_update.get("error"):
                agent_outputs[node_name] = f'<div class="pipeline-error">{_esc(state_update.get("error"))}</div>'
                yield _build_pipeline(all_agents, completed, agent_outputs, error=node_name)
                return

            # Generate this agent's HTML output
            agent_outputs[node_name] = _format_agent_output(node_name, accumulated_state)

            idx = all_agents.index(node_name) if node_name in all_agents else -1
            next_active = all_agents[idx + 1] if idx + 1 < len(all_agents) else None

            yield _build_pipeline(all_agents, completed, agent_outputs, active=next_active)

    except Exception as e:
        logger.exception("Pipeline failed")
        yield f'<div class="pipeline-error">Pipeline error: {_esc(e)}</div>'


def _build_pipeline(all_agents, completed, agent_outputs, active=None, error=None) -> str:
    """Build combined progress + inline output HTML."""
    from ui.components import _build_progress_html
    return _build_progress_html(
        completed=list(completed.keys()),
        active=active,
        error=error,
        agent_outputs=agent_outputs,
    )


def _format_agent_output(agent_id: str, state: dict) -> str:
    """Generate HTML content for a specific agent's output."""
    if agent_id == "diagnostician":
        return _format_diagnostician(state)
    elif agent_id == "bias_detector":
        return _format_bias_detector(state)
    elif agent_id == "devil_advocate":
        return _format_devil_advocate(state)
    elif agent_id == "consultant":
        return _format_consultant(state)
    return ""


def _esc(text: object) -> str:
    """Escape HTML special characters."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _format_diagnostician(state: dict) -> str:
    diag = state.get("diagnostician_output") or {}
    parts = []

    # Structured findings
    findings_list = diag.get("findings_list", [])
    if findings_list:
        items = []
        for f in findings_list:
            if isinstance(f, dict):
                name = _esc(f.get("finding", ""))
                desc = _esc(f.get("description", ""))
                source = f.get("source", "").strip().lower()
                source_tag = ""
                if source in ("imaging", "clinical", "both"):
                    source_tag = f' <span class="source-tag source-{source}">{_esc(source)}</span>'
                line = f"<li><strong>{name}</strong>{source_tag}: {desc}</li>" if desc else f"<li>{name}{source_tag}</li>"
                items.append(line)
            else:
                items.append(f"<li>{_esc(str(f))}</li>")
        parts.append(f'<div class="findings-section"><strong>Findings</strong><ul>{"".join(items)}</ul></div>')

    # Differential diagnoses
    differentials = diag.get("differential_diagnoses", [])
    if differentials:
        items = []
        for d in differentials:
            if isinstance(d, dict):
                name = _esc(d.get("diagnosis", ""))
                reason = _esc(d.get("reasoning", ""))
                items.append(f"<li><strong>{name}</strong>: {reason}</li>" if reason else f"<li>{name}</li>")
            else:
                items.append(f"<li>{_esc(str(d))}</li>")
        parts.append(f'<div class="differentials-section"><strong>Differential Diagnoses</strong><ol>{"".join(items)}</ol></div>')

    # Fallback: raw text if no structured data
    if not parts:
        raw = diag.get("findings", "")
        if raw:
            parts.append(f'<div class="agent-text">{_esc(raw).replace(chr(10), "<br>")}</div>')

    return "".join(parts)


def _format_bias_detector(state: dict) -> str:
    bias_out = state.get("bias_detector_output") or {}
    parts = []

    # Discrepancy summary (always show if present)
    disc = bias_out.get("discrepancy_summary", "")
    if disc:
        parts.append(f'<div class="discrepancy-summary">{_esc(disc)}</div>')

    # Biases
    biases = bias_out.get("identified_biases", [])
    for b in biases:
        severity = b.get("severity", "").strip().lower()
        bias_type = _esc(b.get("type", "Unknown"))
        evidence = _esc(b.get("evidence", ""))
        source = b.get("source", "").strip().lower()
        if severity in ("low", "medium", "high"):
            sev_tag = f'<span class="severity-tag severity-{severity}">{severity.upper()}</span>'
        else:
            sev_tag = ""
        if source in ("doctor", "ai", "both"):
            src_tag = f'<span class="source-tag source-{source}">{source.upper()}</span>'
        else:
            src_tag = ""
        parts.append(
            f'<div class="bias-item">'
            f'<div class="bias-title">{sev_tag} {src_tag} {bias_type}</div>'
            f'<div class="bias-evidence">{evidence}</div>'
            f'</div>'
        )

    # Missed findings
    missed = bias_out.get("missed_findings", [])
    if missed:
        items = "".join(f"<li>{_esc(f)}</li>" for f in missed)
        parts.append(f'<div class="missed-findings"><strong>Missed Findings</strong><ul>{items}</ul></div>')

    # SigLIP sign verification
    sign_results = bias_out.get("consistency_check", [])
    if isinstance(sign_results, list) and sign_results:
        meaningful = [r for r in sign_results if r.get("confidence") != "inconclusive"]
        if meaningful:
            items = []
            for r in meaningful:
                conf = r.get("confidence", "?")
                sign = _esc(r.get("sign", "?"))
                css_cls = "sign-present" if "present" in conf else "sign-absent"
                items.append(f'<li class="{css_cls}"><strong>{sign}</strong> — {conf}</li>')
            parts.append(
                f'<div class="siglip-section">'
                f'<strong>Image Verification (MedSigLIP)</strong>'
                f'<ul>{"".join(items)}</ul>'
                f'</div>'
            )

    return "".join(parts)


def _format_devil_advocate(state: dict) -> str:
    da_out = state.get("devils_advocate_output") or {}
    parts = []

    # Must-not-miss
    mnm = da_out.get("must_not_miss", [])
    for m in mnm:
        dx = _esc(m.get("diagnosis", "?"))
        why = _esc(m.get("why_dangerous", ""))
        signs = _esc(m.get("supporting_signs", ""))
        test = _esc(m.get("rule_out_test", ""))
        details = ""
        if why:
            details += f"<li><strong>Why dangerous:</strong> {why}</li>"
        if signs:
            details += f"<li><strong>Supporting signs:</strong> {signs}</li>"
        if test:
            details += f"<li><strong>Rule-out test:</strong> {test}</li>"
        parts.append(
            f'<div class="mnm-item">'
            f'<div class="mnm-title">{dx}</div>'
            f'<ul>{details}</ul>'
            f'</div>'
        )

    # Challenges
    challenges = da_out.get("challenges", [])
    if challenges:
        for c in challenges:
            claim = _esc(c.get("claim", ""))
            counter = _esc(c.get("counter_evidence", ""))
            parts.append(
                f'<div class="challenge-item">'
                f'<div class="challenge-claim">{claim}</div>'
                f'<div class="challenge-counter">{counter}</div>'
                f'</div>'
            )

    # Recommended workup
    workup = da_out.get("recommended_workup", [])
    if workup:
        items = "".join(f"<li>{_esc(str(w))}</li>" for w in workup)
        parts.append(f'<div class="workup-section"><strong>Recommended Workup</strong><ul>{items}</ul></div>')

    # Fallback: ensure non-empty so the collapsible block can expand
    if not parts:
        parts.append('<div class="agent-text">No structured challenges parsed.</div>')

    return "".join(parts)


def _format_consultant(state: dict) -> str:
    ref = state.get("consultant_output") or {}
    da_out = state.get("devils_advocate_output") or {}
    parts = []

    # Consultation note — the main human-readable report
    note = ref.get("consultation_note", "")
    if note:
        paragraphs = _esc(note).split("\n")
        formatted = "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
        parts.append(f'<div class="consultation-note">{formatted}</div>')

    # Alternative diagnoses to consider
    alt_raw = ref.get("alternative_diagnoses", "")
    if alt_raw:
        try:
            alts = json.loads(alt_raw) if isinstance(alt_raw, str) else alt_raw
            if not isinstance(alts, list):
                alts = []
            if alts:
                items = []
                for a in alts:
                    urgency_raw = str(a.get("urgency", "")).strip().lower()
                    urgency = urgency_raw if urgency_raw in {"critical", "high", "moderate"} else "moderate"
                    urgency_label = urgency.upper()
                    dx = _esc(a.get("diagnosis", "?"))
                    ev = _esc(a.get("evidence", ""))
                    ns = _esc(a.get("next_step", ""))
                    detail = f" — {ev}" if ev else ""
                    step = f"<br><em>Next step: {ns}</em>" if ns else ""
                    items.append(
                        f'<li><span class="urgency-tag urgency-{urgency}">{urgency_label}</span> '
                        f"<strong>{dx}</strong>{detail}{step}</li>"
                    )
                parts.append(f'<div class="alt-diagnoses"><strong>Consider</strong><ul>{"".join(items)}</ul></div>')
        except (json.JSONDecodeError, TypeError):
            pass

    # Immediate actions (merged from Devil's Advocate + Consultant)
    workup = da_out.get("recommended_workup", []) if isinstance(da_out, dict) else []
    actions = ref.get("immediate_actions", [])
    safe_workup = [str(x).strip() for x in workup if str(x).strip()]
    safe_actions = [str(x).strip() for x in actions if str(x).strip()]
    all_items = list(dict.fromkeys(safe_workup + safe_actions))
    if all_items:
        items = "".join(f"<li>{_esc(item)}</li>" for item in all_items)
        parts.append(f'<div class="next-steps"><strong>Recommended Actions</strong><ul>{items}</ul></div>')

    # Confidence note
    if ref.get("confidence_note"):
        parts.append(f'<div class="confidence-note"><em>{_esc(ref["confidence_note"])}</em></div>')

    return "".join(parts)


@gpu_decorator(duration=60)
def transcribe_audio(audio, existing_context: str = ""):
    """
    Transcribe audio input using MedASR.

    Generator that yields (context_text, status_html) for streaming UI feedback.
    Appends transcribed text to any existing context.
    Uses @spaces.GPU on HF Spaces for ZeroGPU support.
    """
    def _status_html(cls: str, text: str) -> str:
        return f'<div class="voice-status {cls}">{text}</div>'

    if audio is None:
        yield existing_context, _status_html("voice-idle", "No audio recorded. Click the microphone to start.")
        return

    if not ENABLE_MEDASR:
        yield existing_context, _status_html("voice-error", "MedASR is disabled (set ENABLE_MEDASR=true)")
        return

    # Step 1: Show processing state
    sr, audio_data = audio
    duration = len(audio_data) / sr if sr > 0 else 0
    yield existing_context, _status_html(
        "voice-processing",
        f'<span class="pulse-dot"></span> Transcribing {duration:.1f}s of audio with MedASR...'
    )

    try:
        from models import medasr_client

        # Convert to float32 mono
        if audio_data.dtype != np.float32:
            if np.issubdtype(audio_data.dtype, np.integer):
                audio_data = audio_data.astype(np.float32) / np.iinfo(audio_data.dtype).max
            else:
                audio_data = audio_data.astype(np.float32)
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        # Resample to 16kHz if needed (MedASR expects 16000Hz)
        target_sr = 16000
        if sr != target_sr:
            from scipy.signal import resample
            num_samples = int(len(audio_data) * target_sr / sr)
            audio_data = resample(audio_data, num_samples).astype(np.float32)
            sr = target_sr

        # Step 2: Run transcription
        text = medasr_client.transcribe(audio_data, sampling_rate=sr)

        if not text.strip():
            yield existing_context, _status_html("voice-error", "No speech detected. Please try again.")
            return

        # Step 3: Append to existing context
        if existing_context.strip():
            new_context = existing_context.rstrip() + "\n\n" + text
        else:
            new_context = text

        word_count = len(text.split())
        yield new_context, _status_html(
            "voice-success",
            f'✓ Transcribed {word_count} words ({duration:.1f}s) — text added to context above'
        )

    except Exception as e:
        logger.exception("MedASR transcription failed")
        yield existing_context, _status_html("voice-error", f"Transcription failed: {e}")


def load_demo(demo_name: str | None):
    """Load a demo case into the UI inputs."""
    if demo_name is None or demo_name not in DEMO_CASES:
        return None, "", "", "CXR"

    case = DEMO_CASES[demo_name]
    image_path = os.path.join(DEMO_CASES_DIR, case["image_file"])

    image = None
    if os.path.exists(image_path):
        image = Image.open(image_path)
    else:
        logger.warning("Demo image not found: %s", image_path)

    modality = case.get("modality") or "CXR"
    return image, case["diagnosis"], case["context"], modality
