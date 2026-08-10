"""ProjectForge AI — Task Planner Resilience & Failover Tests.

Tests Task Planner agent model resolution, LLM provider failover,
dynamic fallback task plan generation, and node execution in Phase 2 workflow.
"""
import pytest
from unittest.mock import patch, MagicMock

from backend.app.schemas.agent import (
    ProjectRequirements, ArchitectureDesign, TaskPlan
)
from backend.app.agents.task_planner import run_task_planner, get_fallback_task_plan
from backend.app.graph.nodes import node_task_planner
from backend.app.llm.base import LLMProviderError


@pytest.fixture
def sample_requirements():
    return ProjectRequirements(
        project_name="Smart Logistics Platform",
        project_description="Real-time fleet tracking and automated dispatch engine",
        team_size=4,
        deadline_days=60,
        skill_level="intermediate",
        complexity="high",
        features=[
            "Real-time GPS Fleet Tracking Dashboard",
            "Automated Dispatch & Route Optimization",
            "Driver Mobile Portal & Push Notifications"
        ]
    )


@pytest.fixture
def sample_technologies():
    return {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "authentication": "JWT",
        "deployment": "Docker",
        "devops": "GitHub Actions",
        "caching_messaging": "Redis",
        "testing": "Pytest",
        "ai_ml": "Google Gemini"
    }


@pytest.fixture
def sample_architecture():
    return ArchitectureDesign(
        system_overview="Microservice-oriented logistics processing hub",
        architecture_type="Microservices",
        components=[
            {"name": "Fleet Tracking Gateway", "description": "High throughput ingestion endpoint"},
            {"name": "Dispatch Engine Service", "description": "Algorithmic route optimization engine"}
        ]
    )


def test_task_planner_fallback_is_dynamically_customized(
    sample_requirements, sample_technologies, sample_architecture
):
    """Test: get_fallback_task_plan generates dynamic tasks customized to project requirements and technologies."""
    fallback_plan = get_fallback_task_plan(
        sample_requirements, sample_technologies, sample_architecture
    )

    assert isinstance(fallback_plan, TaskPlan)
    assert len(fallback_plan.phases) == 7
    assert len(fallback_plan.tasks) >= 12
    assert len(fallback_plan.milestones) == 4

    # Verify project-specific customization in task titles & descriptions
    task_titles = [t.title for t in fallback_plan.tasks]
    assert any("Real-time GPS Fleet Tracking Dashboard" in title for title in task_titles)
    assert any("Automated Dispatch & Route Optimization" in title for title in task_titles)
    assert any("FastAPI" in title or "React" in title or "PostgreSQL" in title for title in task_titles)

    # Verify task attributes
    for task in fallback_plan.tasks:
        assert task.task_id.startswith("T")
        assert task.estimated_hours > 0
        assert task.assigned_role != ""
        assert 1 <= task.phase <= 7


def test_task_planner_catastrophic_ai_outage_returns_fallback(
    sample_requirements, sample_technologies, sample_architecture
):
    """Test: When all LLM providers fail, run_task_planner catches the error and returns fallback TaskPlan."""
    with patch("backend.app.agents.task_planner.LLMFactory.get_provider_for_agent") as mock_factory:
        mock_failing_provider = MagicMock()
        mock_failing_provider.generate_structured.side_effect = LLMProviderError("All LLMs offline / quota exceeded")
        mock_factory.return_value = mock_failing_provider

        result = run_task_planner(
            sample_requirements, sample_technologies, sample_architecture
        )

        assert isinstance(result, TaskPlan)
        assert len(result.tasks) >= 12
        assert len(result.milestones) == 4


def test_task_planner_llm_provider_failover(
    sample_requirements, sample_technologies, sample_architecture
):
    """Test: Task Planner LLM provider failover (Primary Groq fails -> Candidate provider succeeds)."""
    mock_primary = MagicMock()
    mock_primary.model_name = "groq/llama-3.3-70b-versatile"
    mock_primary.generate_structured.side_effect = LLMProviderError("Groq 429 Rate Limit Exceeded")

    mock_candidate = MagicMock()
    mock_candidate.model_name = "openrouter/openrouter/auto"
    mock_candidate.generate_structured.return_value = get_fallback_task_plan(
        sample_requirements, sample_technologies, sample_architecture
    )

    with patch("backend.app.agents.task_planner.LLMFactory.get_provider_for_agent") as mock_factory:
        from backend.app.llm.fallback import FallbackLLMProvider
        fallback_provider = FallbackLLMProvider([mock_primary, mock_candidate])
        mock_factory.return_value = fallback_provider

        result = run_task_planner(
            sample_requirements, sample_technologies, sample_architecture
        )

        assert isinstance(result, TaskPlan)
        assert len(result.tasks) >= 10


def test_node_task_planner_executes_successfully_and_notifies(
    sample_requirements, sample_technologies, sample_architecture
):
    """Test: node_task_planner in LangGraph workflow returns completed status and state task_plan."""
    state = {
        "requirements": sample_requirements.model_dump(),
        "selected_technologies": sample_technologies,
        "architecture": sample_architecture.model_dump(),
    }

    with patch("backend.app.graph.nodes._notify") as mock_notify:
        node_output = node_task_planner(state)

        assert node_output["status"] == "tasks_done"
        assert "task_plan" in node_output
        assert len(node_output["task_plan"]["tasks"]) >= 10

        # Verify notifications emitted for Live AI Activity panel
        mock_notify.assert_any_call("task_planner", "running")
        mock_notify.assert_any_call("task_planner", "completed")
