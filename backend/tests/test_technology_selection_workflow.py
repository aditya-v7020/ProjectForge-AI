"""ProjectForge AI — Technology Selection & Locking Workflow Tests."""
import json
import pytest
from unittest.mock import MagicMock, patch

from backend.app.core.database import SessionLocal, init_db
from backend.app.models.user import User
from backend.app.models.project import Project, TechnologyOption, SelectedTechnology
from backend.app.services.project_service import ProjectService
from backend.app.graph.nodes import node_architecture
from backend.app.schemas.agent import ArchitectureDesign


@pytest.fixture
def test_user(db_session):
    user = db_session.query(User).filter_by(username="test_tech_workflow_user").first()
    if not user:
        user = User(
            username="test_tech_workflow_user",
            email="workflow_user@test.com",
            password_hash="fakehash123",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


def test_no_default_technology_selection(db_session, test_user):
    """Test: Technology Advisor generates options, but NO options are selected or locked by default."""
    svc = ProjectService(db_session)

    project = Project(
        user_id=test_user.id,
        name="No Default Tech Test",
        raw_idea="Test app",
        status="tech_analysis_done",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    sample_options = [
        {
            "category": "frontend",
            "alternatives": [
                {"name": "React", "suitability_score": 90, "is_recommended": True},
                {"name": "Vue", "suitability_score": 80, "is_recommended": False},
            ],
        },
        {
            "category": "backend",
            "alternatives": [
                {"name": "FastAPI", "suitability_score": 95, "is_recommended": True},
                {"name": "Express", "suitability_score": 75, "is_recommended": False},
            ],
        },
    ]

    svc.save_technology_options(project.id, sample_options)

    # Verify options exist — get_technology_options now returns ALL 10 canonical
    # categories (DB-sourced + catalog-filled), so we check the DB-sourced ones
    # are present and correctly populated.
    opts = svc.get_technology_options(project.id)
    assert len(opts) == 10, f"Expected 10 canonical categories, got {len(opts)}"

    # Verify the DB-sourced categories are included with correct data
    opts_by_cat = {o["category"]: o for o in opts}
    assert "frontend" in opts_by_cat
    assert "backend" in opts_by_cat
    fe_names = [a["name"] for a in opts_by_cat["frontend"]["alternatives"]]
    assert "React" in fe_names
    assert "Vue" in fe_names
    be_names = [a["name"] for a in opts_by_cat["backend"]["alternatives"]]
    assert "FastAPI" in be_names
    assert "Express" in be_names

    # Catalog-filled categories must also have alternatives
    for cat_obj in opts:
        assert len(cat_obj["alternatives"]) > 0, f"Category {cat_obj['category']} has 0 alternatives"

    # Verify NO selections exist by default
    selections = svc.get_selected_technologies(project.id)
    assert selections == {}, "Expected selected_technologies to be EMPTY by default!"

    selections_list = svc.get_selected_technologies_list(project.id)
    assert len(selections_list) == 0, "Expected 0 locked selections before user action!"


def test_user_can_select_and_change_options_before_locking(db_session, test_user):
    """Test: User can select options and change choices before final plan generation."""
    svc = ProjectService(db_session)

    project = Project(
        user_id=test_user.id,
        name="Tech Change Test",
        raw_idea="Test app idea",
        status="tech_analysis_done",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Initial selection: Vue + Express
    initial_choices = {"frontend": "Vue", "backend": "Express"}
    svc.save_selected_technologies(project.id, initial_choices)

    selections_1 = svc.get_selected_technologies(project.id)
    assert selections_1["frontend"] == "Vue"
    assert selections_1["backend"] == "Express"

    # User changes choice to React + FastAPI before final lock
    updated_choices = {"frontend": "React", "backend": "FastAPI"}
    svc.save_selected_technologies(project.id, updated_choices)

    selections_2 = svc.get_selected_technologies(project.id)
    assert selections_2["frontend"] == "React"
    assert selections_2["backend"] == "FastAPI"


def test_locking_persists_exact_selected_technologies(db_session, test_user):
    """Test: Locking persists the exact selections in PostgreSQL with is_locked=True."""
    svc = ProjectService(db_session)

    project = Project(
        user_id=test_user.id,
        name="Tech Locking Test",
        raw_idea="Test app idea",
        status="tech_analysis_done",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    user_selections = {
        "frontend": "Svelte",
        "backend": "Go",
        "database": "PostgreSQL",
    }

    saved = svc.save_selected_technologies(project.id, user_selections)
    assert len(saved) == 3
    for item in saved:
        assert item.is_locked is True

    # Query DB directly to verify persistence
    locked_rows = db_session.query(SelectedTechnology).filter_by(project_id=project.id).all()
    locked_dict = {row.category: row.name for row in locked_rows}
    assert locked_dict == user_selections


@patch("backend.app.graph.nodes.run_architecture_agent")
def test_downstream_agents_receive_locked_technology_stack(mock_run_arch, db_session, test_user):
    """Test: Downstream agent nodes (e.g. node_architecture) receive the EXACT locked technology stack."""
    mock_arch_result = ArchitectureDesign(
        system_overview="Mock System Architecture",
        components=[],
        frontend_architecture={},
        backend_architecture={},
        database_design={},
        api_design={},
        auth_flow={},
        data_flow={},
        deployment_plan={},
        diagrams=[],
    )
    mock_run_arch.return_value = mock_arch_result

    locked_stack = {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"}

    state = {
        "project_id": 1,
        "requirements": {
            "project_name": "Test App",
            "features": ["Auth"],
            "team_size": 2,
            "deadline_days": 14,
        },
        "selected_technologies": locked_stack,
    }

    result = node_architecture(state)

    assert result["status"] == "architecture_done"
    mock_run_arch.assert_called_once()
    call_args = mock_run_arch.call_args
    passed_selected_techs = call_args[0][1]
    assert passed_selected_techs == locked_stack, "Downstream node MUST receive exact locked tech stack!"


def test_not_required_technology_selection_persisted_and_passed(db_session, test_user):
    """Test: User selecting 'Not Required' for optional categories persists and is passed correctly."""
    svc = ProjectService(db_session)

    project = Project(
        user_id=test_user.id,
        name="Not Required Tech Test",
        raw_idea="Simple app idea",
        status="tech_analysis_done",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    user_selections = {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "SQLite",
        "ai_ml": "Not Required",
        "caching_messaging": "Not Required",
        "testing": "Not Required",
    }

    saved = svc.save_selected_technologies(project.id, user_selections)
    assert len(saved) == 6

    # Verify directly from database
    retrieved = svc.get_selected_technologies(project.id)
    assert retrieved["ai_ml"] == "Not Required"
    assert retrieved["caching_messaging"] == "Not Required"
    assert retrieved["testing"] == "Not Required"
    assert retrieved["frontend"] == "React"

