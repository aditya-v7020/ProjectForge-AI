"""ProjectForge AI — Tavily & Technology Advisor Integration Tests.

Tests Tavily web search integration, failure/timeout resilience, empty search handling,
LLM provider failover after Tavily errors, and catastrophic 10-category catalog fallback.
"""
import pytest
from unittest.mock import patch, MagicMock

from backend.app.schemas.agent import ProjectRequirements, TechnologyRecommendations
from backend.app.agents.technology_advisor import run_technology_advisor
from backend.app.tools.tavily_search import TavilySearchTool, SearchResults, SearchResult
from backend.app.llm.base import LLMProviderError


@pytest.fixture
def sample_requirements():
    return ProjectRequirements(
        project_name="E-Commerce AI Hub",
        project_description="Online marketplace with automated recommendations and high throughput payments",
        team_size=3,
        deadline_days=45,
        complexity="medium",
        preferred_technologies=["React", "FastAPI", "PostgreSQL"],
    )


def test_tavily_search_success():
    """Test successful Tavily search tool execution."""
    tool = TavilySearchTool()
    tool.api_key = "mock_tavily_key"

    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {
                "title": "React 19 Official Documentation",
                "url": "https://react.dev",
                "content": "React 19 features Server Actions, Asset Loading, and Compiler improvements.",
            },
            {
                "title": "FastAPI v0.115 Docs",
                "url": "https://fastapi.tiangolo.com",
                "content": "FastAPI is a modern, fast web framework for building APIs with Python.",
            }
        ]
    }

    with patch.object(tool, "_get_client", return_value=mock_client):
        res = tool.search("React 19 official docs", max_results=2)
        assert res.available is True
        assert len(res.results) == 2
        assert res.results[0].title == "React 19 Official Documentation"
        assert res.results[0].url == "https://react.dev"
        assert "React 19 features" in res.results[0].content


def test_tavily_search_empty_results():
    """Test Tavily returning empty search results."""
    tool = TavilySearchTool()
    tool.api_key = "mock_tavily_key"

    mock_client = MagicMock()
    mock_client.search.return_value = {"results": []}

    with patch.object(tool, "_get_client", return_value=mock_client):
        res = tool.search("obscure tech query 12345", max_results=3)
        assert res.available is True
        assert len(res.results) == 0


def test_tavily_search_timeout_or_service_error():
    """Test Tavily search graceful handling when request times out or throws an error."""
    tool = TavilySearchTool()
    tool.api_key = "mock_tavily_key"

    mock_client = MagicMock()
    mock_client.search.side_effect = Exception("HTTP 504 Gateway Timeout")

    with patch.object(tool, "_get_client", return_value=mock_client):
        res = tool.search("React docs", max_results=2)
        assert res.available is False
        assert "Tavily search failed" in res.note
        assert len(res.results) == 0


def test_tavily_missing_api_key():
    """Test Tavily tool behavior when TAVILY_API_KEY is not configured."""
    tool = TavilySearchTool()
    tool.api_key = None

    res = tool.search("FastAPI docs")
    assert res.available is False
    assert "Tavily API key not configured" in res.note


def test_technology_advisor_with_tavily_unavailable_continues_to_llm(sample_requirements):
    """Test: When Tavily search fails/times out, Technology Advisor continues to LLM without crashing."""
    with patch("backend.app.agents.technology_advisor.tavily_tool.search") as mock_search:
        mock_search.side_effect = Exception("Tavily service connection timeout")

        result = run_technology_advisor(sample_requirements)

        # Technology Advisor must succeed and return recommendations
        assert isinstance(result, TechnologyRecommendations)
        assert len(result.categories) >= 3
        # Ensure categories contain required technology fields
        cat_names = [c.category for c in result.categories]
        assert "frontend" in cat_names
        assert "backend" in cat_names
        assert "database" in cat_names


def test_technology_advisor_llm_fallback_after_tavily_failure(sample_requirements):
    """Test: If Tavily fails AND primary LLM fails, FallbackLLMProvider automatically routes to candidate LLMs."""
    with patch("backend.app.agents.technology_advisor.tavily_tool.search", side_effect=Exception("Tavily 503 Service Unavailable")):
        # Mock primary LLM throwing 429 rate limit error, secondary LLM succeeding
        mock_primary = MagicMock()
        mock_primary.model_name = "primary-model"
        mock_primary.generate_structured.side_effect = LLMProviderError("Primary LLM 429 Rate Limit Exceeded")

        mock_fallback = MagicMock()
        mock_fallback.model_name = "fallback-model"
        mock_fallback.generate_structured.return_value = TechnologyRecommendations(
            categories=[
                {
                    "category": "frontend",
                    "recommendation": "React",
                    "recommendation_reason": "High performance SPA framework",
                    "alternatives": [
                        {"name": "React", "suitability_score": 90, "is_recommended": True},
                        {"name": "Vue.js", "suitability_score": 80, "is_recommended": False},
                        {"name": "Angular", "suitability_score": 70, "is_recommended": False},
                        {"name": "Svelte", "suitability_score": 85, "is_recommended": False},
                    ]
                }
            ],
            overall_analysis="Fallback LLM succeeded"
        )

        with patch("backend.app.llm.factory.LLMFactory.get_provider_for_agent") as mock_factory:
            from backend.app.llm.fallback import FallbackLLMProvider
            fallback_provider = FallbackLLMProvider([mock_primary, mock_fallback])
            mock_factory.return_value = fallback_provider

            res = run_technology_advisor(sample_requirements)

            assert isinstance(res, TechnologyRecommendations)
            assert res.categories[0].recommendation == "React"


def test_technology_advisor_complete_catalog_fallback(sample_requirements):
    """Test: When Tavily AND ALL AI providers fail, Technology Advisor returns 10-category catalog fallback."""
    with patch("backend.app.agents.technology_advisor.tavily_tool.search", side_effect=Exception("Tavily Network Error")):
        with patch("backend.app.agents.technology_advisor.LLMFactory.get_provider_for_agent") as mock_factory:
            mock_failing_provider = MagicMock()
            mock_failing_provider.generate_structured.side_effect = LLMProviderError("All LLM providers unavailable")
            mock_factory.return_value = mock_failing_provider

            res = run_technology_advisor(sample_requirements)

            # Must return clean 10-category fallback catalog
            assert isinstance(res, TechnologyRecommendations)
            assert len(res.categories) == 10
            cat_names = [c.category for c in res.categories]
            expected_cats = [
                "frontend", "backend", "database", "ai_ml", "authentication",
                "deployment", "api_communication", "devops", "caching_messaging", "testing"
            ]
            for cat in expected_cats:
                assert cat in cat_names

            # Verify every category has 4 alternatives and a recommended option
            for category in res.categories:
                assert len(category.alternatives) == 4
                assert any(alt.is_recommended for alt in category.alternatives)


def test_requirements_endpoint_with_tavily_and_llm_failure(client, auth_headers, db_session):
    """Test: POST /api/projects/{id}/requirements returns 200 OK even when Tavily AND all LLMs fail."""
    # Create project in DB
    from backend.app.models.user import User
    from backend.app.models.project import Project

    user = db_session.query(User).filter_by(username="testuser").first()
    proj = Project(name="Resilience Project", raw_idea="Test idea for Tavily failure", user_id=user.id)
    db_session.add(proj)
    db_session.commit()
    db_session.refresh(proj)

    with patch("backend.app.agents.technology_advisor.tavily_tool.search", side_effect=Exception("Tavily Outage")):
        with patch("backend.app.llm.fallback.FallbackLLMProvider.generate_structured", side_effect=LLMProviderError("All LLMs quota exhausted")):
            res = client.post(f"/api/projects/{proj.id}/requirements", json={
                "project_idea": "I want an e-commerce website for handmade crafts with secure payment gateway"
            }, headers=auth_headers)

            # Endpoint MUST return 200 OK and NOT 500
            assert res.status_code == 200
            data = res.json()
            assert "requirements" in data
            assert "technology_options" in data
            assert len(data["technology_options"]["categories"]) == 10
