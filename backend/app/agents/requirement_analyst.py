"""ProjectForge AI — Requirement Analyst Agent.

Agent 1 of 6: Extracts structured project requirements from a user's
raw project idea.
"""
import logging
from backend.app.llm.factory import LLMFactory
from backend.app.schemas.agent import ProjectRequirements

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Requirement Analyst Agent for ProjectForge AI, a project planning platform.

Your job is to analyze a user's project idea and extract structured requirements.

You must identify:
1. A suitable project name
2. A brief project description
3. Project goals (what the project aims to achieve)
4. Required features (specific features needed)
5. Team size (number of people working on it)
6. Deadline (in days)
7. Budget (if mentioned, otherwise null)
8. Technical skill level of the team (beginner/intermediate/advanced)
9. Preferred technologies (if the user mentions any)
10. Constraints (time, budget, technical, or other limitations)
11. Estimated project complexity (low/medium/high)
12. Special requirements (accessibility, compliance, scalability, etc.)

Be thorough but realistic. If information is not provided, make reasonable inferences
based on the context. For example:
- If no team size is mentioned, estimate based on project scope
- If no deadline is mentioned, suggest a reasonable one
- If skill level isn't stated, assume intermediate

Always provide multiple features — break down the project into concrete capabilities.
Always provide multiple goals — what does the user want to achieve?
"""


def run_requirement_analyst(project_idea: str) -> ProjectRequirements:
    """Run the Requirement Analyst Agent.

    Args:
        project_idea: Raw user project idea text.

    Returns:
        Structured ProjectRequirements.
    """
    logger.info("Requirement Analyst Agent: Starting analysis")

    try:
        llm = LLMFactory.get_provider_for_agent("requirement_analyst")

        prompt = f"""Analyze the following project idea and extract structured requirements.

PROJECT IDEA:
{project_idea}

Extract all requirements including goals, features, team size, deadline, budget,
skill level, preferred technologies, constraints, complexity, and special requirements.

Be specific and thorough. Generate realistic features that such a project would need.
If the user mentions specific numbers (team size, days, budget), use those exact values.
If not mentioned, make reasonable inferences based on the project scope.
"""

        result = llm.generate_structured(
            prompt=prompt,
            output_schema=ProjectRequirements,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.4,
        )

        logger.info(f"Requirement Analyst Agent: Extracted {len(result.features)} features, "
                    f"team_size={result.team_size}, deadline={result.deadline_days} days")

        return result

    except Exception as e:
        logger.warning(
            f"Requirement Analyst Agent: AI generation failed ({e}). "
            "Falling back to default structured requirements."
        )
        first_line = project_idea.strip().split("\n")[0][:40].strip() or "New Project"
        return ProjectRequirements(
            project_name=first_line,
            project_description=project_idea[:250],
            goals=[
                "Build a high quality web platform matching user specifications",
                "Ensure scalability, maintainability, and clean architecture",
            ],
            features=[
                "User Registration and Authentication",
                "Project Dashboard and Management",
                "Core Domain Application Workflows",
                "RESTful API & Database Integration",
            ],
            team_size=2,
            deadline_days=30,
            skill_level="intermediate",
            complexity="medium",
        )
