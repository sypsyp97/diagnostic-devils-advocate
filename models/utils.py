"""
Utility functions for model outputs: thinking token stripping, image encoding,
prompt repetition, etc.
"""

import re
import base64
from io import BytesIO
from PIL import Image

from config import ENABLE_PROMPT_REPETITION

# MedGemma wraps internal reasoning in <unused94>...<unused95> tags
THINKING_PATTERN = re.compile(r"<unused94>.*?<unused95>", re.DOTALL)


def strip_thinking_tokens(text: str) -> str:
    """Remove MedGemma's internal thinking tokens from output."""
    return THINKING_PATTERN.sub("", text).strip()


def image_to_base64(image: Image.Image, fmt: str = "PNG") -> str:
    """Convert PIL Image to base64 data URL string."""
    buffer = BytesIO()
    image.save(buffer, format=fmt)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/{fmt.lower()};base64,{encoded}"


def apply_prompt_repetition(prompt: str) -> str:
    """Repeat the user prompt to improve LLM output quality.

    Based on "Prompt Repetition Improves Non-Reasoning LLMs"
    (arXiv:2512.14982, Google Research 2025): repeating the input prompt
    wins 47/70 benchmark-model combos with 0 losses. Uses the verbose
    variant with a transition phrase for clarity.
    """
    if not ENABLE_PROMPT_REPETITION:
        return prompt
    return f"{prompt}\n\nLet me repeat the request:\n\n{prompt}"


def resize_for_medgemma(image: Image.Image, max_size: int = 896) -> Image.Image:
    """Resize image to fit MedGemma's expected input resolution (896x896)."""
    if max(image.size) <= max_size:
        return image
    ratio = max_size / max(image.size)
    new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    return image.resize(new_size, Image.LANCZOS)
