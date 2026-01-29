"""
Configuration for Diagnostic Devil's Advocate.
Controls model loading, quantization, and environment-specific settings.

Model loading priority:
  1. Local path (MODEL_LOCAL_DIR env var) — fully offline
  2. HF cache (auto-downloaded via huggingface-cli download) — offline after first download
  3. HF Hub (requires HF_TOKEN for gated models) — online fallback
"""

import os
from huggingface_hub import try_to_load_from_cache

# --- Model Selection ---
USE_27B = os.environ.get("USE_27B", "false").lower() == "true"
QUANTIZE_4B = os.environ.get("QUANTIZE_4B", "true").lower() == "true"
ENABLE_MEDASR = os.environ.get("ENABLE_MEDASR", "true").lower() == "true"

# --- Performance Optimization ---
# torch.compile: JIT 编译加速，首次推理慢（编译），后续快 30-80%
# 默认关闭：ZeroGPU 冷启动每次都要重新编译，不划算
ENABLE_TORCH_COMPILE = os.environ.get("ENABLE_TORCH_COMPILE", "false").lower() == "true"
# SDPA: 优化注意力计算，省显存 + 加速（无编译开销）
ENABLE_SDPA = os.environ.get("ENABLE_SDPA", "true").lower() == "true"

# --- Prompt Repetition (arXiv:2512.14982) ---
# Repeating the user prompt improves non-reasoning LLM performance (47 wins, 0 losses
# across 70 benchmark-model combos). Only increases prefill tokens, no extra generation.
ENABLE_PROMPT_REPETITION = os.environ.get("ENABLE_PROMPT_REPETITION", "true").lower() == "true"

# --- HF Token (for gated models) ---
# Loaded from: env var > huggingface-cli login stored token (auto)
HF_TOKEN = os.environ.get("HF_TOKEN", None)

# --- Model IDs (HF Hub) ---
_MEDGEMMA_4B_HUB_ID = "google/medgemma-1.5-4b-it"
_MEDGEMMA_27B_HUB_ID = "google/medgemma-27b-text-it"
_MEDSIGLIP_HUB_ID = "google/medsiglip-448"
_MEDASR_HUB_ID = "google/medasr"

# --- Optional local model directories (override HF Hub) ---
# Set these env vars to point to a local directory containing model weights.
# If not set, models load from HF cache (downloaded via `huggingface-cli download`).
MODEL_LOCAL_DIR = os.environ.get("MODEL_LOCAL_DIR", None)

def _resolve_model_path(hub_id: str, local_subdir: str | None = None) -> str:
    """Resolve model path: local dir > HF cache > HF Hub ID."""
    # 1. Explicit local directory
    if MODEL_LOCAL_DIR:
        local_path = os.path.join(MODEL_LOCAL_DIR, local_subdir or hub_id.split("/")[-1])
        if os.path.isdir(local_path):
            return local_path
    # 2. HF cache (already downloaded via huggingface-cli download)
    try:
        cached = try_to_load_from_cache(hub_id, "config.json")
    except Exception:
        cached = None
    if cached is not None and isinstance(cached, str):
        # Return the repo snapshot directory (parent of config.json)
        return os.path.dirname(cached)
    # 3. Fallback to Hub ID (will download on first use)
    return hub_id

MEDGEMMA_4B_MODEL_ID = _resolve_model_path(_MEDGEMMA_4B_HUB_ID, "medgemma-4b")
MEDGEMMA_27B_MODEL_ID = _resolve_model_path(_MEDGEMMA_27B_HUB_ID, "medgemma-27b")
MEDSIGLIP_MODEL_ID = _resolve_model_path(_MEDSIGLIP_HUB_ID, "medsiglip-448")
MEDASR_MODEL_ID = _resolve_model_path(_MEDASR_HUB_ID, "medasr")

# --- Generation Parameters ---
MAX_NEW_TOKENS_4B = 4096
MAX_NEW_TOKENS_27B = 6000
TEMPERATURE = 0.0
REPETITION_PENALTY = 1.2  # Prevent greedy decoding repetition loops

# --- Device ---
DEVICE = os.environ.get("DEVICE", "cuda")

# --- Demo Cases Directory ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DEMO_CASES_DIR = os.path.join(DATA_DIR, "demo_cases")
