---
title: Diagnostic Devil's Advocate
emoji: "\U0001FA7A"
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: "5.12.0"
app_file: app.py
pinned: false
license: cc-by-4.0
tags:
  - medgemma
  - medical-imaging
  - multi-agent
  - cognitive-bias
  - radiology
---

<div align="center">

# 🩺 Diagnostic Devil's Advocate

### AI-Powered Cognitive Debiasing for Clinical Diagnosis

**A multi-agent system that challenges medical diagnoses to catch what doctors might miss.**

[![MedGemma](https://img.shields.io/badge/MedGemma-4B%20%7C%2027B-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://huggingface.co/google/medgemma-1.5-4b-it)
[![MedSigLIP](https://img.shields.io/badge/MedSigLIP-448-34A853?style=for-the-badge&logo=google&logoColor=white)](https://huggingface.co/google/medsiglip-448)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Pipeline-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Gradio](https://img.shields.io/badge/Gradio-UI-F97316?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app)

[Live Demo](#getting-started) &bull; [Architecture](#architecture) &bull; [Demo Cases](#demo-cases) &bull; [Technical Details](#technical-details)

---

</div>

## The Problem

> *Diagnostic errors affect an estimated **12 million** adults annually in the U.S. alone, with cognitive biases — [anchoring](https://en.wikipedia.org/wiki/Anchoring_(cognitive_bias)), [premature closure](https://en.wikipedia.org/wiki/Premature_closure), [confirmation bias](https://en.wikipedia.org/wiki/Confirmation_bias) — implicated in up to **74%** of cases.* ([Singh et al., BMJ Quality & Safety, 2014](https://qualitysafety.bmj.com/content/23/9/727))

Doctors are not wrong because they lack knowledge. They are wrong because the human brain takes shortcuts — and in medicine, shortcuts kill. A physician who sees "young patient + chest pain after trauma" anchors on **rib contusion** and stops looking. The pneumothorax on the X-ray goes unseen. The patient deteriorates.

**Diagnostic Devil's Advocate** is a system that acts as an adversarial second opinion. It does not replace the physician — it challenges them. It asks: *"Have you considered what happens if you're wrong?"*

## How It Works

The system runs a **4-agent pipeline** orchestrated by [LangGraph](https://langchain-ai.github.io/langgraph/) where each agent has a distinct adversarial role. Every agent analyzes **both the medical image and the full clinical context** (history, vitals, labs, exam findings) — because some dangerous conditions (aortic dissection, pulmonary embolism) may show subtle or no imaging signs but have obvious clinical red flags. Critically, the first agent does this **without seeing the doctor's diagnosis**, preventing the AI itself from being [anchored](https://en.wikipedia.org/wiki/Anchoring_(cognitive_bias)).

### The Four Agents

| Agent | Role | Model | Key Design Choice |
|:------|:-----|:------|:------------------|
| **Diagnostician** | Independent image + clinical analysis | [MedGemma 4B-IT](https://huggingface.co/google/medgemma-1.5-4b-it) (multimodal) | **Blinded** — never sees the doctor's diagnosis. Tags each finding as `imaging`, `clinical`, or `both` to distinguish evidence sources. |
| **Bias Detector** | Compare doctor vs. AI findings | [MedGemma 4B-IT](https://huggingface.co/google/medgemma-1.5-4b-it) + [MedSigLIP](https://huggingface.co/google/medsiglip-448) | Uses **zero-shot image classification** to verify radiological signs. Flags clinical red flags ignored by either assessment. |
| **Devil's Advocate** | Adversarial challenge | [MedGemma 4B-IT](https://huggingface.co/google/medgemma-1.5-4b-it) | Deliberately contrarian — uses both imaging and clinical evidence to argue for **[must-not-miss diagnoses](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6775443/)** |
| **Consultant** | Synthesize final report | [MedGemma 4B-IT](https://huggingface.co/google/medgemma-1.5-4b-it) or [27B Text-IT](https://huggingface.co/google/medgemma-27b-text-it) | Writes as a **collegial consultant**: *"Have you considered..."* not *"You are wrong."* Only this agent optionally upgrades to 27B for deeper reasoning. |

## Architecture

The pipeline is orchestrated by [LangGraph](https://langchain-ai.github.io/langgraph/) as a linear `StateGraph`:

**Gradio UI** (image upload, diagnosis input, clinical context, [MedASR](https://huggingface.co/google/medasr) voice input)
→ **Diagnostician** — receives image + clinical context but **NOT** the doctor's diagnosis; tags findings by source (`imaging` / `clinical` / `both`)
→ **Bias Detector** — now receives the doctor's diagnosis, compares it against independent findings using image, clinical data, and [MedSigLIP](https://huggingface.co/google/medsiglip-448) sign verification
→ **Devil's Advocate** — challenges the working diagnosis using both imaging and clinical evidence for must-not-miss alternatives
→ **Consultant** — synthesizes a collegial consultation note
→ **Output** (consultation report, alternative diagnoses, recommended workup)

### MedSigLIP Sign Verification

The Bias Detector doesn't just rely on text reasoning — it uses [**MedSigLIP-448**](https://huggingface.co/google/medsiglip-448) for objective visual verification. For each radiological sign mentioned by the Diagnostician (e.g., "pleural effusion", "cardiomegaly", "pneumothorax"), MedSigLIP performs [zero-shot binary classification](https://huggingface.co/tasks/zero-shot-image-classification): it compares the logits of `"chest radiograph showing [sign]"` vs `"normal chest radiograph with no [sign]"`. A logit difference > 2 is classified as "likely present", grounding the bias analysis in **visual evidence** rather than pure language reasoning.

## Demo Cases

Three composite clinical scenarios covering the most dangerous diagnostic error patterns:

<table>
<tr>
<td width="33%" valign="top">

### Case 1: Missed Pneumothorax
**🏷️ TRAUMA**

32M, motorcycle collision. Doctor diagnoses **rib contusion**, discharges patient. Supine CXR actually shows a **left pneumothorax** with rib fractures.

**Bias**: [Satisfaction of search](https://radiopaedia.org/articles/satisfaction-of-search) — found the rib fractures, stopped looking.

</td>
<td width="33%" valign="top">

### Case 2: Aortic Dissection → "GERD"
**🏷️ VASCULAR**

58M, hypertensive, tearing chest pain. Doctor diagnoses **acid reflux**, prescribes antacids. Blood pressure asymmetry (178/102 R vs 146/88 L) and D-dimer 4,850 suggest **Stanford type B dissection**.

**Bias**: [Anchoring](https://en.wikipedia.org/wiki/Anchoring_(cognitive_bias)) + [availability heuristic](https://en.wikipedia.org/wiki/Availability_heuristic) — common diagnosis assumed first.

</td>
<td width="33%" valign="top">

### Case 3: Postpartum PE → "Anxiety"
**🏷️ POSTPARTUM**

29F, day 5 post C-section, dyspnea and tachycardia. Doctor orders **psychiatric consult**. SpO2 91%, ABG shows respiratory alkalosis — classic **pulmonary embolism**.

**Bias**: [Premature closure](https://en.wikipedia.org/wiki/Premature_closure) + [framing effect](https://en.wikipedia.org/wiki/Framing_effect_(psychology)) — young woman = anxiety.

</td>
</tr>
</table>

> All cases are educational composites synthesized from published literature. See [`data/demo_cases/SOURCES.md`](data/demo_cases/SOURCES.md) for full citations.

## Technical Details

### Model Stack

| Model | Parameters | Role | Loading |
|:------|:----------|:-----|:--------|
| [MedGemma 1.5 4B-IT](https://huggingface.co/google/medgemma-1.5-4b-it) | 4B | Multimodal image+text analysis | 4-bit quantized (~4GB VRAM) or BF16 (~8GB) |
| [MedGemma 27B Text-IT](https://huggingface.co/google/medgemma-27b-text-it) | 27B | Consultant deep reasoning (optional) | BF16 (~54GB VRAM) |
| [MedSigLIP-448](https://huggingface.co/google/medsiglip-448) | 0.9B | Zero-shot sign verification | FP32 (~3GB VRAM) |
| [MedASR](https://huggingface.co/google/medasr) | 105M | Medical speech-to-text | FP32 (~0.5GB VRAM) |

### Hardware

The full pipeline (4B 4-bit + MedSigLIP + MedASR) requires **~8 GB VRAM** and runs on any CUDA GPU with 12GB+ memory. All models load locally via [Transformers](https://huggingface.co/docs/transformers) with [4-bit quantization](https://huggingface.co/docs/bitsandbytes) — **zero API costs, fully offline-capable**.

### Key Technical Decisions

- **Blinded Diagnostician**: The first agent never sees the doctor's diagnosis. This prevents the AI from anchoring on the same conclusion, enabling genuine independent analysis.

- **Dual-source analysis (imaging + clinical)**: All agents analyze both the medical image and the full clinical context (vitals, labs, risk factors). Each Diagnostician finding is tagged with its source (`imaging`, `clinical`, or `both`). This is critical because many must-not-miss diagnoses — aortic dissection (BP asymmetry), pulmonary embolism (low SpO2, elevated D-dimer) — may have subtle or absent imaging signs but glaring clinical red flags.

- **Structured JSON output**: All agents output structured JSON parsed by [`json_repair`](https://github.com/mangiucugna/json_repair), which handles LLM output quirks (missing commas, truncation, markdown wrapping).

- **Thinking token stripping**: MedGemma wraps internal reasoning in `<unused94>...<unused95>` tags ([model card](https://huggingface.co/google/medgemma-27b-text-it#thinking-mode)). These are stripped via regex before display.

- **Adaptive model routing**: The first three agents (Diagnostician, Bias Detector, Devil's Advocate) always use 4B-IT for multimodal image+text analysis. Only the Consultant (text-only synthesis) optionally upgrades to 27B when `USE_27B=true` for deeper clinical reasoning. `generate_with_image()` always uses 4B (only model with vision).

- **Collegial tone**: The Consultant is prompted to write as a consulting colleague, not a critic. Research shows physicians respond better to [collaborative challenge than confrontation](https://pubmed.ncbi.nlm.nih.gov/28493811/).

- **Prompt Repetition**: All agents use the prompt repetition technique from [*"Prompt Repetition Improves Non-Reasoning LLMs"*](https://arxiv.org/abs/2512.14982) (Google Research, 2025). The user prompt is repeated with a transition phrase (`<query> Let me repeat the request: <query>`), which won **47 out of 70** benchmark-model combinations with **zero losses** — at nearly zero cost (only increases prefill tokens, no extra generation). Controllable via `ENABLE_PROMPT_REPETITION` env var.

## Getting Started

### Prerequisites

- Python 3.11+
- CUDA-capable GPU (12GB+ VRAM)
- [Hugging Face account](https://huggingface.co) with access to gated models (MedGemma, MedSigLIP, MedASR)

### Installation

```bash
# Clone the repository
git clone https://github.com/sypsyp97/diagnostic-devils-advocate
cd diagnostic-devils-advocate

# Install dependencies
pip install -r requirements.txt

# Login to Hugging Face (required for gated models)
huggingface-cli login
```

### Running

```bash
# Standard launch (4B quantized, 12GB GPU)
python app.py

# With 27B reasoning model (A100 80GB required)
USE_27B=true QUANTIZE_4B=false python app.py

# Disable voice input
ENABLE_MEDASR=false python app.py
```

The app launches at `http://localhost:7860`.

### Environment Variables

| Variable | Default | Description |
|:---------|:--------|:------------|
| `USE_27B` | `false` | Enable 27B model for the Consultant agent |
| `QUANTIZE_4B` | `true` | 4-bit quantize the 4B model |
| `ENABLE_MEDASR` | `true` | Enable voice input via MedASR |
| `HF_TOKEN` | — | Hugging Face token (or use `huggingface-cli login`) |
| `ENABLE_PROMPT_REPETITION` | `true` | [Prompt repetition](https://arxiv.org/abs/2512.14982) for improved output quality |
| `MODEL_LOCAL_DIR` | — | Local directory for pre-downloaded models |
| `DEVICE` | `cuda` | Compute device |

## Project Structure

```
diagnostic-devils-advocate/
├── app.py                        # Gradio entry point
├── config.py                     # Model selection & environment config
├── requirements.txt
│
├── agents/
│   ├── state.py                  # LangGraph TypedDict state definitions
│   ├── prompts.py                # All agent prompt templates
│   ├── graph.py                  # LangGraph StateGraph pipeline
│   ├── output_parser.py          # JSON parsing with json_repair + llm-output-parser
│   ├── diagnostician.py          # Agent 1: Blinded image + clinical analysis
│   ├── bias_detector.py          # Agent 2: Bias detection + MedSigLIP
│   ├── devil_advocate.py         # Agent 3: Adversarial challenge
│   └── consultant.py              # Agent 4: Consultation note synthesis
│
├── models/
│   ├── medgemma_client.py        # MedGemma 4B/27B inference client
│   ├── medsiglip_client.py       # MedSigLIP zero-shot classification
│   ├── medasr_client.py          # MedASR speech-to-text
│   └── utils.py                  # Image preprocessing, token stripping
│
├── ui/
│   ├── components.py             # Gradio layout & progress visualization
│   ├── callbacks.py              # UI event handlers & pipeline integration
│   └── css.py                    # Custom styling (responsive design)
│
└── data/
    └── demo_cases/               # 3 composite clinical scenarios
        └── SOURCES.md            # Full literature citations
```

## Disclaimer

> **This is a research prototype built for the MedGemma Impact Challenge. It is NOT intended for clinical decision-making.** All demo cases are educational composites. Medical images are sourced from the University of Saskatchewan Teaching Collection (CC-BY-NC-SA 4.0).

## References

- Singh H, et al. "The frequency of diagnostic errors in outpatient care." [*BMJ Quality & Safety*, 2014](https://qualitysafety.bmj.com/content/23/9/727)
- Graber ML, et al. "Cognitive interventions to reduce diagnostic error." [*BMJ Quality & Safety*, 2012](https://qualitysafety.bmj.com/content/21/7/535)
- Croskerry P. "The importance of cognitive errors in diagnosis." [*Academic Medicine*, 2003](https://pubmed.ncbi.nlm.nih.gov/12915371/)
- Ball CG, et al. "Incidence, risk factors, and outcomes for occult pneumothoraces." [*J Trauma*, 2005](https://pubmed.ncbi.nlm.nih.gov/16374282/)
- Hansen MS, et al. "Frequency of misdiagnosis of acute aortic dissection." [*Am J Cardiol*, 2007](https://pubmed.ncbi.nlm.nih.gov/17350380/)
- Ivgi M, et al. "Prompt Repetition Improves Non-Reasoning LLMs." [*arXiv:2512.14982*](https://arxiv.org/abs/2512.14982), Google Research, 2025
- Google Health AI. [Health AI Developer Foundations (HAI-DEF)](https://developers.google.com/health-ai)
- Yang J, et al. [MedGemma: Medical AI model](https://huggingface.co/collections/google/health-ai-developer-foundations-68544906f8a0a10f7d30ade8) — Hugging Face Collection

---

<div align="center">

Built with [Google Health AI Developer Foundations](https://developers.google.com/health-ai) for the [MedGemma Impact Challenge](https://www.kaggle.com/competitions/medgemma-impact-challenge)

</div>
