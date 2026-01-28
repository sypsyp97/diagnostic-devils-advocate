"""
MedSigLIP client: zero-shot medical image classification and embedding extraction.
Uses AutoProcessor following the official Google-Health/medsiglip notebook.
"""

from __future__ import annotations

import logging
import os
import threading

from PIL import Image

from config import MEDSIGLIP_MODEL_ID, HF_TOKEN, DEVICE

logger = logging.getLogger(__name__)

_model = None
_processor = None
_load_lock = threading.Lock()


def _token_arg() -> dict:
    if os.path.isdir(MEDSIGLIP_MODEL_ID):
        return {}
    return {"token": HF_TOKEN}


def load():
    """Load MedSigLIP model and processor."""
    global _model, _processor
    if _model is not None:
        return _model, _processor

    with _load_lock:
        if _model is not None:
            return _model, _processor

        import torch
        from transformers import AutoModel, AutoImageProcessor, AutoTokenizer, SiglipProcessor

        logger.info("Loading MedSigLIP from %s...", "local" if os.path.isdir(MEDSIGLIP_MODEL_ID) else "HF Hub")

        # MedSigLIP may lack processor_config.json, so load components separately
        try:
            from transformers import AutoProcessor
            _processor = AutoProcessor.from_pretrained(MEDSIGLIP_MODEL_ID, **_token_arg())
        except Exception as e:
            logger.warning("AutoProcessor failed (%s), loading components separately", e)
            image_processor = AutoImageProcessor.from_pretrained(MEDSIGLIP_MODEL_ID, **_token_arg())
            tokenizer = AutoTokenizer.from_pretrained(MEDSIGLIP_MODEL_ID, **_token_arg())
            _processor = SiglipProcessor(image_processor=image_processor, tokenizer=tokenizer)

        _model = AutoModel.from_pretrained(
            MEDSIGLIP_MODEL_ID, **_token_arg(), torch_dtype=torch.float32,
        ).to(DEVICE)
        _model.eval()
        logger.info("MedSigLIP loaded.")
        return _model, _processor


def classify(image: Image.Image, candidate_labels: list) -> list[dict]:
    """
    Zero-shot classification of a medical image.

    Args:
        candidate_labels: list of str OR list of (short_label, descriptive_prompt) tuples.

    Returns list of {"label": str, "score": float} sorted by descending score.
    Scores are raw logits (not sigmoid/softmax) — higher = better match.
    """
    if candidate_labels and isinstance(candidate_labels[0], (list, tuple)):
        display_labels = [c[0] for c in candidate_labels]
        text_prompts = [c[1] for c in candidate_labels]
    else:
        display_labels = candidate_labels
        text_prompts = candidate_labels

    model, processor = load()
    # Official usage: single processor call with padding="max_length"
    inputs = processor(
        text=text_prompts, images=image,
        padding="max_length", return_tensors="pt",
    ).to(model.device)

    import torch

    with torch.inference_mode():
        outputs = model(**inputs)

    # Use raw logits — official notebook uses argmax on logits_per_image directly
    logits = outputs.logits_per_image[0].cpu().tolist()

    results = [{"label": label, "score": score} for label, score in zip(display_labels, logits)]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def _normalize_modality(modality: str | None) -> str:
    m = (modality or "").strip().lower()
    if m in {"cxr", "x-ray", "xray", "chest x-ray", "chest xray", "chest radiograph", "radiograph"}:
        return "cxr"
    if m in {"ct", "ct scan", "computed tomography"}:
        return "ct"
    return "other"


def _verification_prompts(sign: str, modality: str | None) -> tuple[str, str]:
    sign_l = sign.lower()
    m = _normalize_modality(modality)
    if m == "ct":
        positive = f"a CT scan showing {sign_l}"
        negative = f"a CT scan showing no evidence of {sign_l}"
    elif m == "other":
        positive = f"a medical image showing {sign_l}"
        negative = f"a medical image showing no evidence of {sign_l}"
    else:
        positive = f"a chest radiograph showing {sign_l}"
        negative = f"a normal chest radiograph with no {sign_l}"
    return positive, negative


def verify_sign(image: Image.Image, sign: str, modality: str | None = None) -> dict:
    """
    Binary verification: does the image show this finding/sign?
    Compares "showing X" vs "no X" — matches official MedSigLIP usage pattern.

    Returns confidence level based on logit difference:
        diff > 2  → "likely present"
        diff > 0  → "possibly present"
        diff > -2 → "inconclusive"
        else      → "likely absent"
    """
    positive, negative = _verification_prompts(sign, modality)

    results = classify(image, [
        ("positive", positive),
        ("negative", negative),
    ])

    pos = next(r for r in results if r["label"] == "positive")
    neg = next(r for r in results if r["label"] == "negative")
    diff = pos["score"] - neg["score"]

    if diff > 2:
        confidence = "likely present"
    elif diff > 0:
        confidence = "possibly present"
    elif diff > -2:
        confidence = "inconclusive"
    else:
        confidence = "likely absent"

    return {
        "sign": sign,
        "modality": _normalize_modality(modality),
        "positive_logit": pos["score"],
        "negative_logit": neg["score"],
        "diff": diff,
        "confidence": confidence,
    }


def verify_findings(
    image: Image.Image,
    signs: list[str],
    modality: str | None = None,
) -> list[dict]:
    """
    Verify a list of imaging signs against the image.
    Returns only results where SigLIP has a meaningful opinion (not inconclusive).
    """
    results = [verify_sign(image, sign, modality=modality) for sign in signs]
    return results
