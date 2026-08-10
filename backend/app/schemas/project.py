"""ProjectForge AI — Project Schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------
class ProjectCreate(BaseModel):
    """Create a new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    raw_idea: str = ""


class ProjectResponse(BaseModel):
    """Project summary response."""
    id: int
    name: str
    description: str
    raw_idea: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectDetailResponse(BaseModel):
    """Full project response with all related data."""
    id: int
    name: str
    description: str
    raw_idea: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    requirements: Optional[Dict[str, Any]] = None
    technology_options: Optional[List[Dict[str, Any]]] = None
    selected_technologies: Optional[List[Dict[str, Any]]] = None
    architecture: Optional[Dict[str, Any]] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    team_members: Optional[List[Dict[str, Any]]] = None
    risks: Optional[List[Dict[str, Any]]] = None
    critiques: Optional[List[Dict[str, Any]]] = None
    blueprint: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Requirements
# ---------------------------------------------------------------------------
class RequirementsInput(BaseModel):
    """User submits project idea for requirement analysis."""
    project_idea: str = Field(..., min_length=10)


class RequirementsResponse(BaseModel):
    """Extracted requirements."""
    goals: List[str] = []
    features: List[str] = []
    team_size: int = 1
    deadline_days: int = 30
    budget: Optional[float] = None
    skill_level: str = "intermediate"
    preferred_technologies: List[str] = []
    constraints: List[str] = []
    complexity: str = "medium"


# ---------------------------------------------------------------------------
# Technology Selection
# ---------------------------------------------------------------------------
class TechnologyOptionResponse(BaseModel):
    """A single technology alternative."""
    id: int
    category: str
    name: str
    suitability_score: int
    advantages: List[str] = []
    disadvantages: List[str] = []
    difficulty: str
    fit_reason: str
    not_fit_reason: str
    is_recommended: bool

    class Config:
        from_attributes = True


class TechnologySelectionInput(BaseModel):
    """User's technology selections — one per category."""
    selections: Dict[str, str]
    # e.g. {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"}


class SelectedTechnologyResponse(BaseModel):
    """A locked technology selection."""
    category: str
    name: str
    is_locked: bool
    selected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Architecture
# ---------------------------------------------------------------------------
class ArchitectureResponse(BaseModel):
    """Generated architecture."""
    system_architecture: Dict[str, Any] = {}
    component_architecture: Dict[str, Any] = {}
    api_architecture: Dict[str, Any] = {}
    database_architecture: Dict[str, Any] = {}
    auth_flow: Dict[str, Any] = {}
    data_flow: Dict[str, Any] = {}
    deployment_architecture: Dict[str, Any] = {}
    diagrams: Dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
class TaskResponse(BaseModel):
    """A development task."""
    task_id: str
    title: str
    description: str
    phase: int
    priority: str
    estimated_hours: float
    complexity: int
    dependencies: List[str] = []
    assigned_role: str
    status: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------
class TimelineEntryResponse(BaseModel):
    """A timeline entry."""
    task_id: str
    start_day: int
    end_day: int
    assigned_member: str
    is_critical: bool

    class Config:
        from_attributes = True


class MilestoneResponse(BaseModel):
    """A milestone."""
    name: str
    target_day: int
    associated_tasks: List[str] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Risk
# ---------------------------------------------------------------------------
class RiskResponse(BaseModel):
    """A project risk."""
    category: str
    severity: str
    probability: str
    impact: str
    explanation: str
    mitigation: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------
class BlueprintResponse(BaseModel):
    """Final project blueprint."""
    content: Dict[str, Any] = {}
    feasibility_score: str = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
