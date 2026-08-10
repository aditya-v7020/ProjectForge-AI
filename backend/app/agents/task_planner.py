"""ProjectForge AI — Task Planner Agent.

Agent 4 of 6: Breaks the project into realistic development tasks organized
into phases, with dependencies, priorities, and milestones.
"""
import logging
from typing import Dict, List
from backend.app.llm.factory import LLMFactory
from backend.app.schemas.agent import (
    ProjectRequirements, ArchitectureDesign, TaskPlan, TaskItem, MilestoneItem
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Task Planner Agent for ProjectForge AI.

Your job is to break a project into realistic, actionable development tasks.

CRITICAL RULES:
1. Tasks must be specific to the SELECTED technology stack.
2. Tasks must be realistic and actionable — not vague.
3. Dependencies must be logical (you can't integrate frontend with backend
   before both exist).
4. Time estimates must be realistic for the team's skill level.
5. Priorities must reflect actual development order.
6. If a technology category is marked as "Not Required" (e.g. ai_ml: "Not Required", testing: "Not Required"), DO NOT generate tasks, phases, or dependencies for that category.

TASK STRUCTURE:
- task_id: Unique ID (T1, T2, T3, ...)
- title: Clear, specific task title
- description: What needs to be done (2-3 sentences)
- phase: Phase number (1 = setup, 2 = core backend, 3 = frontend, etc.)
- priority: critical/high/medium/low
- estimated_hours: Realistic hours for one developer
- complexity: 1-5 scale
- dependencies: List of task_ids this depends on (e.g., ["T1", "T2"])
- assigned_role: Which team role handles this (e.g., "Backend Developer")

PHASE STRUCTURE (typical):
Phase 1: Project Setup & Foundation
Phase 2: Database & Backend Core
Phase 3: Authentication & Security
Phase 4: Frontend Foundation
Phase 5: Feature Implementation
Phase 6: Integration & Testing
Phase 7: Deployment & Launch

MILESTONES should mark phase completions and key deliverables.

Generate 15-30 tasks depending on project complexity.
Every task should be completable in 2-20 hours.
"""


def run_task_planner(
    requirements: ProjectRequirements,
    selected_technologies: Dict[str, str],
    architecture: ArchitectureDesign,
) -> TaskPlan:
    """Run the Task Planner Agent.

    Args:
        requirements: Structured project requirements.
        selected_technologies: Locked technology selections.
        architecture: Generated architecture.

    Returns:
        TaskPlan with phases, tasks, dependencies, and milestones.
    """
    logger.info("Task Planner Agent: Generating tasks")

    try:
        llm = LLMFactory.get_provider_for_agent("task_planner")

        tech_text = "\n".join(f"  {cat}: {tech}" for cat, tech in selected_technologies.items())

        prompt = f"""Create a detailed task plan for this project.

PROJECT:
  Name: {requirements.project_name}
  Team Size: {requirements.team_size}
  Deadline: {requirements.deadline_days} days
  Skill Level: {requirements.skill_level}
  Complexity: {requirements.complexity}

SELECTED TECHNOLOGY STACK:
{tech_text}

ARCHITECTURE OVERVIEW:
{architecture.system_overview}

KEY FEATURES TO BUILD:
{chr(10).join(f'  - {f}' for f in requirements.features)}

ARCHITECTURE COMPONENTS:
{chr(10).join(f'  - {c.get("name", "")}: {c.get("description", "")}' for c in architecture.components[:10])}

Create a comprehensive task plan with:
1. Multiple phases (setup → backend → frontend → integration → testing → deployment)
2. 15-30 specific tasks using the SELECTED technologies
3. Realistic time estimates based on team skill level ({requirements.skill_level})
4. Proper dependencies (e.g., database setup before API development)
5. Milestones at key phase completions
6. Role assignments considering team size of {requirements.team_size}

Generate the complete task plan now.
"""

        result = llm.generate_structured(
            prompt=prompt,
            output_schema=TaskPlan,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.4,
        )

        logger.info(f"Task Planner Agent: Generated {len(result.tasks)} tasks, "
                    f"{len(result.milestones)} milestones")
        return result

    except Exception as e:
        logger.warning(
            f"Task Planner Agent: AI generation failed ({e}). "
            "Using dynamic project-customized TaskPlan fallback."
        )
        return get_fallback_task_plan(requirements, selected_technologies, architecture)


def get_fallback_task_plan(
    requirements: ProjectRequirements,
    selected_technologies: Dict[str, str],
    architecture: ArchitectureDesign,
) -> TaskPlan:
    """Generate a dynamic, project-customized fallback task plan when all LLM providers fail.

    Customized to the user's specific features, selected technology stack, team size, and deadline.
    """
    frontend = selected_technologies.get("frontend", "React")
    backend = selected_technologies.get("backend", "FastAPI")
    database = selected_technologies.get("database", "PostgreSQL")
    auth = selected_technologies.get("authentication", "JWT")
    deployment = selected_technologies.get("deployment", "Docker")
    devops = selected_technologies.get("devops", "GitHub Actions")
    caching = selected_technologies.get("caching_messaging", "Redis")
    testing = selected_technologies.get("testing", "Pytest")
    ai_ml = selected_technologies.get("ai_ml")

    phases = [
        {"phase_number": 1, "name": "Project Setup & Foundation", "description": f"Initialize workspace, version control, and environments for {requirements.project_name}."},
        {"phase_number": 2, "name": "Database & Core Backend Services", "description": f"Design data models in {database} and build core API endpoints in {backend}."},
        {"phase_number": 3, "name": "Authentication & Security", "description": f"Implement {auth} stateless authentication and security interceptors."},
        {"phase_number": 4, "name": "Frontend Foundation & UI Shell", "description": f"Initialize {frontend} SPA, design tokens, routing, and HTTP client integration."},
        {"phase_number": 5, "name": "Feature Implementation", "description": f"Develop core project features: {', '.join(requirements.features[:3])}."},
        {"phase_number": 6, "name": "Integration, Caching & Testing", "description": f"Set up caching via {caching} and execute test suite with {testing}."},
        {"phase_number": 7, "name": "Deployment & Production Launch", "description": f"Containerize with {deployment} and automate deployment via {devops}."},
    ]

    tasks: List[TaskItem] = []
    task_counter = 1

    def next_id() -> str:
        nonlocal task_counter
        tid = f"T{task_counter}"
        task_counter += 1
        return tid

    # Phase 1: Setup
    t1 = next_id()
    tasks.append(TaskItem(
        task_id=t1,
        title=f"Initialize Repository & {requirements.project_name} Workspace",
        description=f"Configure git repository, directory structure, and development environment for {requirements.project_name}.",
        phase=1, priority="critical", estimated_hours=4.0, complexity=1, dependencies=[], assigned_role="DevOps Engineer"
    ))

    t2 = next_id()
    tasks.append(TaskItem(
        task_id=t2,
        title=f"Set Up {backend} Backend Environment",
        description=f"Initialize {backend} project workspace, dependency manifests, and environment variables.",
        phase=1, priority="critical", estimated_hours=6.0, complexity=2, dependencies=[t1], assigned_role="Backend Developer"
    ))

    t3 = next_id()
    tasks.append(TaskItem(
        task_id=t3,
        title=f"Configure {database} Database Instance",
        description=f"Provision {database} connection parameters, ORM configurations, and initial database migrations.",
        phase=1, priority="high", estimated_hours=6.0, complexity=2, dependencies=[t2], assigned_role="Database Administrator"
    ))

    # Phase 2: Database & Backend Core
    t4 = next_id()
    tasks.append(TaskItem(
        task_id=t4,
        title=f"Design {database} Entities & Schema Models",
        description=f"Implement relational tables and data models in {database} for application domain entities.",
        phase=2, priority="critical", estimated_hours=8.0, complexity=3, dependencies=[t3], assigned_role="Backend Developer"
    ))

    t5 = next_id()
    tasks.append(TaskItem(
        task_id=t5,
        title=f"Develop Core REST Endpoints in {backend}",
        description=f"Build foundation CRUD API routes in {backend} with request/response schema validation.",
        phase=2, priority="high", estimated_hours=12.0, complexity=3, dependencies=[t4], assigned_role="Backend Developer"
    ))

    # Phase 3: Auth & Security
    t6 = next_id()
    tasks.append(TaskItem(
        task_id=t6,
        title=f"Implement {auth} Token Security & Middleware",
        description=f"Build stateless token verification, password hashing, and endpoint security handlers using {auth}.",
        phase=3, priority="critical", estimated_hours=8.0, complexity=3, dependencies=[t5], assigned_role="Backend Developer"
    ))

    t7 = next_id()
    tasks.append(TaskItem(
        task_id=t7,
        title="Expose User Registration & Auth API Routes",
        description="Build user sign-up, login, token refresh, and session verification API endpoints.",
        phase=3, priority="high", estimated_hours=6.0, complexity=2, dependencies=[t6], assigned_role="Backend Developer"
    ))

    # Phase 4: Frontend Foundation
    t8 = next_id()
    tasks.append(TaskItem(
        task_id=t8,
        title=f"Initialize {frontend} Frontend Application",
        description=f"Set up {frontend} single-page app framework, client routing, and global styling tokens.",
        phase=4, priority="high", estimated_hours=8.0, complexity=2, dependencies=[t1], assigned_role="Frontend Developer"
    ))

    t9 = next_id()
    tasks.append(TaskItem(
        task_id=t9,
        title=f"Integrate HTTP Client & Auth Context in {frontend}",
        description=f"Configure HTTP API client interceptors, JWT token storage, and global user context.",
        phase=4, priority="high", estimated_hours=8.0, complexity=3, dependencies=[t7, t8], assigned_role="Frontend Developer"
    ))

    # Phase 5: Feature Implementation (Dynamically customized per project requirement feature)
    feature_tasks_p2 = []
    features_to_build = requirements.features if requirements.features else ["Core Workflow Management", "User Dashboard & Settings"]

    for feat in features_to_build:
        fid = next_id()
        feature_tasks_p2.append(fid)
        tasks.append(TaskItem(
            task_id=fid,
            title=f"Build Feature: {feat}",
            description=f"Implement backend services in {backend} and interactive UI views in {frontend} for '{feat}'.",
            phase=5, priority="critical" if len(feature_tasks_p2) <= 2 else "high",
            estimated_hours=12.0, complexity=3, dependencies=[t9], assigned_role="Fullstack Developer"
        ))

    # If AI/ML selected, add AI integration task
    if ai_ml and ai_ml.lower() != "not required":
        aiml_id = next_id()
        feature_tasks_p2.append(aiml_id)
        tasks.append(TaskItem(
            task_id=aiml_id,
            title=f"Integrate {ai_ml} Intelligence Engine",
            description=f"Build AI service adapter and prompt orchestrator using {ai_ml} for smart insights.",
            phase=5, priority="high", estimated_hours=10.0, complexity=4, dependencies=[t5], assigned_role="AI Engineer"
        ))

    # Phase 6: Integration & Testing
    t_test1 = next_id()
    tasks.append(TaskItem(
        task_id=t_test1,
        title=f"Configure {caching} Caching & Performance Layer",
        description=f"Integrate {caching} for session caching, query response optimization, and rate limiting.",
        phase=6, priority="medium", estimated_hours=6.0, complexity=3, dependencies=[t5], assigned_role="Backend Developer"
    ))

    t_test2 = next_id()
    tasks.append(TaskItem(
        task_id=t_test2,
        title=f"Automate Unit & API Integration Tests using {testing}",
        description=f"Write automated backend test suite with {testing} for endpoint validation and security compliance.",
        phase=6, priority="high", estimated_hours=10.0, complexity=3, dependencies=feature_tasks_p2 + [t_test1], assigned_role="QA Engineer"
    ))

    # Phase 7: Deployment
    t_dep1 = next_id()
    tasks.append(TaskItem(
        task_id=t_dep1,
        title=f"Containerize Application Services with {deployment}",
        description=f"Write multi-stage Dockerfiles and compose manifests for {backend}, {frontend}, and {database}.",
        phase=7, priority="high", estimated_hours=6.0, complexity=3, dependencies=[t_test2], assigned_role="DevOps Engineer"
    ))

    t_dep2 = next_id()
    tasks.append(TaskItem(
        task_id=t_dep2,
        title=f"Configure CI/CD Automation in {devops}",
        description=f"Configure automated build, test, and release pipelines using {devops}.",
        phase=7, priority="critical", estimated_hours=6.0, complexity=3, dependencies=[t_dep1], assigned_role="DevOps Engineer"
    ))

    # Calculate realistic milestone target days
    d_total = requirements.deadline_days if requirements.deadline_days else 30
    d1 = max(2, int(d_total * 0.15))
    d2 = max(5, int(d_total * 0.35))
    d3 = max(12, int(d_total * 0.75))
    d4 = d_total

    milestones = [
        MilestoneItem(name="M1: Foundation & Setup Complete", target_day=d1, associated_tasks=[t1, t2, t3]),
        MilestoneItem(name="M2: Database, API Core & Auth Complete", target_day=d2, associated_tasks=[t4, t5, t6, t7]),
        MilestoneItem(name="M3: Frontend App & Feature Delivery Complete", target_day=d3, associated_tasks=[t8, t9] + feature_tasks_p2),
        MilestoneItem(name="M4: Testing, Containerization & Production Launch", target_day=d4, associated_tasks=[t_test1, t_test2, t_dep1, t_dep2]),
    ]

    return TaskPlan(phases=phases, tasks=tasks, milestones=milestones)
