"""ProjectForge AI — Database Model Tests."""
from backend.app.models import (
    User, Project, Requirements, TechnologyOption, SelectedTechnology,
    Architecture, Task, TimelineEntry, Milestone, TeamMember, Risk, Blueprint,
)
from backend.app.services.project_service import ProjectService


def test_user_model(db_session):
    """Test User creation and query."""
    user = User(username="alice", email="alice@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    saved = db_session.query(User).filter_by(username="alice").first()
    assert saved is not None
    assert saved.email == "alice@example.com"


def test_project_crud(db_session, test_user):
    """Test Project creation, read, update, delete."""
    svc = ProjectService(db_session)
    project = svc.create_project(test_user.id, "Test App", "Desc", "Idea")

    assert project.id is not None
    assert project.status == "created"

    retrieved = svc.get_project(project.id, test_user.id)
    assert retrieved.name == "Test App"

    svc.update_status(project.id, "completed")
    assert svc.get_project(project.id, test_user.id).status == "completed"

    deleted = svc.delete_project(project.id, test_user.id)
    assert deleted is True
    assert svc.get_project(project.id, test_user.id) is None


def test_locked_technology_selections(db_session, test_user):
    """Test saving and retrieving LOCKED technology selections."""
    svc = ProjectService(db_session)
    project = svc.create_project(test_user.id, "Tech Test", "", "")

    selections = {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
    }
    svc.save_selected_technologies(project.id, selections)

    locked = svc.get_selected_technologies(project.id)
    assert locked["frontend"] == "React"
    assert locked["backend"] == "FastAPI"
    assert locked["database"] == "PostgreSQL"
