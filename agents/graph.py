"""
LangGraph pipeline: linear flow through 4 diagnostic agents.

START → diagnostician → bias_detector → devil_advocate → consultant → END
"""

import logging
import threading

from agents.state import PipelineState
from agents import diagnostician, bias_detector, devil_advocate, consultant

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, START, END

    _LANGGRAPH_AVAILABLE = True
except ModuleNotFoundError:
    StateGraph = None  # type: ignore[assignment]
    START = END = None
    _LANGGRAPH_AVAILABLE = False


def _check_error(state: PipelineState) -> str:
    """Route to END if an error occurred, otherwise continue."""
    if state.get("error"):
        return "end"
    return "continue"


class _FallbackGraph:
    def invoke(self, initial_state: PipelineState) -> PipelineState:
        state = initial_state
        for fn in (diagnostician.run, bias_detector.run, devil_advocate.run, consultant.run):
            state = fn(state)
            if state.get("error"):
                break
        return state

    def stream(self, initial_state: PipelineState, stream_mode: str = "updates"):
        state = initial_state
        for name, fn in (
            ("diagnostician", diagnostician.run),
            ("bias_detector", bias_detector.run),
            ("devil_advocate", devil_advocate.run),
            ("consultant", consultant.run),
        ):
            state = fn(state)
            yield {name: dict(state)}
            if state.get("error"):
                break


def build_graph():
    """Build and compile the diagnostic debiasing pipeline."""
    if not _LANGGRAPH_AVAILABLE:
        logger.warning("langgraph is not installed; falling back to a simple sequential pipeline.")
        return _FallbackGraph()

    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("diagnostician", diagnostician.run)
    graph.add_node("bias_detector", bias_detector.run)
    graph.add_node("devil_advocate", devil_advocate.run)
    graph.add_node("consultant", consultant.run)

    # Linear flow with error checking
    graph.add_edge(START, "diagnostician")
    graph.add_conditional_edges("diagnostician", _check_error, {"continue": "bias_detector", "end": END})
    graph.add_conditional_edges("bias_detector", _check_error, {"continue": "devil_advocate", "end": END})
    graph.add_conditional_edges("devil_advocate", _check_error, {"continue": "consultant", "end": END})
    graph.add_edge("consultant", END)

    return graph.compile()


# Singleton compiled graph
_compiled_graph = None
_compiled_graph_lock = threading.Lock()


def get_graph():
    """Get or create the compiled pipeline graph."""
    global _compiled_graph
    if _compiled_graph is not None:
        return _compiled_graph
    with _compiled_graph_lock:
        if _compiled_graph is None:
            _compiled_graph = build_graph()
    return _compiled_graph


def _make_initial_state(
    image,
    doctor_diagnosis: str,
    clinical_context: str,
    modality: str | None = None,
) -> PipelineState:
    return {
        "clinical_input": {
            "image": image,
            "doctor_diagnosis": doctor_diagnosis,
            "clinical_context": clinical_context,
            "modality": modality or "CXR",
        },
        "diagnostician_output": None,
        "bias_detector_output": None,
        "devils_advocate_output": None,
        "consultant_output": None,
        "current_step": "start",
        "error": None,
    }


def run_pipeline(
    image,
    doctor_diagnosis: str,
    clinical_context: str,
    modality: str | None = None,
) -> PipelineState:
    """Run the full debiasing pipeline (blocking)."""
    graph = get_graph()
    initial_state = _make_initial_state(image, doctor_diagnosis, clinical_context, modality=modality)
    return graph.invoke(initial_state)


def stream_pipeline(
    image,
    doctor_diagnosis: str,
    clinical_context: str,
    modality: str | None = None,
):
    """
    Stream the pipeline, yielding (node_name, state) after each agent completes.
    Use this for progressive UI updates.
    """
    graph = get_graph()
    initial_state = _make_initial_state(image, doctor_diagnosis, clinical_context, modality=modality)

    for event in graph.stream(initial_state, stream_mode="updates"):
        # event is {node_name: state_update}
        for node_name, state_update in event.items():
            yield node_name, state_update
