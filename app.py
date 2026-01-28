"""
Diagnostic Devil's Advocate — Main entry point.
A multi-agent AI system that challenges clinical diagnoses to prevent cognitive bias errors.
"""

import logging
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

import gradio as gr  # noqa: E402

from config import ENABLE_MEDASR  # noqa: E402
from ui.components import build_ui  # noqa: E402
from ui.callbacks import analyze_streaming, load_demo, transcribe_audio  # noqa: E402
from ui.css import CUSTOM_CSS  # noqa: E402


def main():
    demo = build_ui(
        analyze_fn=analyze_streaming,
        load_demo_fn=load_demo,
        transcribe_fn=transcribe_audio if ENABLE_MEDASR else None,
    )
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(),
        ssr_mode=False,  # Disable SSR for consistent CSS loading
    )


if __name__ == "__main__":
    main()
