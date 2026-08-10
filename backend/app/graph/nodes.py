"""ProjectForge AI — LangGraph Workflow Nodes.

Each node corresponds to one agent or workflow step. Nodes update state and emit
real-time progress notifications.
"""
import logging
from typing import Dict, Any

from backend.app.graph.state import ProjectState
from backend.app.schemas.agent import (
    ProjectRequirements, TechnologyRecommendations, ArchitectureDesign,
    TaskPlan, TimelinePlan, CritiqueResult, ensure_project_requirements,
)
from backend.app.agents.requirement_analyst import run_requirement_analyst
from backend.app.agents.technology_advisor import run_technology_advisor, get_fallback_technology_recommendations
from backend.app.agents.architecture_agent import run_architecture_agent, get_fallback_architecture_design
from backend.app.agents.task_planner import run_task_planner, get_fallback_task_plan
from backend.app.agents.timeline_agent import run_timeline_agent, get_fallback_timeline_plan
from backend.app.agents.critic_agent import run_critic_agent, get_fallback_critique_result
from backend.app.services.progress_manager import send_progress

logger = logging.getLogger(__name__)

_progress_callback = None


def set_progress_callback(callback):
    """Set optional progress callback function."""
    global _progress_callback
    _progress_callback = callback


def _notify(agent_name: str, status: str):
    """Helper to emit progress notifications for a node."""
    logger.info(f"Node notification: {agent_name} → {status}")
    if _progress_callback:
        try:
            _progress_callback(agent_name, status)
        except Exception as e:
            logger.warning(f"Failed to invoke progress callback: {e}")


def _parse_architecture(arch_raw, reqs, selected) -> ArchitectureDesign:
    if isinstance(arch_raw, ArchitectureDesign):
        return arch_raw
    if isinstance(arch_raw, dict) and arch_raw:
        try:
            return ArchitectureDesign.model_validate(arch_raw)
        except Exception:
            pass
    return get_fallback_architecture_design(reqs, selected)


def _parse_task_plan(tp_raw, reqs, selected, arch) -> TaskPlan:
    if isinstance(tp_raw, TaskPlan):
        return tp_raw
    if isinstance(tp_raw, dict) and tp_raw:
        try:
            return TaskPlan.model_validate(tp_raw)
        except Exception:
            pass
    return get_fallback_task_plan(reqs, selected, arch)


def _parse_timeline(tl_raw, reqs, tp, selected) -> TimelinePlan:
    if isinstance(tl_raw, TimelinePlan):
        return tl_raw
    if isinstance(tl_raw, dict) and tl_raw:
        try:
            return TimelinePlan.model_validate(tl_raw)
        except Exception:
            pass
    return get_fallback_timeline_plan(reqs, tp, selected)


def node_requirement_analyst(state: ProjectState) -> dict:
    """Node: Run Requirement Analyst Agent."""
    _notify("requirement_analyst", "running")
    try:
        raw_idea = state.get("raw_idea", "")
        if not raw_idea:
            raw_reqs = state.get("requirements")
            if raw_reqs:
                if isinstance(raw_reqs, dict):
                    raw_idea = raw_reqs.get("project_description", "") or raw_reqs.get("project_name", "")
                elif isinstance(raw_reqs, ProjectRequirements):
                    raw_idea = raw_reqs.project_description or raw_reqs.project_name

        result = run_requirement_analyst(raw_idea)
        _notify("requirement_analyst", "completed")
        return {
            "requirements": result.model_dump(),
            "status": "requirements_done",
            "current_agent": "requirement_analyst",
        }
    except Exception as e:
        logger.error(f"Requirement Analyst failed: {e}")
        _notify("requirement_analyst", "failed")
        return {
            "error": f"Requirement Analyst failed: {str(e)}",
            "status": "error",
        }


def node_technology_advisor(state: ProjectState) -> dict:
    """Node: Run Technology Advisor Agent."""
    _notify("technology_advisor", "running")
    try:
        requirements = ensure_project_requirements(state.get("requirements"))
        result = run_technology_advisor(requirements)
        _notify("technology_advisor", "completed")
        return {
            "technology_options": result.model_dump(),
            "status": "tech_analysis_done",
            "current_agent": "technology_advisor",
        }
    except Exception as e:
        logger.error(f"Technology Advisor failed: {e}")
        _notify("technology_advisor", "completed")
        fallback_result = get_fallback_technology_recommendations(
            ensure_project_requirements(state.get("requirements"))
        )
        return {
            "technology_options": fallback_result.model_dump(),
            "status": "tech_analysis_done",
            "current_agent": "technology_advisor",
        }


def node_architecture(state: ProjectState) -> dict:
    """Node: Run Architecture Agent with LOCKED technologies."""
    _notify("architecture", "running")
    try:
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}

        if not selected:
            raise ValueError("No technologies selected. Cannot generate architecture.")

        result = run_architecture_agent(requirements, selected)
        _notify("architecture", "completed")
        return {
            "architecture": result.model_dump(),
            "status": "architecture_done",
            "current_agent": "architecture",
        }
    except Exception as e:
        logger.error(f"Architecture Agent failed: {e}")
        _notify("architecture", "completed")
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}
        fallback = get_fallback_architecture_design(requirements, selected)
        return {
            "architecture": fallback.model_dump(),
            "status": "architecture_done",
            "current_agent": "architecture",
        }


def node_task_planner(state: ProjectState) -> dict:
    """Node: Run Task Planner Agent."""
    _notify("task_planner", "running")
    try:
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}
        architecture = _parse_architecture(state.get("architecture"), requirements, selected)

        result = run_task_planner(requirements, selected, architecture)
        _notify("task_planner", "completed")
        return {
            "task_plan": result.model_dump(),
            "status": "tasks_done",
            "current_agent": "task_planner",
        }
    except Exception as e:
        logger.error(f"Task Planner failed: {e}")
        _notify("task_planner", "completed")
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}
        architecture = _parse_architecture(state.get("architecture"), requirements, selected)
        fallback = get_fallback_task_plan(requirements, selected, architecture)
        return {
            "task_plan": fallback.model_dump(),
            "status": "tasks_done",
            "current_agent": "task_planner",
        }


def node_timeline(state: ProjectState) -> dict:
    """Node: Run Timeline & Resource Agent."""
    _notify("timeline", "running")
    try:
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}
        architecture = _parse_architecture(state.get("architecture"), requirements, selected)
        task_plan = _parse_task_plan(state.get("task_plan"), requirements, selected, architecture)

        result = run_timeline_agent(requirements, task_plan, selected)
        _notify("timeline", "completed")
        return {
            "timeline": result.model_dump(),
            "status": "timeline_done",
            "current_agent": "timeline",
        }
    except Exception as e:
        logger.error(f"Timeline Agent failed: {e}")
        _notify("timeline", "completed")
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}
        architecture = _parse_architecture(state.get("architecture"), requirements, selected)
        task_plan = _parse_task_plan(state.get("task_plan"), requirements, selected, architecture)
        fallback = get_fallback_timeline_plan(requirements, task_plan, selected)
        return {
            "timeline": fallback.model_dump(),
            "status": "timeline_done",
            "current_agent": "timeline",
        }


def node_critic(state: ProjectState) -> dict:
    """Node: Run Critic & Risk Agent."""
    _notify("critic", "running")
    try:
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}
        architecture = _parse_architecture(state.get("architecture"), requirements, selected)
        task_plan = _parse_task_plan(state.get("task_plan"), requirements, selected, architecture)
        timeline = _parse_timeline(state.get("timeline"), requirements, task_plan, selected)
        revision_count = state.get("revision_count", 0)

        result = run_critic_agent(
            requirements, selected, architecture, task_plan, timeline, revision_count
        )
        _notify("critic", "completed")

        new_status = "review_done"
        if result.decision == "needs_revision":
            max_rev = state.get("max_revisions", 3)
            if revision_count >= max_rev:
                result.decision = "approved"
                warnings = state.get("warnings", [])
                warnings.append(
                    f"Maximum revision limit ({max_rev}) reached. "
                    "Plan approved with remaining issues noted."
                )
                return {
                    "critique": result.model_dump(),
                    "status": "completed",
                    "current_agent": "critic",
                    "warnings": warnings,
                }

        return {
            "critique": result.model_dump(),
            "status": new_status,
            "current_agent": "critic",
            "revision_count": state.get("revision_count", 0) + (
                1 if result.decision == "needs_revision" else 0
            ),
        }
    except Exception as e:
        logger.error(f"Critic Agent failed: {e}")
        _notify("critic", "completed")
        requirements = ensure_project_requirements(state.get("requirements"))
        selected = state.get("selected_technologies") or {}
        architecture = _parse_architecture(state.get("architecture"), requirements, selected)
        task_plan = _parse_task_plan(state.get("task_plan"), requirements, selected, architecture)
        timeline = _parse_timeline(state.get("timeline"), requirements, task_plan, selected)
        fallback = get_fallback_critique_result(requirements, selected, architecture, task_plan, timeline)
        return {
            "critique": fallback.model_dump(),
            "status": "review_done",
            "current_agent": "critic",
        }


def node_generate_blueprint(state: ProjectState) -> dict:
    """Node: Generate the final blueprint from all agent outputs."""
    _notify("blueprint", "running")
    try:
        requirements = state.get("requirements") or {}
        if isinstance(requirements, ProjectRequirements):
            requirements = requirements.model_dump()
        tech_options = state.get("technology_options") or {}
        selected = state.get("selected_technologies") or {}
        architecture = state.get("architecture") or {}
        task_plan = state.get("task_plan") or {}
        timeline = state.get("timeline") or {}
        critique = state.get("critique") or {}

        cats = tech_options.get("categories", []) if isinstance(tech_options, dict) else []

        tasks = task_plan.get("tasks", []) if isinstance(task_plan, dict) else []
        task_deps = {}
        for t in tasks:
            if isinstance(t, dict):
                task_deps[t.get("task_id", "")] = t.get("dependencies", [])

        blueprint = {
            "project_overview": {
                "name": requirements.get("project_name", "") if isinstance(requirements, dict) else "",
                "description": requirements.get("project_description", "") if isinstance(requirements, dict) else "",
                "complexity": requirements.get("complexity", "") if isinstance(requirements, dict) else "",
                "team_size": requirements.get("team_size", 1) if isinstance(requirements, dict) else 1,
                "deadline_days": requirements.get("deadline_days", 30) if isinstance(requirements, dict) else 30,
            },
            "requirements": requirements,
            "selected_technology_stack": selected,
            "alternatives_considered": cats,
            "technology_rationale": {
                cat: (
                    f"Category intentionally excluded / Not Required for this project"
                    if tech == "Not Required"
                    else f"Selected {tech} for this project"
                )
                for cat, tech in selected.items()
            },
            "system_architecture": architecture,
            "development_tasks": tasks,
            "task_dependencies": task_deps,
            "timeline": timeline.get("schedule", []) if isinstance(timeline, dict) else [],
            "team_allocation": timeline.get("team_allocation", []) if isinstance(timeline, dict) else [],
            "milestones": task_plan.get("milestones", []) if isinstance(task_plan, dict) else [],
            "risk_analysis": critique.get("risks", []) if isinstance(critique, dict) else [],
            "mitigation_strategies": [
                {"risk": r.get("explanation", r.get("risk", "")), "mitigation": r.get("mitigation", "")}
                for r in (critique.get("risks", []) if isinstance(critique, dict) else [])
                if isinstance(r, dict)
            ],
            "feasibility": {
                "score": critique.get("feasibility_score", 85) if isinstance(critique, dict) else 85,
                "timeline_feasibility": timeline.get("feasibility", "feasible") if isinstance(timeline, dict) else "feasible",
                "assessment": critique.get("overall_feedback", critique.get("overall_assessment", "Plan approved")) if isinstance(critique, dict) else "Plan approved",
            },
            "deployment_plan": architecture.get("deployment_plan", {}) if isinstance(architecture, dict) else {},
            "development_roadmap": task_plan.get("phases", []) if isinstance(task_plan, dict) else [],
            "warnings": state.get("warnings", []),
            "technology_warnings": critique.get("technology_warnings", []) if isinstance(critique, dict) else [],
        }

        _notify("blueprint", "completed")
        return {
            "blueprint": blueprint,
            "status": "completed",
        }
    except Exception as e:
        logger.error(f"Blueprint generation failed: {e}")
        _notify("blueprint", "completed")
        return {
            "blueprint": {"project_overview": {"name": "Default Blueprint"}, "status": "completed"},
            "status": "completed",
        }


def should_revise(state: ProjectState) -> str:
    """Conditional edge: decide whether to revise or finalize.

    Returns:
        "revise" if the critic wants revision and we haven't hit max.
        "finalize" otherwise.
    """
    critique = state.get("critique", {})
    if not isinstance(critique, dict):
        return "finalize"

    decision = critique.get("decision", "approved")
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 3)

    if decision == "needs_revision" and revision_count < max_revisions:
        logger.info(f"Workflow: Revision requested (count {revision_count + 1}/{max_revisions})")
        return "revise"

    logger.info("Workflow: Proceeding to blueprint finalization")
    return "finalize"
