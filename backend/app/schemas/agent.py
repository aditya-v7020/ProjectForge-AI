"""ProjectForge AI — Agent Input/Output Schemas.

Structured Pydantic models that agents produce as output.
Used for structured LLM output parsing.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# Requirement Analyst Output
# ---------------------------------------------------------------------------
class ProjectRequirements(BaseModel):
    """Structured requirements extracted by the Requirement Analyst."""
    project_name: str = Field(default="Untitled Project", description="Inferred project name")
    project_description: str = Field(default="", description="Brief project description")
    goals: List[str] = Field(default_factory=list, description="Project goals")
    features: List[str] = Field(default_factory=list, description="Required features")
    team_size: int = Field(default=1, description="Number of team members")
    deadline_days: int = Field(default=30, description="Deadline in days")
    budget: Optional[float] = Field(default=None, description="Budget if mentioned")
    skill_level: str = Field(default="intermediate", description="Team skill level: beginner/intermediate/advanced")
    preferred_technologies: List[str] = Field(default_factory=list, description="Technologies the user prefers")
    constraints: List[str] = Field(default_factory=list, description="Project constraints")
    complexity: str = Field(default="medium", description="Estimated complexity: low/medium/high")
    special_requirements: List[str] = Field(default_factory=list, description="Any special requirements")


def ensure_project_requirements(data: Any) -> ProjectRequirements:
    """Safely convert any input (dict, JSON string, Pydantic model, or raw string)
    into a valid ProjectRequirements instance.
    """
    import json
    if isinstance(data, ProjectRequirements):
        return data
    if isinstance(data, str):
        data_str = data.strip()
        if not data_str:
            return ProjectRequirements()
        try:
            parsed = json.loads(data_str)
            if isinstance(parsed, str):  # handle double-serialized JSON strings
                parsed = json.loads(parsed)
            if isinstance(parsed, dict):
                return ProjectRequirements.model_validate(parsed)
        except Exception:
            pass
        return ProjectRequirements(project_description=data_str)
    if isinstance(data, dict):
        if "raw_data" in data and isinstance(data["raw_data"], dict):
            return ProjectRequirements.model_validate(data["raw_data"])
        return ProjectRequirements.model_validate(data)

    return ProjectRequirements()


# ---------------------------------------------------------------------------
# Technology Advisor Output
# ---------------------------------------------------------------------------
class TechAlternative(BaseModel):
    """A single technology alternative."""
    name: str = Field(..., description="Technology name")
    suitability_score: int = Field(default=0, ge=0, le=100, description="Suitability score 0-100")
    advantages: List[str] = Field(default_factory=list, description="Advantages for this project")
    disadvantages: List[str] = Field(default_factory=list, description="Disadvantages for this project")
    difficulty: str = Field(default="medium", description="Difficulty: easy/medium/hard")
    fit_reason: str = Field(default="", description="Why this technology fits")
    not_fit_reason: str = Field(default="", description="Why this technology may not fit")
    is_recommended: bool = Field(default=False, description="Whether this is the recommended option")


class TechCategory(BaseModel):
    """Technology alternatives for one category."""
    category: str = Field(..., description="Category name: frontend/backend/database/ai_ml/deployment/authentication")
    alternatives: List[TechAlternative] = Field(default_factory=list)
    recommendation: str = Field(default="", description="Recommended option name")
    recommendation_reason: str = Field(default="", description="Why this is recommended")


class TechnologyRecommendations(BaseModel):
    """Full technology analysis output."""
    categories: List[TechCategory] = Field(default_factory=list)
    overall_analysis: str = Field(default="", description="Overall technology analysis summary")
    web_research_used: bool = Field(default=False, description="Whether Tavily web search was used")
    web_research_note: str = Field(default="", description="Note about web research availability")


# ---------------------------------------------------------------------------
# Architecture Agent Output
# ---------------------------------------------------------------------------
class ArchitectureDesign(BaseModel):
    """Architecture generated using locked technology selections."""
    system_overview: str = Field(default="", description="High-level system architecture description")
    components: List[Dict[str, Any]] = Field(default_factory=list, description="System components")
    frontend_architecture: Dict[str, Any] = Field(default_factory=dict)
    backend_architecture: Dict[str, Any] = Field(default_factory=dict)
    database_design: Dict[str, Any] = Field(default_factory=dict)
    api_design: Dict[str, Any] = Field(default_factory=dict)
    auth_flow: Dict[str, Any] = Field(default_factory=dict)
    data_flow: Dict[str, Any] = Field(default_factory=dict)
    deployment_plan: Dict[str, Any] = Field(default_factory=dict)
    ai_ml_architecture: Optional[Dict[str, Any]] = Field(default=None)
    diagrams: List[Dict[str, str]] = Field(default_factory=list, description="Mermaid diagram descriptions")


# ---------------------------------------------------------------------------
# Task Planner Output
# ---------------------------------------------------------------------------
class TaskItem(BaseModel):
    """A single development task."""
    task_id: str = Field(..., description="Unique task ID like T1, T2")
    title: str = Field(..., description="Task title")
    description: str = Field(default="", description="Task description")
    phase: int = Field(default=1, description="Project phase number")
    priority: str = Field(default="medium", description="Priority: critical/high/medium/low")
    estimated_hours: float = Field(default=4, description="Estimated hours to complete")
    complexity: int = Field(default=2, ge=1, le=5, description="Complexity 1-5")
    dependencies: List[str] = Field(default_factory=list, description="List of dependency task IDs")
    assigned_role: str = Field(default="", description="Role responsible for this task")


class MilestoneItem(BaseModel):
    """A project milestone."""
    name: str = Field(..., description="Milestone name")
    target_day: int = Field(..., description="Target day number")
    associated_tasks: List[str] = Field(default_factory=list, description="Associated task IDs")


class TaskPlan(BaseModel):
    """Complete task plan output."""
    phases: List[Dict[str, Any]] = Field(default_factory=list, description="Phase descriptions")
    tasks: List[TaskItem] = Field(default_factory=list)
    milestones: List[MilestoneItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Timeline & Resource Agent Output
# ---------------------------------------------------------------------------
class ScheduledTask(BaseModel):
    """A task with scheduled timeline."""
    task_id: str
    title: str = ""
    start_day: int
    end_day: int
    assigned_member: str = ""
    is_critical: bool = False


class TeamMemberAllocation(BaseModel):
    """Team member with assigned tasks."""
    role: str
    name: str = ""
    assigned_tasks: List[str] = Field(default_factory=list)


class TimelinePlan(BaseModel):
    """Complete timeline output."""
    schedule: List[ScheduledTask] = Field(default_factory=list)
    team_allocation: List[TeamMemberAllocation] = Field(default_factory=list)
    milestones: List[MilestoneItem] = Field(default_factory=list)
    feasibility: str = Field(default="feasible", description="feasible/tight/unrealistic")
    feasibility_score: int = Field(default=80, ge=0, le=100)
    feasibility_notes: str = Field(default="")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations if timeline is tight/unrealistic")


# ---------------------------------------------------------------------------
# Critic & Risk Agent Output
# ---------------------------------------------------------------------------
class RiskItem(BaseModel):
    """A project risk."""
    category: str = Field(..., description="Risk category: technical/schedule/resource/budget/dependency")
    severity: str = Field(default="medium", description="Severity: low/medium/high/critical")
    probability: str = Field(default="medium", description="Probability: low/medium/high")
    impact: str = Field(default="medium", description="Impact: low/medium/high")
    explanation: str = Field(default="")
    mitigation: str = Field(default="")


class CritiqueResult(BaseModel):
    """Critic & Risk Agent output."""
    decision: str = Field(default="approved", description="approved or needs_revision")
    issues: List[str] = Field(default_factory=list, description="Issues found")
    corrections: List[str] = Field(default_factory=list, description="Suggested corrections")
    risks: List[RiskItem] = Field(default_factory=list)
    technology_warnings: List[str] = Field(default_factory=list, description="Warnings about locked tech selections")
    overall_assessment: str = Field(default="", description="Overall assessment summary")
    feasibility_score: int = Field(default=80, ge=0, le=100)
