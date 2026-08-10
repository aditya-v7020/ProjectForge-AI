"""ProjectForge AI — Regression Tests for Agent Data Flow."""
import json
import pytest
from unittest.mock import MagicMock, patch

from backend.app.schemas.agent import ProjectRequirements, TechnologyRecommendations, ensure_project_requirements
from backend.app.graph.nodes import node_requirement_analyst, node_technology_advisor
from backend.app.agents.technology_advisor import run_technology_advisor


def test_ensure_project_requirements_dict():
    """Test converting dict to ProjectRequirements."""
    data = {"project_name": "Test App", "features": ["Feature 1"], "team_size": 3}
    req = ensure_project_requirements(data)
    assert isinstance(req, ProjectRequirements)
    assert req.project_name == "Test App"
    assert req.features == ["Feature 1"]
    assert req.team_size == 3


def test_ensure_project_requirements_json_str():
    """Test converting JSON string to ProjectRequirements."""
    data_dict = {"project_name": "JSON App", "features": ["Auth"]}
    json_str = json.dumps(data_dict)
    req = ensure_project_requirements(json_str)
    assert isinstance(req, ProjectRequirements)
    assert req.project_name == "JSON App"


def test_ensure_project_requirements_double_encoded_json_str():
    """Test converting double-serialized JSON string to ProjectRequirements."""
    data_dict = {"project_name": "Double Encoded App"}
    double_str = json.dumps(json.dumps(data_dict))
    req = ensure_project_requirements(double_str)
    assert isinstance(req, ProjectRequirements)
    assert req.project_name == "Double Encoded App"


def test_ensure_project_requirements_plain_str():
    """Test converting plain unparsed string to ProjectRequirements gracefully."""
    plain_str = "Build an e-commerce website for 3 people in 30 days"
    req = ensure_project_requirements(plain_str)
    assert isinstance(req, ProjectRequirements)
    assert req.project_description == plain_str


def test_ensure_project_requirements_instance():
    """Test passing an existing ProjectRequirements instance."""
    inst = ProjectRequirements(project_name="Instance App")
    req = ensure_project_requirements(inst)
    assert req is inst
    assert req.project_name == "Instance App"


@patch("backend.app.agents.technology_advisor._perform_web_research", return_value="Web research mock")
@patch("backend.app.agents.technology_advisor.LLMFactory.get_provider_for_agent")
def test_technology_advisor_data_flow_regression(mock_llm_factory, mock_web_research):
    """Regression test: Ensure Technology Advisor accepts string or dict or model requirements without validation error."""
    mock_provider = MagicMock()
    mock_recommendations = TechnologyRecommendations(categories=[])
    mock_provider.generate_structured.return_value = mock_recommendations
    mock_llm_factory.return_value = mock_provider

    # String input (previously caused ValidationError: Input should be a valid dictionary or instance of ProjectRequirements)
    json_str = json.dumps({"project_name": "E-Commerce", "features": ["Cart", "Payment"]})
    result_str = run_technology_advisor(json_str)
    assert isinstance(result_str, TechnologyRecommendations)

    # Dict input
    req_dict = {"project_name": "E-Commerce", "features": ["Cart", "Payment"]}
    result_dict = run_technology_advisor(req_dict)
    assert isinstance(result_dict, TechnologyRecommendations)

    # Instance input
    req_inst = ProjectRequirements(project_name="E-Commerce")
    result_inst = run_technology_advisor(req_inst)
    assert isinstance(result_inst, TechnologyRecommendations)


@patch("backend.app.graph.nodes.run_technology_advisor")
def test_node_technology_advisor_handles_string_state(mock_run_tech):
    """Test node_technology_advisor handles stringified requirements in LangGraph state."""
    mock_recommendations = TechnologyRecommendations(categories=[])
    mock_run_tech.return_value = mock_recommendations

    state = {
        "project_id": 1,
        "raw_idea": "Build store",
        "requirements": json.dumps({"project_name": "Store App"}),  # Requirements stored as JSON string
    }

    result = node_technology_advisor(state)
    assert result["status"] == "tech_analysis_done"
    assert "error" not in result
