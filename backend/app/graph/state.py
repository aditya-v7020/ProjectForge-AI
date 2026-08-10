"""ProjectForge AI — LangGraph State Definition.

TypedDict-based state that flows through the agent workflow.
"""
from typing import TypedDict, Optional, List, Dict, Any


class ProjectState(TypedDict, total=False):
    """State object that travels through the LangGraph workflow.

    This carries all data between agents. It is persisted to the database
    between Phase 1 (requirements + tech analysis) and Phase 2 (architecture
    through final blueprint).
    """
    # --- Project Identity ---
    project_id: int
    raw_idea: str

    # --- Agent Outputs ---
    requirements: Optional[Dict[str, Any]]  # ProjectRequirements as dict
    technology_options: Optional[Dict[str, Any]]  # TechnologyRecommendations as dict
    selected_technologies: Optional[Dict[str, str]]  # {"frontend": "React", ...}
    architecture: Optional[Dict[str, Any]]  # ArchitectureDesign as dict
    task_plan: Optional[Dict[str, Any]]  # TaskPlan as dict
    timeline: Optional[Dict[str, Any]]  # TimelinePlan as dict
    critique: Optional[Dict[str, Any]]  # CritiqueResult as dict

    # --- Workflow Control ---
    status: str  # Current workflow status
    revision_count: int  # Number of revision cycles completed
    max_revisions: int  # Maximum allowed revisions (default: 3)
    current_agent: str  # Currently running agent name

    # --- Final Output ---
    blueprint: Optional[Dict[str, Any]]  # Final blueprint content

    # --- Error Handling ---
    error: Optional[str]  # Error message if something fails
    warnings: List[str]  # Non-fatal warnings
