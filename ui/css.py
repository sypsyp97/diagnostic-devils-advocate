"""Custom CSS for the Diagnostic Devil's Advocate UI."""

CUSTOM_CSS = """
/* ===== Global ===== */
.gradio-container {
    max-width: 1320px !important;
    margin: 0 auto !important;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow-x: hidden;
}

/* ===== Hero Banner ===== */
.hero-banner {
    text-align: center !important;
    padding: 36px 28px 24px !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #0f3460 100%) !important;
    color: #fff !important;
    margin-bottom: 22px !important;
    box-shadow: 0 4px 28px rgba(0, 0, 0, 0.2) !important;
    position: relative !important;
    overflow: hidden !important;
}
.hero-banner::after {
    content: '' !important;
    position: absolute !important;
    top: -50% !important;
    right: -20% !important;
    width: 400px !important;
    height: 400px !important;
    background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%) !important;
    pointer-events: none !important;
}
.hero-badge {
    display: inline-block !important;
    padding: 4px 14px !important;
    border-radius: 20px !important;
    background: rgba(59, 130, 246, 0.2) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
    color: #93c5fd !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    margin-bottom: 12px !important;
}
.hero-banner h1 {
    margin: 0 0 8px !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.8px !important;
    color: #fff !important;
    border: none !important;
}
.hero-sub {
    margin: 0 0 6px !important;
    font-size: 1.02rem !important;
    color: #93c5fd !important;
    font-weight: 500 !important;
}
.hero-desc {
    margin: 0 auto !important;
    font-size: 0.86rem !important;
    color: #94a3b8 !important;
    max-width: 660px !important;
    line-height: 1.55 !important;
}
.hero-models {
    margin-top: 16px !important;
    display: flex !important;
    justify-content: center !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
}
.model-chip {
    display: inline-block !important;
    padding: 3px 12px !important;
    border-radius: 6px !important;
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #cbd5e1 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
}

/* ===== Section Label ===== */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin: 16px 0 10px;
    padding-left: 2px;
}

/* ===== Demo Case: Hidden buttons ===== */
.case-row {
    height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
}
.case-card-btn {
    opacity: 0 !important;
    position: absolute !important;
    pointer-events: none !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ===== Demo Case Cards (overlay, clickable) ===== */
.case-cards-overlay {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 14px;
    margin-bottom: 20px;
}
.case-card {
    border-radius: 14px;
    padding: 18px 16px 14px;
    background: #fff;
    border: 1.5px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.22s ease;
    position: relative;
    overflow: hidden;
}
.case-card:hover {
    border-color: #93c5fd;
    box-shadow: 0 6px 24px rgba(59, 130, 246, 0.12);
    transform: translateY(-3px);
}
.case-card:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}
.case-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
}
.case-card-pneumo::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.case-card-aorta::before  { background: linear-gradient(90deg, #ef4444, #f87171); }
.case-card-pe::before     { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }

.card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.case-icon { font-size: 1.8rem; }
.case-tag {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 3px 8px;
    border-radius: 5px;
    text-transform: uppercase;
}
.tag-blue   { background: #dbeafe; color: #1d4ed8; }
.tag-red    { background: #fee2e2; color: #b91c1c; }
.tag-purple { background: #f3e8ff; color: #7c3aed; }

.case-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 2px;
}
.case-meta {
    font-size: 0.78rem;
    color: #64748b;
    margin-bottom: 6px;
}
.case-desc {
    font-size: 0.74rem;
    color: #94a3b8;
    line-height: 1.4;
    margin-bottom: 10px;
}
.case-misdiag {
    padding-top: 8px;
    border-top: 1px solid #f1f5f9;
    font-size: 0.74rem;
}
.misdiag-label {
    color: #94a3b8;
}
.misdiag-value {
    color: #dc2626;
    font-weight: 700;
}

/* ===== Voice Input Section ===== */
.voice-section {
    margin-top: 12px;
    padding: 12px 14px 8px;
    background: linear-gradient(135deg, #fafbff 0%, #f0f4ff 100%);
    border: 1.5px solid #dbeafe;
    border-radius: 12px 12px 0 0;
    border-bottom: none;
}
.voice-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}
.voice-icon { font-size: 1.2rem; }
.voice-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #1e293b;
}
.voice-badge {
    font-size: 0.6rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    background: #dbeafe;
    color: #1d4ed8;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.voice-hint {
    font-size: 0.74rem;
    color: #94a3b8;
    line-height: 1.4;
}
.voice-row {
    gap: 10px !important;
    align-items: stretch !important;
    margin-bottom: 6px !important;
}
.voice-audio {
    border-radius: 0 0 0 12px !important;
}
.transcribe-btn {
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: 1.5px solid #3b82f6 !important;
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    transition: all 0.15s ease !important;
}
.transcribe-btn:hover {
    background: #dbeafe !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15) !important;
}

/* Voice status indicators */
.voice-status {
    font-size: 0.76rem;
    padding: 6px 10px;
    border-radius: 8px;
    margin-top: 6px;
    text-align: center;
    line-height: 1.4;
}
.voice-idle {
    background: #f8fafc;
    color: #94a3b8;
    border: 1px solid #e2e8f0;
}
.voice-processing {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}
.voice-success {
    background: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
    font-weight: 600;
}
.voice-error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

/* Pulsing dot for processing state */
.pulse-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #3b82f6;
    animation: pulse-dot-anim 1s ease-in-out infinite;
}
@keyframes pulse-dot-anim {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.7); }
}

/* ===== Analyze Button ===== */
.analyze-btn {
    width: 100% !important;
    border-radius: 12px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 14px !important;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    transition: all 0.2s ease !important;
    margin-top: 10px !important;
    letter-spacing: -0.2px !important;
}
.analyze-btn:hover {
    box-shadow: 0 6px 24px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-2px) !important;
}

/* ===== Progress Bar ===== */
.progress-container {
    margin: 4px 0 8px;
}
.progress-bar-track {
    height: 28px;
    background: #f1f5f9;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 14px;
    border: 1px solid #e2e8f0;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 14px;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: width 0.6s ease;
    min-width: 0;
}
/* ===== Pipeline Agent Blocks ===== */
.pipeline-agents {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
details.agent-block,
div.agent-block {
    border-radius: 12px;
    border: 1px solid transparent;
    box-sizing: border-box;
    width: 100%;
    min-width: 0;
    overflow-x: hidden;
}
details.agent-block > summary {
    list-style: none;
    cursor: pointer;
    user-select: none;
}
details.agent-block > summary::-webkit-details-marker {
    display: none;
}
details.agent-block > summary::after {
    content: '▾';
    font-size: 0.7rem;
    color: #94a3b8;
    margin-left: 6px;
    transition: transform 0.2s ease;
}
details.agent-block:not([open]) > summary::after {
    transform: rotate(-90deg);
}
.agent-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
}
div.agent-block .agent-header {
    cursor: default;
}
.step-icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-size: 0.82rem;
    font-weight: 700;
    flex-shrink: 0;
}
.step-name {
    font-size: 0.88rem;
    font-weight: 700;
}
.step-status {
    font-size: 0.72rem;
    margin-left: auto;
}

/* Agent output area */
.agent-output {
    padding: 4px 14px 14px;
    font-size: 0.84rem;
    line-height: 1.6;
    color: #334155;
    border-top: 1px solid rgba(0,0,0,0.06);
    overflow: hidden;
    overflow-wrap: break-word;
    overflow-wrap: anywhere;
    word-break: break-word;
}
.agent-output * {
    max-width: 100%;
    box-sizing: border-box;
}
.agent-output pre,
.agent-output code {
    max-width: 100%;
    white-space: pre-wrap;
    word-break: break-word;
}
.agent-output ul {
    margin: 6px 0;
    padding-left: 18px;
}
.agent-output li {
    margin-bottom: 4px;
}
.agent-text {
    overflow-wrap: break-word;
    word-break: break-word;
}
.agent-output details summary {
    cursor: pointer;
    color: #475569;
}
.findings-section,
.differentials-section {
    margin-bottom: 6px;
}
.findings-section strong,
.differentials-section strong {
    color: #1e293b;
}
.differentials-section ol {
    margin: 6px 0;
    padding-left: 22px;
}

/* Step states */
.step-done {
    background: #f0fdf4;
    border-color: #bbf7d0;
}
.step-done .step-icon {
    background: #22c55e;
    color: #fff;
}
.step-done .step-name { color: #166534; }
.step-done .step-status { color: #4ade80; }

.step-active {
    background: #eff6ff;
    border-color: #bfdbfe;
    animation: pulse-border 2s ease-in-out infinite;
}
.step-active .step-icon {
    background: #3b82f6;
    color: #fff;
    animation: spin 1.2s linear infinite;
}
.step-active .step-name { color: #1d4ed8; }
.step-active .step-status { color: #60a5fa; }

.step-waiting {
    background: #f8fafc;
    border-color: #f1f5f9;
}
.step-waiting .step-icon {
    background: #e2e8f0;
    color: #94a3b8;
}
.step-waiting .step-name { color: #94a3b8; }
.step-waiting .step-status { color: #cbd5e1; }

.step-error {
    background: #fef2f2;
    border-color: #fecaca;
}
.step-error .step-icon {
    background: #ef4444;
    color: #fff;
}
.step-error .step-name { color: #991b1b; }
.step-error .step-status { color: #f87171; }

@keyframes pulse-border {
    0%, 100% { border-color: #bfdbfe; }
    50% { border-color: #60a5fa; }
}
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* ===== Agent Output Styling ===== */

/* Bias Detector */
.discrepancy-summary {
    padding: 8px 12px;
    margin-bottom: 10px;
    background: #fff7ed;
    border-radius: 8px;
    border: 1px solid #fed7aa;
    color: #9a3412;
    font-size: 0.84rem;
    line-height: 1.5;
}
.bias-item {
    margin-bottom: 10px;
    padding: 8px 12px;
    background: #fffbeb;
    border-left: 3px solid #f59e0b;
    border-radius: 0 8px 8px 0;
}
.bias-title {
    font-weight: 700;
    color: #92400e;
    margin-bottom: 4px;
}
.bias-evidence {
    color: #78716c;
    font-size: 0.82rem;
}
.severity-tag {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-right: 4px;
    vertical-align: middle;
}
.severity-high { background: #fee2e2; color: #dc2626; }
.severity-medium { background: #fff7ed; color: #ea580c; }
.severity-low { background: #fefce8; color: #ca8a04; }

.source-tag {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-right: 4px;
    vertical-align: middle;
}
.source-doctor { background: #dbeafe; color: #1d4ed8; }
.source-ai { background: #ede9fe; color: #7c3aed; }
.source-both { background: #e0e7ff; color: #4338ca; }
.source-imaging { background: #dbeafe; color: #1d4ed8; }
.source-clinical { background: #fef3c7; color: #b45309; }

.missed-findings {
    margin-top: 8px;
    padding: 8px 12px;
    background: #fef2f2;
    border-radius: 8px;
}
.missed-findings strong {
    color: #991b1b;
}

/* SigLIP */
.siglip-section {
    margin-top: 8px;
    padding: 8px 12px;
    background: #f0f9ff;
    border-radius: 8px;
}
.siglip-section strong {
    color: #0369a1;
}
.sign-present {
    color: #166534;
}
.sign-absent {
    color: #94a3b8;
}

/* Devil's Advocate */
.mnm-item {
    margin-bottom: 10px;
    padding: 8px 12px;
    background: #fef2f2;
    border-left: 3px solid #ef4444;
    border-radius: 0 8px 8px 0;
}
.mnm-title {
    font-weight: 700;
    color: #991b1b;
    font-size: 0.92rem;
}
.mnm-item ul {
    margin-top: 4px;
}
.challenge-item {
    margin-bottom: 8px;
    padding: 8px 12px;
    background: #faf5ff;
    border-left: 3px solid #8b5cf6;
    border-radius: 0 8px 8px 0;
}
.challenge-claim {
    font-weight: 700;
    color: #5b21b6;
    margin-bottom: 2px;
}
.challenge-counter {
    color: #6b7280;
    font-size: 0.82rem;
}

/* Consultant */
.consultation-note {
    padding: 12px 16px;
    background: linear-gradient(135deg, #f8fafc, #f0f9ff);
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    color: #1e293b;
    font-size: 0.86rem;
    line-height: 1.65;
    margin-bottom: 10px;
}
.consultation-note p {
    margin: 0 0 8px;
}
.consultation-note p:last-child {
    margin-bottom: 0;
}
.alt-diagnoses {
    margin-bottom: 8px;
}
.urgency-tag {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    vertical-align: middle;
}
.urgency-critical { background: #fee2e2; color: #dc2626; }
.urgency-high { background: #fff7ed; color: #ea580c; }
.urgency-moderate { background: #fefce8; color: #ca8a04; }
.urgency-unknown { background: #e2e8f0; color: #475569; }
.next-steps {
    margin-bottom: 8px;
}
.confidence-note {
    padding: 8px 12px;
    background: #f8fafc;
    border-radius: 8px;
    color: #64748b;
    font-size: 0.8rem;
}

/* Pipeline error */
.pipeline-error {
    padding: 14px;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    color: #991b1b;
    font-weight: 600;
}

/* ===== Footer ===== */
.footer-text {
    text-align: center;
    padding: 18px;
    margin-top: 24px;
    font-size: 0.76rem;
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    flex-wrap: wrap;
}
.footer-chip {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 4px;
    background: #f1f5f9;
    color: #475569;
    font-weight: 600;
    font-size: 0.72rem;
}
.footer-sep {
    color: #cbd5e1;
    margin: 0 2px;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
    .gradio-container { max-width: 100% !important; }
    .hero-banner h1 { font-size: 1.5rem; }
    .case-cards-overlay { grid-template-columns: 1fr; }
}

/* ===== Dark Mode ===== */
/* Using .dark class selector (Gradio/HF) + media query fallback */
.dark .section-label,
:root.dark .section-label {
    color: #94a3b8;
}

/* Case Cards */
.dark .case-card,
:root.dark .case-card {
    background: #1e293b;
    border-color: #334155;
}
.dark .case-card:hover,
:root.dark .case-card:hover {
    border-color: #60a5fa;
    box-shadow: 0 6px 24px rgba(59, 130, 246, 0.2);
}
.dark .case-title,
:root.dark .case-title {
    color: #f1f5f9;
}
.dark .case-meta,
:root.dark .case-meta {
    color: #94a3b8;
}
.dark .case-desc,
:root.dark .case-desc {
    color: #64748b;
}
.dark .case-misdiag,
:root.dark .case-misdiag {
    border-top-color: #334155;
}
.dark .misdiag-label,
:root.dark .misdiag-label {
    color: #64748b;
}
.dark .misdiag-value,
:root.dark .misdiag-value {
    color: #f87171;
}

/* Tags in dark mode */
.dark .tag-blue, :root.dark .tag-blue { background: #1e3a5f; color: #60a5fa; }
.dark .tag-red, :root.dark .tag-red { background: #450a0a; color: #fca5a5; }
.dark .tag-purple, :root.dark .tag-purple { background: #2e1065; color: #c4b5fd; }

/* Voice Section */
.dark .voice-section,
:root.dark .voice-section {
    background: linear-gradient(135deg, #1e293b 0%, #1e3a5f 100%);
    border-color: #334155;
}
.dark .voice-title,
:root.dark .voice-title {
    color: #f1f5f9;
}
.dark .voice-badge,
:root.dark .voice-badge {
    background: #1e3a5f;
    color: #60a5fa;
}
.dark .voice-hint,
:root.dark .voice-hint {
    color: #64748b;
}
.dark .transcribe-btn,
:root.dark .transcribe-btn {
    background: #1e3a5f !important;
    border-color: #3b82f6 !important;
    color: #60a5fa !important;
}
.dark .transcribe-btn:hover,
:root.dark .transcribe-btn:hover {
    background: #1d4ed8 !important;
    color: #fff !important;
}

/* Voice status indicators */
.dark .voice-idle,
:root.dark .voice-idle {
    background: #1e293b;
    color: #64748b;
    border-color: #334155;
}
.dark .voice-processing,
:root.dark .voice-processing {
    background: #1e3a5f;
    color: #60a5fa;
    border-color: #3b82f6;
}
.dark .voice-success,
:root.dark .voice-success {
    background: #14532d;
    color: #4ade80;
    border-color: #22c55e;
}
.dark .voice-error,
:root.dark .voice-error {
    background: #450a0a;
    color: #fca5a5;
    border-color: #ef4444;
}

/* Progress Bar */
.dark .progress-bar-track,
:root.dark .progress-bar-track {
    background: #1e293b;
    border-color: #334155;
}

/* Agent Blocks */
.dark .step-done,
:root.dark .step-done {
    background: #14532d;
    border-color: #22c55e;
}
.dark .step-done .step-name, :root.dark .step-done .step-name { color: #4ade80; }
.dark .step-done .step-status, :root.dark .step-done .step-status { color: #22c55e; }

.dark .step-active,
:root.dark .step-active {
    background: #1e3a5f;
    border-color: #3b82f6;
}
.dark .step-active .step-name, :root.dark .step-active .step-name { color: #60a5fa; }
.dark .step-active .step-status, :root.dark .step-active .step-status { color: #3b82f6; }

.dark .step-waiting,
:root.dark .step-waiting {
    background: #1e293b;
    border-color: #334155;
}
.dark .step-waiting .step-icon,
:root.dark .step-waiting .step-icon {
    background: #334155;
    color: #64748b;
}
.dark .step-waiting .step-name, :root.dark .step-waiting .step-name { color: #64748b; }
.dark .step-waiting .step-status, :root.dark .step-waiting .step-status { color: #475569; }

.dark .step-error,
:root.dark .step-error {
    background: #450a0a;
    border-color: #ef4444;
}
.dark .step-error .step-name, :root.dark .step-error .step-name { color: #fca5a5; }
.dark .step-error .step-status, :root.dark .step-error .step-status { color: #ef4444; }

/* Agent Output */
.dark .agent-output,
:root.dark .agent-output {
    color: #cbd5e1;
    border-top-color: rgba(255,255,255,0.08);
}
.dark .agent-output details summary,
:root.dark .agent-output details summary {
    color: #94a3b8;
}
.dark .findings-section strong,
.dark .differentials-section strong,
:root.dark .findings-section strong,
:root.dark .differentials-section strong {
    color: #f1f5f9;
}

/* Bias Detector */
.dark .discrepancy-summary,
:root.dark .discrepancy-summary {
    background: #431407;
    border-color: #c2410c;
    color: #fed7aa;
}
.dark .bias-item,
:root.dark .bias-item {
    background: #422006;
    border-left-color: #f59e0b;
}
.dark .bias-title,
:root.dark .bias-title {
    color: #fcd34d;
}
.dark .bias-evidence,
:root.dark .bias-evidence {
    color: #a8a29e;
}
.dark .missed-findings,
:root.dark .missed-findings {
    background: #450a0a;
}
.dark .missed-findings strong,
:root.dark .missed-findings strong {
    color: #fca5a5;
}

/* Severity tags */
.dark .severity-high, :root.dark .severity-high { background: #450a0a; color: #fca5a5; }
.dark .severity-medium, :root.dark .severity-medium { background: #431407; color: #fdba74; }
.dark .severity-low, :root.dark .severity-low { background: #422006; color: #fde047; }

/* Source tags */
.dark .source-doctor, :root.dark .source-doctor { background: #1e3a5f; color: #60a5fa; }
.dark .source-ai, :root.dark .source-ai { background: #2e1065; color: #c4b5fd; }
.dark .source-both, :root.dark .source-both { background: #312e81; color: #a5b4fc; }
.dark .source-imaging, :root.dark .source-imaging { background: #1e3a5f; color: #60a5fa; }
.dark .source-clinical, :root.dark .source-clinical { background: #422006; color: #fcd34d; }

/* SigLIP */
.dark .siglip-section,
:root.dark .siglip-section {
    background: #0c4a6e;
}
.dark .siglip-section strong,
:root.dark .siglip-section strong {
    color: #7dd3fc;
}
.dark .sign-present,
:root.dark .sign-present {
    color: #4ade80;
}
.dark .sign-absent,
:root.dark .sign-absent {
    color: #64748b;
}

/* Devil's Advocate */
.dark .mnm-item,
:root.dark .mnm-item {
    background: #450a0a;
    border-left-color: #ef4444;
}
.dark .mnm-title,
:root.dark .mnm-title {
    color: #fca5a5;
}
.dark .challenge-item,
:root.dark .challenge-item {
    background: #2e1065;
    border-left-color: #8b5cf6;
}
.dark .challenge-claim,
:root.dark .challenge-claim {
    color: #c4b5fd;
}
.dark .challenge-counter,
:root.dark .challenge-counter {
    color: #9ca3af;
}

/* Consultant */
.dark .consultation-note,
:root.dark .consultation-note {
    background: linear-gradient(135deg, #1e293b, #0c4a6e);
    border-color: #334155;
    color: #e2e8f0;
}
.dark .urgency-critical, :root.dark .urgency-critical { background: #450a0a; color: #fca5a5; }
.dark .urgency-high, :root.dark .urgency-high { background: #431407; color: #fdba74; }
.dark .urgency-moderate, :root.dark .urgency-moderate { background: #422006; color: #fde047; }
.dark .urgency-unknown, :root.dark .urgency-unknown { background: #334155; color: #94a3b8; }
.dark .confidence-note,
:root.dark .confidence-note {
    background: #1e293b;
    color: #94a3b8;
}

/* Pipeline error */
.dark .pipeline-error,
:root.dark .pipeline-error {
    background: #450a0a;
    border-color: #ef4444;
    color: #fca5a5;
}

/* Footer */
.dark .footer-text,
:root.dark .footer-text {
    color: #64748b;
    border-top-color: #334155;
}
.dark .footer-chip,
:root.dark .footer-chip {
    background: #334155;
    color: #94a3b8;
}
.dark .footer-sep,
:root.dark .footer-sep {
    color: #475569;
}

/* Media query fallback for system dark mode */
@media (prefers-color-scheme: dark) {
    .section-label { color: #94a3b8; }
    .case-card { background: #1e293b; border-color: #334155; }
    .case-title { color: #f1f5f9; }
    .case-meta { color: #94a3b8; }
    .case-desc { color: #64748b; }
    .progress-bar-track { background: #1e293b; border-color: #334155; }
    .agent-output { color: #cbd5e1; }
    .footer-text { color: #64748b; border-top-color: #334155; }
    .footer-chip { background: #334155; color: #94a3b8; }
}
"""
