"""
MedGemma client: unified interface for 4B (multimodal) and 27B (text-only) models.
Loads locally via transformers with optional 4-bit quantization.
"""

from __future__ import annotations

import logging
import os
import threading
from PIL import Image

from config import (
    USE_27B, QUANTIZE_4B, HF_TOKEN, DEVICE,
    MEDGEMMA_4B_MODEL_ID, MEDGEMMA_27B_MODEL_ID,
    MAX_NEW_TOKENS_4B, MAX_NEW_TOKENS_27B, TEMPERATURE, REPETITION_PENALTY,
)
from models.utils import strip_thinking_tokens, resize_for_medgemma, apply_prompt_repetition

logger = logging.getLogger(__name__)

_model_4b = None
_processor_4b = None
_model_27b = None
_tokenizer_27b = None
_load_4b_lock = threading.Lock()
_load_27b_lock = threading.Lock()


def _is_local_path(model_id: str) -> bool:
    """Check if model_id is a local directory path."""
    return os.path.isdir(model_id)


def _token_arg(model_id: str) -> dict:
    """Return token kwarg only when loading from HF Hub (not local path)."""
    if _is_local_path(model_id):
        return {}
    return {"token": HF_TOKEN}


def _get_quantization_config():
    """Return BitsAndBytesConfig for 4-bit quantization."""
    import torch
    from transformers import BitsAndBytesConfig
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
    )


def load_4b():
    """Load MedGemma 4B-IT (multimodal) model and processor."""
    global _model_4b, _processor_4b
    if _model_4b is not None:
        return _model_4b, _processor_4b

    with _load_4b_lock:
        if _model_4b is not None:
            return _model_4b, _processor_4b

        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        is_local = _is_local_path(MEDGEMMA_4B_MODEL_ID)
        logger.info(
            "Loading MedGemma 4B-IT (%s) from %s...",
            "4-bit" if QUANTIZE_4B else "bf16",
            "local" if is_local else "HF Hub",
        )

        # BitsAndBytes quantization requires device_map="auto", not "cuda"
        device_map = "auto" if QUANTIZE_4B else DEVICE
        kwargs = {**_token_arg(MEDGEMMA_4B_MODEL_ID), "device_map": device_map}
        if QUANTIZE_4B:
            kwargs["quantization_config"] = _get_quantization_config()
        else:
            kwargs["dtype"] = torch.bfloat16

        _processor_4b = AutoProcessor.from_pretrained(MEDGEMMA_4B_MODEL_ID, **_token_arg(MEDGEMMA_4B_MODEL_ID))
        _model_4b = AutoModelForImageTextToText.from_pretrained(MEDGEMMA_4B_MODEL_ID, **kwargs)
        _model_4b.eval()
        logger.info("MedGemma 4B loaded.")
        return _model_4b, _processor_4b


def load_27b():
    """Load MedGemma 27B Text-IT model and tokenizer (A100 only)."""
    global _model_27b, _tokenizer_27b
    if _model_27b is not None:
        return _model_27b, _tokenizer_27b

    with _load_27b_lock:
        if _model_27b is not None:
            return _model_27b, _tokenizer_27b

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        is_local = _is_local_path(MEDGEMMA_27B_MODEL_ID)
        logger.info(
            "Loading MedGemma 27B Text-IT (bf16) from %s...",
            "local" if is_local else "HF Hub",
        )

        _tokenizer_27b = AutoTokenizer.from_pretrained(MEDGEMMA_27B_MODEL_ID, **_token_arg(MEDGEMMA_27B_MODEL_ID))
        _model_27b = AutoModelForCausalLM.from_pretrained(
            MEDGEMMA_27B_MODEL_ID,
            **_token_arg(MEDGEMMA_27B_MODEL_ID),
            dtype=torch.bfloat16,
            device_map="auto",
        )
        _model_27b.eval()
        logger.info("MedGemma 27B loaded.")
        return _model_27b, _tokenizer_27b


def generate_with_image(prompt: str, image: Image.Image, system_prompt: str = "") -> str:
    """Generate text from image + text prompt using MedGemma 4B."""
    model, processor = load_4b()
    image = resize_for_medgemma(image)
    prompt = apply_prompt_repetition(prompt)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})
    messages.append({
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt},
        ],
    })

    inputs = processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt",
    ).to(model.device)

    import torch

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS_4B,
            do_sample=TEMPERATURE > 0,
            repetition_penalty=REPETITION_PENALTY,
            **({"temperature": TEMPERATURE} if TEMPERATURE > 0 else {}),
        )

    # Decode only the new tokens
    new_tokens = output_ids[0, inputs["input_ids"].shape[1]:]
    text = processor.tokenizer.decode(new_tokens, skip_special_tokens=True)
    return strip_thinking_tokens(text)


def generate_text(prompt: str, system_prompt: str = "") -> str:
    """Generate text from text-only prompt. Uses 27B if available, else 4B."""
    if USE_27B:
        return _generate_text_27b(prompt, system_prompt)
    return _generate_text_4b(prompt, system_prompt)


def _generate_text_4b(prompt: str, system_prompt: str = "") -> str:
    """Text-only generation with 4B model."""
    model, processor = load_4b()
    prompt = apply_prompt_repetition(prompt)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})
    messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})

    inputs = processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt",
    ).to(model.device)

    import torch

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS_4B,
            do_sample=TEMPERATURE > 0,
            repetition_penalty=REPETITION_PENALTY,
            **({"temperature": TEMPERATURE} if TEMPERATURE > 0 else {}),
        )

    new_tokens = output_ids[0, inputs["input_ids"].shape[1]:]
    text = processor.tokenizer.decode(new_tokens, skip_special_tokens=True)
    return strip_thinking_tokens(text)


def _generate_text_27b(prompt: str, system_prompt: str = "") -> str:
    """Text-only generation with 27B model (thinking mode)."""
    model, tokenizer = load_27b()
    prompt = apply_prompt_repetition(prompt)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    input_text = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    import torch

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS_27B,
            do_sample=TEMPERATURE > 0,
            repetition_penalty=REPETITION_PENALTY,
            **({"temperature": TEMPERATURE} if TEMPERATURE > 0 else {}),
        )

    new_tokens = output_ids[0, inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return strip_thinking_tokens(text)
