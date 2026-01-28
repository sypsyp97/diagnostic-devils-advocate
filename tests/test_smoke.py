"""Quick smoke tests: imports, graph build, demo loading, utils."""

import os
import sys

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_smoke_graph_builds():
    from agents.graph import build_graph

    graph = build_graph()
    assert graph is not None


def test_smoke_demo_loader_returns_expected_shape():
    from ui.callbacks import load_demo

    img, diagnosis, context, modality = load_demo("Case 1: Missed Pneumothorax")
    assert isinstance(diagnosis, str) and diagnosis
    assert isinstance(context, str) and context
    assert modality in {"CXR", "CT", "Other"}
    assert img is None or hasattr(img, "size")


def test_utils_strip_and_resize():
    from models.utils import resize_for_medgemma, strip_thinking_tokens

    assert strip_thinking_tokens("<unused94>t<unused95>Real answer") == "Real answer"
    big = Image.new("RGB", (2000, 2000), color="gray")
    resized = resize_for_medgemma(big)
    assert max(resized.size) <= 896

