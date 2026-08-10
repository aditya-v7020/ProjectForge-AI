"""ProjectForge AI — Architecture Agent.

Agent 3 of 6: Generates project architecture using ONLY the user's
locked technology selections. Never substitutes user choices.
"""
import logging
from typing import Dict
from backend.app.llm.factory import LLMFactory
from backend.app.schemas.agent import ProjectRequirements, ArchitectureDesign

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Architecture Agent for ProjectForge AI.

Your job is to design a complete project architecture using the user's LOCKED
technology selections. You MUST use exactly the technologies the user selected.

CRITICAL RULES:
1. NEVER substitute, alter, or replace user-selected technologies.
2. If a category is set to "Not Required", DO NOT generate components, architecture modules, or diagrams for that category. Mention in system overview or relevant notes that the category was intentionally excluded per user choice.
3. If the user selected React for frontend, your architecture MUST use React.
4. If the user selected FastAPI for backend, your architecture MUST use FastAPI.
5. If the user selected MySQL for database, your architecture, table design, and Mermaid diagrams MUST use MySQL. Never substitute MySQL with PostgreSQL or SQLite.
6. If the user selected JWT for authentication, your architecture MUST specify JWT authentication. If authentication is "Not Required", omit authentication layers.
7. Design the architecture to work seamlessly with the locked stack.
8. Provide practical, implementable architecture.

Generate:
1. system_overview: High-level description of the entire system using locked stack
2. components: List of system components with their roles (omit excluded categories)
3. frontend_architecture: Frontend structure, routing, state management, key components
4. backend_architecture: Backend structure, API patterns, middleware, services
5. database_design: Tables/collections, relationships, key entities specific to selected database engine
6. api_design: REST endpoints, request/response patterns, error handling
7. auth_flow: Authentication flow if selected, or note "Not Required"
8. data_flow: How data moves through the system
9. deployment_plan: How to deploy with the selected deployment platform (or "Not Required")
10. ai_ml_architecture: Only if an AI/ML technology was explicitly selected (Set to None if "Not Required")
11. diagrams: Mermaid diagram descriptions showing system architecture with exact selected tech labels (omitting "Not Required" categories)
"""


def run_architecture_agent(
    requirements: ProjectRequirements,
    selected_technologies: Dict[str, str],
) -> ArchitectureDesign:
    """Run the Architecture Agent.

    Args:
        requirements: Structured project requirements.
        selected_technologies: User's LOCKED technology selections.

    Returns:
        ArchitectureDesign with complete project architecture.
    """
    logger.info(f"Architecture Agent: Designing for stack: {selected_technologies}")

    try:
        llm = LLMFactory.get_provider_for_agent("architecture")
        tech_text = "\n".join(f"  {cat}: {tech}" for cat, tech in selected_technologies.items())

        prompt = f"""Design a complete project architecture for the following project.

PROJECT:
  Name: {requirements.project_name}
  Description: {requirements.project_description}
  Team Size: {requirements.team_size}
  Deadline: {requirements.deadline_days} days
  Complexity: {requirements.complexity}
  Skill Level: {requirements.skill_level}

LOCKED TECHNOLOGY SELECTIONS (you MUST use these exactly):
{tech_text}

FEATURES TO SUPPORT:
{chr(10).join(f'  - {f}' for f in requirements.features)}

GOALS:
{chr(10).join(f'  - {g}' for g in requirements.goals)}

Design a practical, implementable architecture that:
1. Uses ONLY the selected technologies above
2. Supports all listed features
3. Is appropriate for a team of {requirements.team_size} over {requirements.deadline_days} days
4. Includes specific component names, API endpoints, and database tables
5. Includes at least one Mermaid diagram description

Generate the complete architecture now.
"""

        result = llm.generate_structured(
            prompt=prompt,
            output_schema=ArchitectureDesign,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.4,
        )

        logger.info(f"Architecture Agent: Generated {len(result.components)} components")
        return result

    except Exception as e:
        logger.warning(
            f"Architecture Agent: AI generation failed ({e}). "
            "Using fallback structured architecture design."
        )
        return get_fallback_architecture_design(requirements, selected_technologies)


def get_fallback_architecture_design(
    requirements: ProjectRequirements,
    selected_technologies: Dict[str, str],
) -> ArchitectureDesign:
    """Generate a reliable fallback ArchitectureDesign matching schema dict requirements when all LLM providers fail."""
    frontend = selected_technologies.get("frontend", "React")
    backend = selected_technologies.get("backend", "FastAPI")
    database = selected_technologies.get("database", "PostgreSQL")
    auth = selected_technologies.get("authentication", "JWT")
    deployment = selected_technologies.get("deployment", "Docker")
    devops = selected_technologies.get("devops", "GitHub Actions")

    return ArchitectureDesign(
        system_overview=f"Modular architecture for {requirements.project_name} built with {frontend}, {backend}, and {database}.",
        components=[
            {"name": "Frontend Web Client", "technology": frontend, "description": f"Single Page Application built with {frontend}"},
            {"name": "Backend Application Server", "technology": backend, "description": f"REST API server built with {backend}"},
            {"name": "Relational Persistence Layer", "technology": database, "description": f"Primary relational database engine ({database})"},
            {"name": "Security & Identity Module", "technology": auth, "description": f"Authentication and authorization token handler ({auth})"},
            {"name": "Container Operations Engine", "technology": deployment, "description": f"Deployment runtime packaging with {deployment}"},
        ],
        frontend_architecture={"framework": frontend, "structure": "Component-driven single page application", "state_management": "Context API"},
        backend_architecture={"framework": backend, "pattern": "REST API with layered controllers and service handlers", "validation": "Pydantic"},
        database_design={"engine": database, "pattern": "Relational schema with normalized tables and ORM persistence"},
        api_design={"type": "RESTful HTTP API", "format": "JSON", "error_handling": "Standard HTTP status codes and centralized exception handler"},
        auth_flow={"mechanism": auth, "type": "Stateless bearer token authentication"},
        data_flow={"flow": f"Client ({frontend}) -> REST API ({backend}) -> ORM -> Database ({database})"},
        deployment_plan={"platform": deployment, "automation": devops, "packaging": "Docker containerization"},
        ai_ml_architecture=None,
        diagrams=[
            {"type": "mermaid", "code": f"graph TD\n  Client[{frontend} SPA] --> API[{backend} Server]\n  API --> DB[({database} DB)]\n  API --> Auth[{auth} Auth]"}
        ]
    )
