"""ProjectForge AI — Project API Routes.

All project CRUD + agent workflow trigger endpoints.
"""
import asyncio
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.project import (
    ProjectCreate, ProjectResponse, TechnologySelectionInput,
)
from backend.app.services.project_service import ProjectService
from backend.app.services.agent_service import AgentService
from backend.app.services.progress_manager import progress_stream, send_progress
from backend.app.core import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["Projects"])


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new project."""
    svc = ProjectService(db)
    project = svc.create_project(
        user_id=user.id,
        name=data.name,
        description=data.description,
        raw_idea=data.raw_idea,
    )
    return ProjectResponse.model_validate(project)


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all projects for the current user."""
    svc = ProjectService(db)
    projects = svc.get_user_projects(user.id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get full project details."""
    svc = ProjectService(db)
    detail = svc.get_project_detail(project_id, user.id)
    if not detail:
        raise HTTPException(status_code=404, detail="Project not found.")
    return detail


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a project."""
    svc = ProjectService(db)
    if not svc.delete_project(project_id, user.id):
        raise HTTPException(status_code=404, detail="Project not found.")


# ---------------------------------------------------------------------------
# Phase 1: Requirements + Technology Analysis
# ---------------------------------------------------------------------------

@router.post("/{project_id}/requirements")
def analyze_requirements(
    project_id: int,
    data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit project idea and run Requirement Analyst + Technology Advisor.

    Body: {"project_idea": "I want to build..."}
    """
    if not settings.has_any_llm_key():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No LLM provider configured. Please set at least one API key "
                   "(GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY) in your .env file.",
        )

    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    project_idea = data.get("project_idea", "")
    if not project_idea or len(project_idea) < 10:
        raise HTTPException(
            status_code=400,
            detail="Project idea must be at least 10 characters long.",
        )

    # Update raw idea
    project.raw_idea = project_idea
    db.commit()

    try:
        agent_svc = AgentService(db)
        result = agent_svc.run_requirements_and_tech_analysis(project_id, project_idea)
        return result
    except Exception as e:
        logger.error(f"Phase 1 failed for project {project_id}: {e}")
        svc.update_status(project_id, "error")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Requirements Data (GET)
# ---------------------------------------------------------------------------

@router.get("/{project_id}/requirements")
def get_requirements(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get extracted requirements for a project."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    reqs = svc.get_requirements(project_id)
    if not reqs:
        raise HTTPException(
            status_code=404,
            detail="No requirements found. Run requirements analysis first.",
        )
    return reqs


# ---------------------------------------------------------------------------
# Technology Options & Selection
# ---------------------------------------------------------------------------

@router.get("/{project_id}/technology-options")
def get_technology_options(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get generated technology alternatives."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    options = svc.get_technology_options(project_id)
    if not options:
        raise HTTPException(
            status_code=404,
            detail="No technology options found. Run requirements analysis first.",
        )
    return {"categories": options}


@router.post("/{project_id}/technology-selection")
def select_technologies(
    project_id: int,
    data: TechnologySelectionInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """User selects and LOCKS technologies.

    Body: {"selections": {"frontend": "React", "backend": "FastAPI", ...}}
    """
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if not data.selections:
        raise HTTPException(
            status_code=400,
            detail="At least one technology selection is required.",
        )

    # Validate selections against available options
    options = svc.get_technology_options(project_id)
    available_categories = {opt["category"] for opt in options}
    available_techs = {}
    for opt in options:
        available_techs[opt["category"]] = [
            alt["name"] for alt in opt.get("alternatives", [])
        ]

    # Required categories by default
    required_categories = {"frontend", "backend", "database"}

    # Verify every REQUIRED category present in options has an explicit selection
    missing_required = [
        cat for cat in available_categories
        if cat in required_categories and not data.selections.get(cat)
    ]
    if missing_required:
        raise HTTPException(
            status_code=400,
            detail=f"Technology selection missing for required category: '{missing_required[0]}'. Please select a technology for all required categories before locking.",
        )

    for category, selected_name in data.selections.items():
        if category not in available_categories and category not in [
            "frontend", "backend", "database", "ai_ml", "authentication",
            "deployment", "api_communication", "devops", "caching_messaging", "testing"
        ]:
            raise HTTPException(
                status_code=400,
                detail=f"Category '{category}' not found in technology options.",
            )
        if selected_name != "Not Required" and selected_name not in available_techs.get(category, []):
            logger.warning(
                f"Selected '{selected_name}' for '{category}' not in generated options."
            )

    # Save and LOCK selections
    svc.save_selected_technologies(project_id, data.selections)
    svc.update_status(project_id, "tech_selected")

    send_progress(project_id, "user_selection", "completed")

    return {
        "message": "Technologies selected and LOCKED.",
        "selections": data.selections,
        "locked": True,
    }


# ---------------------------------------------------------------------------
# Phase 2: Generate Full Plan
# ---------------------------------------------------------------------------

@router.post("/{project_id}/generate-plan")
def generate_plan(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Run Phase 2: Architecture → Tasks → Timeline → Critic → Blueprint.

    Requires technologies to be selected and locked first.
    """
    if not settings.has_any_llm_key():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No LLM provider configured. Please set at least one API key.",
        )

    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Verify technologies are selected
    selected = svc.get_selected_technologies(project_id)
    if not selected:
        raise HTTPException(
            status_code=400,
            detail="No technologies selected. Select technologies first.",
        )

    try:
        agent_svc = AgentService(db)
        result = agent_svc.run_plan_generation(project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Phase 2 failed for project {project_id}: {e}")
        svc.update_status(project_id, "error")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Individual Data Endpoints
# ---------------------------------------------------------------------------

@router.get("/{project_id}/architecture")
def get_architecture(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get generated architecture."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    arch = svc.get_architecture(project_id)
    if not arch:
        raise HTTPException(status_code=404, detail="Architecture not generated yet.")
    return arch


@router.get("/{project_id}/tasks")
def get_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get generated tasks."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return {"tasks": svc.get_tasks(project_id)}


@router.get("/{project_id}/timeline")
def get_timeline(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get generated timeline."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return svc.get_timeline(project_id)


@router.get("/{project_id}/risks")
def get_risks(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get risk analysis."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return {"risks": svc.get_risks(project_id)}


@router.get("/{project_id}/blueprint")
def get_blueprint(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the final project blueprint."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    bp = svc.get_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=404, detail="Blueprint not generated yet.")
    return bp


# ---------------------------------------------------------------------------
# SSE Progress Stream
# ---------------------------------------------------------------------------

@router.get("/{project_id}/progress")
async def stream_progress(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """SSE endpoint for real-time agent progress updates."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    return StreamingResponse(
        progress_stream(project_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Demo Data
# ---------------------------------------------------------------------------

@router.post("/demo/seed")
def seed_demo_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Load demo project with pre-generated data."""
    from backend.app.services.demo_data import create_demo_project
    try:
        project = create_demo_project(db, user.id)
        return {
            "message": "Demo project created successfully.",
            "project_id": project.id,
            "project_name": project.name,
        }
    except Exception as e:
        logger.error(f"Demo data seeding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Feature 2: AI Project Chat
# ---------------------------------------------------------------------------

@router.post("/{project_id}/chat")
def project_chat(
    project_id: int,
    data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Ask questions about the active project using full context & LLM fallback."""
    svc = ProjectService(db)
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    return svc.chat_about_project(project_id, user.id, message, history)


# ---------------------------------------------------------------------------
# Feature 3: Project Health Score
# ---------------------------------------------------------------------------

@router.get("/{project_id}/health-score")
def get_project_health_score(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get calculated health score and architectural metrics."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    return svc.calculate_health_score(project_id, user.id)


# ---------------------------------------------------------------------------
# Feature 4: Regenerate / Improve Agent Output
# ---------------------------------------------------------------------------

@router.post("/{project_id}/regenerate/{stage}")
def regenerate_stage(
    project_id: int,
    stage: str,
    data: dict = {},
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Regenerate or improve an individual agent's output without re-running full workflow."""
    agent_svc = AgentService(db)
    feedback = data.get("feedback", "")
    try:
        result = agent_svc.regenerate_stage(project_id, stage, feedback)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Regeneration failed for stage '{stage}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Feature 5: Export Project Blueprint (JSON, Markdown, PDF)
# ---------------------------------------------------------------------------

@router.get("/{project_id}/export/{export_format}")
def export_project_blueprint(
    project_id: int,
    export_format: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export the project blueprint as JSON, Markdown, or PDF format."""
    svc = ProjectService(db)
    try:
        result = svc.export_project(project_id, user.id, export_format)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Export failed for format '{export_format}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Feature 7: Cost Estimation
# ---------------------------------------------------------------------------

@router.get("/{project_id}/cost-estimation")
def get_cost_estimation(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get approximate development labor and cloud infrastructure costs."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    return svc.calculate_cost_estimation(project_id, user.id)


# ---------------------------------------------------------------------------
# Feature 8: Interactive Risk Suggestions
# ---------------------------------------------------------------------------

@router.post("/{project_id}/risks/suggest")
def suggest_risk_mitigation(
    project_id: int,
    data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get AI mitigation and improvement suggestions for a specific risk."""
    svc = ProjectService(db)
    try:
        result = svc.suggest_risk_mitigation(project_id, user.id, data)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Risk suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Feature 9: Tavily Research Sources
# ---------------------------------------------------------------------------

@router.get("/{project_id}/tavily-sources")
def get_tavily_sources(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get research sources used by Technology Advisor agent."""
    svc = ProjectService(db)
    project = svc.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    return svc.get_tavily_sources(project_id, user.id)







