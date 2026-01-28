"""
MedASR client: medical speech-to-text transcription.
Uses CTC decoding with proper blank-token collapse.
"""

from __future__ import annotations

import logging
import os
import threading
import warnings

from config import MEDASR_MODEL_ID, HF_TOKEN, DEVICE, ENABLE_MEDASR

logger = logging.getLogger(__name__)

_model = None
_processor = None
_load_lock = threading.Lock()


def _token_arg() -> dict:
    if os.path.isdir(MEDASR_MODEL_ID):
        return {}
    # Only pass `token` when explicitly provided; omitting it lets HF Hub fall back
    # to `huggingface-cli login` cached credentials (useful on local/dev machines).
    if HF_TOKEN:
        return {"token": HF_TOKEN}
    return {}


def load():
    """Load MedASR model and processor."""
    global _model, _processor
    if _model is not None:
        return _model, _processor
    if not ENABLE_MEDASR:
        raise RuntimeError("MedASR is disabled via ENABLE_MEDASR=false")

    with _load_lock:
        if _model is not None:
            return _model, _processor

        import torch
        from transformers import AutoModelForCTC, AutoProcessor

        logger.info("Loading MedASR from %s...", "local" if os.path.isdir(MEDASR_MODEL_ID) else "HF Hub")
        _processor = AutoProcessor.from_pretrained(MEDASR_MODEL_ID, **_token_arg())
        _model = AutoModelForCTC.from_pretrained(
            MEDASR_MODEL_ID, **_token_arg(), dtype=torch.float32,
        ).to(DEVICE)
        _model.eval()
        logger.info("MedASR loaded.")
        return _model, _processor


def _ctc_greedy_decode(logits, processor) -> str:
    """
    Proper CTC greedy decode:
    1. argmax to get predicted token IDs
    2. Collapse consecutive duplicate IDs
    3. Remove blank token IDs
    4. Decode remaining IDs to text
    """
    import torch

    predicted_ids = torch.argmax(logits, dim=-1)[0]  # (seq_len,)

    # Determine blank token ID
    blank_id = getattr(processor.tokenizer, "pad_token_id", None)
    if blank_id is None:
        blank_id = 0  # CTC blank is typically ID 0

    # Collapse consecutive duplicates, then remove blanks
    collapsed = []
    prev_id = -1
    for token_id in predicted_ids.tolist():
        if token_id != prev_id:
            if token_id != blank_id:
                collapsed.append(token_id)
            prev_id = token_id

    if not collapsed:
        return ""

    # Decode token IDs to text
    text = processor.tokenizer.decode(collapsed, skip_special_tokens=True)
    return text.strip()


def transcribe(audio_array, sampling_rate: int = 16000) -> str:
    """
    Transcribe audio to text using CTC greedy decoding.

    Args:
        audio_array: numpy array of audio samples (mono, float32).
        sampling_rate: audio sample rate (MedASR expects 16kHz).

    Returns:
        Transcribed text string.
    """
    model, processor = load()
    import torch

    inputs = processor(
        audio_array, sampling_rate=sampling_rate, return_tensors="pt",
    ).to(model.device)

    with torch.inference_mode():
        # Suppress the harmless padding='same' convolution warning
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*padding='same'.*")
            logits = model(**inputs).logits

    return _ctc_greedy_decode(logits, processor)
