"""Gradio UI layout for Diagnostic Devil's Advocate."""

import gradio as gr
from config import ENABLE_MEDASR


def build_ui(analyze_fn, load_demo_fn, transcribe_fn=None):
    """
    Build the Gradio Blocks UI.

    Args:
        analyze_fn: generator(image, diagnosis, context, modality) -> yields HTML
        load_demo_fn: callback(demo_name) -> (image, diagnosis, context, modality)
        transcribe_fn: callback(audio, existing_context) -> yields (context, status_html) (optional)
    """
    with gr.Blocks(title="Diagnostic Devil's Advocate") as demo:

        # ── Hero Banner ──
        gr.HTML(
            """
            <div class="hero-banner">
                <div class="hero-badge">MedGemma Impact Challenge</div>
                <h1>Diagnostic Devil's Advocate</h1>
                <p class="hero-sub">AI-Powered Cognitive Debiasing for Medical Image Interpretation</p>
                <p class="hero-desc">Upload a medical image with the working diagnosis.
                   Four AI agents will independently analyze it, detect cognitive biases,
                   challenge the diagnosis, and synthesize a debiasing report.</p>
                <div class="hero-models">
                    <span class="model-chip">MedGemma 1.5</span>
                    <span class="model-chip">MedSigLIP</span>
                    <span class="model-chip">LangGraph</span>
                    <span class="model-chip">MedASR</span>
                </div>
            </div>
            """
        )

        # ── Demo Cases Row (3 clickable cards) ──
        gr.HTML('<div class="section-label">SELECT A DEMO CASE</div>')

        with gr.Row(elem_classes=["case-row"]):
            demo_btn_1 = gr.Button(
                value="",
                elem_id="case-btn-1",
                elem_classes=["case-card-btn"],
            )
            demo_btn_2 = gr.Button(
                value="",
                elem_id="case-btn-2",
                elem_classes=["case-card-btn"],
            )
            demo_btn_3 = gr.Button(
                value="",
                elem_id="case-btn-3",
                elem_classes=["case-card-btn"],
            )

        # Overlay HTML on top of buttons for card visuals
        gr.HTML("""
        <div class="case-cards-overlay">
            <div class="case-card case-card-pneumo" onclick="document.querySelector('#case-btn-1').click()">
                <div class="card-top">
                    <span class="case-icon">🫁</span>
                    <span class="case-tag tag-blue">TRAUMA</span>
                </div>
                <div class="case-title">Missed Pneumothorax</div>
                <div class="case-meta">32-year-old Male</div>
                <div class="case-desc">Motorcycle collision · Left chest pain · HR 104 · SpO₂ 96%</div>
                <div class="case-misdiag">
                    <span class="misdiag-label">Initial Dx:</span>
                    <span class="misdiag-value">Rib contusion</span>
                </div>
            </div>
            <div class="case-card case-card-aorta" onclick="document.querySelector('#case-btn-2').click()">
                <div class="card-top">
                    <span class="case-icon">🫀</span>
                    <span class="case-tag tag-red">VASCULAR</span>
                </div>
                <div class="case-title">Aortic Dissection</div>
                <div class="case-meta">58-year-old Male</div>
                <div class="case-desc">Sudden chest→back pain · BP asymmetry 32mmHg · D-dimer 4850</div>
                <div class="case-misdiag">
                    <span class="misdiag-label">Initial Dx:</span>
                    <span class="misdiag-value">GERD / Reflux</span>
                </div>
            </div>
            <div class="case-card case-card-pe" onclick="document.querySelector('#case-btn-3').click()">
                <div class="card-top">
                    <span class="case-icon">🩸</span>
                    <span class="case-tag tag-purple">POSTPARTUM</span>
                </div>
                <div class="case-title">Pulmonary Embolism</div>
                <div class="case-meta">29-year-old Female</div>
                <div class="case-desc">5 days post C-section · HR 118 · SpO₂ 91% · pO₂ 68</div>
                <div class="case-misdiag">
                    <span class="misdiag-label">Initial Dx:</span>
                    <span class="misdiag-value">Postpartum anxiety</span>
                </div>
            </div>
        </div>
        """)

        # ── Main Content: Input + Output ──
        with gr.Row(equal_height=False):

            # ═══════════ Left Column: Input ═══════════
            with gr.Column(scale=4, min_width=340):
                gr.HTML('<div class="section-label">CLINICAL INPUT</div>')

                image_input = gr.Image(
                    type="pil",
                    label="Medical Image",
                    height=240,
                )
                modality_input = gr.Radio(
                    choices=["CXR", "CT", "Other"],
                    value="CXR",
                    label="Imaging Modality",
                )
                diagnosis_input = gr.Textbox(
                    label="Doctor's Working Diagnosis",
                    placeholder="e.g., Left rib contusion with musculoskeletal chest wall pain",
                )
                context_input = gr.Textbox(
                    label="Clinical Context (history, vitals, labs, exam)",
                    placeholder=(
                        "e.g., 32M, motorcycle accident, left-sided chest pain, "
                        "HR 104, SpO2 96%, WBC 11.2..."
                    ),
                    lines=5,
                )

                # ── Voice Input (MedASR) ──
                if ENABLE_MEDASR and transcribe_fn:
                    gr.HTML("""
                    <div class="voice-section">
                        <div class="voice-header">
                            <span class="voice-icon">🎙️</span>
                            <span class="voice-title">Voice Input</span>
                            <span class="voice-badge">MedASR</span>
                        </div>
                        <div class="voice-hint">Record clinical context with your microphone.
                            Text will be appended to the context field above.</div>
                    </div>
                    """)
                    with gr.Row(elem_classes=["voice-row"]):
                        audio_input = gr.Audio(
                            sources=["microphone"],
                            type="numpy",
                            label="",
                            show_label=False,
                            elem_classes=["voice-audio"],
                        )
                        with gr.Column(scale=1, min_width=160):
                            transcribe_btn = gr.Button(
                                "Transcribe",
                                size="sm",
                                elem_classes=["transcribe-btn"],
                            )
                            voice_status = gr.HTML(
                                value='<div class="voice-status voice-idle">Ready to record</div>',
                            )
                else:
                    gr.HTML(
                        '<div class="voice-status voice-idle">Voice input disabled (MedASR)</div>'
                    )

                analyze_btn = gr.Button(
                    "Analyze & Challenge Diagnosis",
                    variant="primary",
                    size="lg",
                    elem_classes=["analyze-btn"],
                )

            # ═══════════ Right Column: Pipeline Output ═══════════
            with gr.Column(scale=6, min_width=500):

                gr.HTML('<div class="section-label">PIPELINE OUTPUT</div>')
                pipeline_output = gr.HTML(
                    value=_initial_progress_html(),
                )

        # ── Footer ──
        gr.HTML(
            """
            <div class="footer-text">
                <span>Built with</span>
                <span class="footer-chip">MedGemma</span>
                <span class="footer-chip">MedSigLIP</span>
                <span class="footer-chip">LangGraph</span>
                <span class="footer-chip">Gradio</span>
                <span class="footer-sep">|</span>
                <span>MedGemma Impact Challenge 2025</span>
                <span class="footer-sep">|</span>
                <span>Research & educational use only</span>
            </div>
            """
        )

        # ═══════════ Wire Callbacks ═══════════

        analyze_btn.click(
            fn=analyze_fn,
            inputs=[image_input, diagnosis_input, context_input, modality_input],
            outputs=[pipeline_output],
        )

        demo_btn_1.click(
            fn=lambda: load_demo_fn("Case 1: Missed Pneumothorax"),
            inputs=[],
            outputs=[image_input, diagnosis_input, context_input, modality_input],
        )
        demo_btn_2.click(
            fn=lambda: load_demo_fn("Case 2: Aortic Dissection"),
            inputs=[],
            outputs=[image_input, diagnosis_input, context_input, modality_input],
        )
        demo_btn_3.click(
            fn=lambda: load_demo_fn("Case 3: Pulmonary Embolism"),
            inputs=[],
            outputs=[image_input, diagnosis_input, context_input, modality_input],
        )

        # Voice transcription — outputs to context field + status indicator
        if ENABLE_MEDASR and transcribe_fn:
            transcribe_btn.click(
                fn=transcribe_fn,
                inputs=[audio_input, context_input],
                outputs=[context_input, voice_status],
            )

    return demo


def _initial_progress_html() -> str:
    """Static initial progress bar HTML."""
    return _build_progress_html([], None, None, {})


def _build_progress_html(
    completed: list[str],
    active: str | None,
    error: str | None,
    agent_outputs: dict[str, str] | None = None,
) -> str:
    """Build pipeline output: progress bar + each agent's result inline.

    Args:
        agent_outputs: {agent_id: html_content} for completed agents.
    """
    if agent_outputs is None:
        agent_outputs = {}

    agents = [
        ("diagnostician", "Diagnostician", "Independent image analysis"),
        ("bias_detector", "Bias Detector", "Cognitive bias identification"),
        ("devil_advocate", "Devil's Advocate", "Adversarial challenge"),
        ("consultant", "Consultant", "Consultation synthesis"),
    ]

    n_done = len(completed)
    pct = int(n_done / len(agents) * 100)

    bar_color = "#ef4444" if error else "#3b82f6"
    html = f"""
    <div class="progress-container">
        <div class="progress-bar-track">
            <div class="progress-bar-fill" style="width:{pct}%;background:{bar_color};">
                {pct}%
            </div>
        </div>
        <div class="pipeline-agents">
    """

    for agent_id, name, desc in agents:
        if agent_id == error:
            cls = "step-error"
            icon = "✗"
            status = "Failed"
        elif agent_id in completed:
            cls = "step-done"
            icon = "✓"
            status = "Complete"
        elif agent_id == active:
            cls = "step-active"
            icon = "⟳"
            status = desc
        else:
            cls = "step-waiting"
            icon = "○"
            status = "Waiting"

        content = agent_outputs.get(agent_id, "")
        if content:
            # Collapsible: <details open> with header as <summary>
            html += f"""
        <details class="agent-block {cls}" open>
            <summary class="agent-header">
                <span class="step-icon">{icon}</span>
                <span class="step-name">{name}</span>
                <span class="step-status">{status}</span>
            </summary>
            <div class="agent-output">{content}</div>
        </details>"""
        else:
            # No output yet — just show the header (not collapsible)
            html += f"""
        <div class="agent-block {cls}">
            <div class="agent-header">
                <span class="step-icon">{icon}</span>
                <span class="step-name">{name}</span>
                <span class="step-status">{status}</span>
            </div>
        </div>"""

    html += "</div></div>"
    return html
