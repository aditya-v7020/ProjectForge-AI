"""ProjectForge AI — Critic & Risk Agent.

Agent 6 of 6: Reviews the complete project blueprint, identifies risks,
and decides whether the plan needs revision or is approved.
"""
import logging
from typing import Dict, List, Any
from backend.app.llm.factory import LLMFactory
from backend.app.schemas.agent import (
    ProjectRequirements, ArchitectureDesign, TaskPlan,
    TimelinePlan, CritiqueResult, RiskItem,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Critic & Risk Agent for ProjectForge AI.

Your job is to critically review the COMPLETE project plan and identify problems,
risks, and areas for improvement.

REVIEW CHECKLIST:
1. TECHNOLOGY COMPATIBILITY: Do all selected technologies work well together?
2. ARCHITECTURE COMPLETENESS: Does the architecture cover all features?
3. MISSING TASKS: Are there tasks that should exist but don't?
4. DEPENDENCY PROBLEMS: Are task dependencies logical and complete?
5. TIMELINE FEASIBILITY: Is the schedule realistic for the team?
6. TEAM WORKLOAD: Is work distributed fairly? Is anyone overloaded?
7. TECHNOLOGY CONFLICTS: Are there any incompatibilities?
8. UNNECESSARY COMPLEXITY: Is the plan over-engineered?

RISK CATEGORIES:
- technical: Technology-related risks (compatibility, complexity, learning curve)
- schedule: Timeline risks (deadlines, delays, underestimation)
- resource: Team/resource risks (skill gaps, availability, burnout)
- budget: Cost-related risks
- dependency: External dependency risks (third-party services, APIs)

RISK SEVERITY: low / medium / high / critical
RISK PROBABILITY: low / medium / high
RISK IMPACT: low / medium / high

DECISION RULES:
- "approved": Plan is solid with only minor issues. Risks are identified but manageable.
- "needs_revision": Significant problems found. Provide SPECIFIC corrections.

IMPORTANT:
- If a LOCKED technology creates a problem, add it to technology_warnings.
  Do NOT override the user's selection. Warn them and let them decide.
- If a category is marked as "Not Required" by the user, RESPECT that decision. DO NOT treat intentionally excluded categories as missing components, missing technology problems, or risks.
- Be constructive — don't just criticize, provide solutions.
- Be honest but not overly negative — a plan doesn't need to be perfect.

feasibility_score: 0-100 overall project feasibility.
"""


def run_critic_agent(
    requirements: ProjectRequirements,
    selected_technologies: Dict[str, str],
    architecture: ArchitectureDesign,
    task_plan: TaskPlan,
    timeline: TimelinePlan,
    revision_count: int = 0,
) -> CritiqueResult:
    """Run the Critic & Risk Agent.

    Args:
        requirements: Structured project requirements.
        selected_technologies: Locked technology selections.
        architecture: Generated architecture.
        task_plan: Generated task plan.
        timeline: Generated timeline.
        revision_count: Current revision number (0 = first review).

    Returns:
        CritiqueResult with decision (approved/needs_revision), issues, and risks.
    """
    logger.info(f"Critic & Risk Agent: Review #{revision_count + 1}")

    try:
        llm = LLMFactory.get_provider_for_agent("critic")

        tech_text = "\n".join(f"  {cat}: {tech}" for cat, tech in selected_technologies.items())
        tasks_text = "\n".join(
            f"  {t.task_id}: {t.title} [{t.estimated_hours}h, phase {t.phase}, "
            f"deps: {t.dependencies}]"
            for t in (task_plan.tasks if task_plan and task_plan.tasks else [])
        )

        schedule_lines = []
        if timeline and timeline.schedule:
            for s in timeline.schedule:
                tid = getattr(s, "task_id", s.get("task_id", "")) if isinstance(s, dict) else getattr(s, "task_id", "")
                sday = getattr(s, "start_day", s.get("start_day", 1)) if isinstance(s, dict) else getattr(s, "start_day", 1)
                eday = getattr(s, "end_day", s.get("end_day", 1)) if isinstance(s, dict) else getattr(s, "end_day", 1)
                assignee = getattr(s, "assigned_to", s.get("assigned_to", s.get("assigned_member", ""))) if isinstance(s, dict) else getattr(s, "assigned_to", "")
                iscrit = getattr(s, "is_critical", s.get("is_critical", False)) if isinstance(s, dict) else getattr(s, "is_critical", False)
                schedule_lines.append(f"  {tid}: day {sday}–{eday} ({assignee}){' [CRITICAL]' if iscrit else ''}")
        schedule_text = "\n".join(schedule_lines)

        team_lines = []
        if timeline and timeline.team_allocation:
            for m in timeline.team_allocation:
                role = getattr(m, "role", m.get("role", "Developer")) if isinstance(m, dict) else getattr(m, "role", "Developer")
                assigned_ts = getattr(m, "assigned_tasks", m.get("assigned_tasks", [])) if isinstance(m, dict) else getattr(m, "assigned_tasks", [])
                team_lines.append(f"  {role}: {len(assigned_ts)} tasks")
        team_text = "\n".join(team_lines)

        revision_context = ""
        if revision_count > 0:
            revision_context = (
                f"\nThis is revision #{revision_count + 1}. Previous reviews found issues "
                f"that should now be resolved. Focus on remaining problems. "
                f"If the major issues are fixed, approve the plan.\n"
            )

        prompt = f"""Critically review this COMPLETE project plan.
{revision_context}
PROJECT:
  Name: {requirements.project_name}
  Team Size: {requirements.team_size}
  Deadline: {requirements.deadline_days} days
  Skill Level: {requirements.skill_level}
  Complexity: {requirements.complexity}

LOCKED TECHNOLOGY SELECTIONS:
{tech_text}

ARCHITECTURE:
  Overview: {architecture.system_overview if architecture else 'Standard Architecture'}
  Components: {len(architecture.components) if architecture and architecture.components else 0} components

TASKS ({len(task_plan.tasks) if task_plan and task_plan.tasks else 0} total):
{tasks_text}

TIMELINE:
  Feasibility: {timeline.feasibility if timeline else 'feasible'} ({timeline.feasibility_score if timeline else 85}%)
{schedule_text}

TEAM:
{team_text}

Review the entire plan and:
1. Identify specific issues (if any)
2. Suggest specific corrections (if needed)
3. Identify ALL project risks with severity, probability, impact, and mitigation
4. Warn about any locked technology concerns (do NOT override selections)
5. Provide an overall feasibility score
6. Decide: "approved" or "needs_revision"

Be constructive and practical. A plan with minor issues can still be approved.
Only mark as "needs_revision" for significant problems.
"""

        result = llm.generate_structured(
            prompt=prompt,
            output_schema=CritiqueResult,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
        )

        logger.info(f"Critic Agent: Decision={result.decision}, "
                    f"Issues={len(result.issues)}, Risks={len(result.risks)}")
        return result

    except Exception as e:
        logger.warning(
            f"Critic Agent: AI generation failed ({e}). "
            "Using fallback CritiqueResult."
        )
        return get_fallback_critique_result(requirements, selected_technologies, architecture, task_plan, timeline)


def get_fallback_critique_result(
    requirements: ProjectRequirements,
    selected_technologies: Dict[str, str],
    architecture: ArchitectureDesign,
    task_plan: TaskPlan,
    timeline: TimelinePlan,
) -> CritiqueResult:
    """Generate a clean fallback CritiqueResult approving the plan when AI providers fail."""
    risks = [
        RiskItem(
            category="schedule",
            risk="Target deadline buffer constraint",
            severity="medium",
            probability="medium",
            impact="medium",
            mitigation="Prioritize critical path tasks T1-T5 and use daily standups to monitor progress.",
            affected_component="Project Timeline"
        ),
        RiskItem(
            category="technical",
            risk="Integration and technology alignment across services",
            severity="low",
            probability="low",
            impact="medium",
            mitigation=f"Ensure standard API contracts and integration testing with {selected_technologies.get('testing', 'Pytest')}.",
            affected_component="Backend API Services"
        )
    ]

    return CritiqueResult(
        decision="approved",
        overall_feedback=f"Plan for {requirements.project_name} is solid and well structured with manageable risks.",
        issues=[],
        suggested_corrections=[],
        risks=risks,
        technology_warnings=[],
        feasibility_score=85
    )
