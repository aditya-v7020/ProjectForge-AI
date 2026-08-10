"""ProjectForge AI — LangGraph Workflow Definition.

Two-phase workflow:
  Phase 1: Requirements → Technology Analysis → STOP (wait for user selection)
  Phase 2: Architecture → Tasks → Timeline → Critic → [Revision Loop] → Blueprint
"""
import logging
from langgraph.graph import StateGraph, END

from backend.app.graph.state import ProjectState
from backend.app.graph.nodes import (
    node_requirement_analyst,
    node_technology_advisor,
    node_architecture,
    node_task_planner,
    node_timeline,
    node_critic,
    node_generate_blueprint,
    should_revise,
)

logger = logging.getLogger(__name__)


def build_phase1_graph() -> StateGraph:
    """Build the Phase 1 workflow: Requirements → Technology Analysis.

    This graph runs after the user submits a project idea.
    It stops after technology analysis, waiting for user selection.

    Returns:
        Compiled LangGraph StateGraph.
    """
    graph = StateGraph(ProjectState)

    # Add nodes
    graph.add_node("requirement_analyst", node_requirement_analyst)
    graph.add_node("technology_advisor", node_technology_advisor)

    # Define edges
    graph.set_entry_point("requirement_analyst")
    graph.add_edge("requirement_analyst", "technology_advisor")
    graph.add_edge("technology_advisor", END)

    return graph.compile()


def build_phase2_graph() -> StateGraph:
    """Build the Phase 2 workflow: Architecture → Tasks → Timeline → Critic → Blueprint.

    This graph runs after the user selects and locks technologies.
    It includes the critic revision loop (max 3 cycles).

    Returns:
        Compiled LangGraph StateGraph.
    """
    graph = StateGraph(ProjectState)

    # Add nodes
    graph.add_node("architecture", node_architecture)
    graph.add_node("task_planner", node_task_planner)
    graph.add_node("timeline", node_timeline)
    graph.add_node("critic", node_critic)
    graph.add_node("blueprint", node_generate_blueprint)

    # Define edges
    graph.set_entry_point("architecture")
    graph.add_edge("architecture", "task_planner")
    graph.add_edge("task_planner", "timeline")
    graph.add_edge("timeline", "critic")

    # Conditional edge: critic → revise or finalize
    graph.add_conditional_edges(
        "critic",
        should_revise,
        {
            "revise": "task_planner",   # Loop back to task planner for revision
            "finalize": "blueprint",     # Proceed to blueprint generation
        },
    )

    graph.add_edge("blueprint", END)

    return graph.compile()


def run_phase1(project_id: int, raw_idea: str) -> ProjectState:
    """Execute Phase 1: Requirements → Technology Analysis.

    Args:
        project_id: Database project ID.
        raw_idea: Raw user project idea text.

    Returns:
        Final state after Phase 1 (contains requirements + tech options).
    """
    logger.info(f"Phase 1: Starting for project {project_id}")

    initial_state: ProjectState = {
        "project_id": project_id,
        "raw_idea": raw_idea,
        "requirements": None,
        "technology_options": None,
        "selected_technologies": None,
        "architecture": None,
        "task_plan": None,
        "timeline": None,
        "critique": None,
        "status": "started",
        "revision_count": 0,
        "max_revisions": 3,
        "current_agent": "",
        "blueprint": None,
        "error": None,
        "warnings": [],
    }

    graph = build_phase1_graph()
    result = graph.invoke(initial_state)

    logger.info(f"Phase 1: Completed with status={result.get('status')}")
    return result


def run_phase2(state: ProjectState) -> ProjectState:
    """Execute Phase 2: Architecture → Tasks → Timeline → Critic → Blueprint.

    Args:
        state: State from Phase 1 + user's locked technology selections.

    Returns:
        Final state with complete blueprint.
    """
    logger.info(f"Phase 2: Starting for project {state.get('project_id')}")

    # Ensure revision tracking is initialized
    state.setdefault("revision_count", 0)
    state.setdefault("max_revisions", 3)
    state.setdefault("warnings", [])

    graph = build_phase2_graph()
    result = graph.invoke(state)

    logger.info(f"Phase 2: Completed with status={result.get('status')}")
    return result
