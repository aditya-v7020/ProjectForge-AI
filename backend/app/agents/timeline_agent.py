"""ProjectForge AI — Timeline & Resource Agent.

Agent 5 of 6: Creates a realistic timeline, allocates team members,
and detects unrealistic schedules.
"""
import logging
from typing import Dict, List, Any
from backend.app.llm.factory import LLMFactory
from backend.app.schemas.agent import (
    ProjectRequirements, TaskPlan, TimelinePlan, TaskItem,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Timeline & Resource Agent for ProjectForge AI.

Your job is to create a realistic project timeline and allocate tasks to team members.

CRITICAL DEADLINE & SCALING RULES:
1. The project has a configured target deadline of {deadline_days} days. You MUST scale and distribute the schedule across the entire duration up to {deadline_days} days.
2. The final scheduled task must complete on or near day {deadline_days}.
3. Respect task dependencies — a task cannot start before its dependencies finish.
4. Distribute work across team members fairly.
5. Identify the critical path (tasks that determine project duration).
6. Milestones MUST be spread logically from day 1 up to (and NEVER exceeding) day {deadline_days}.
7. Each item in `schedule` MUST include both `task_id` (e.g., T1) AND its descriptive `title` (e.g., "Design database schema").
8. DO NOT create timeline schedule entries or allocate team work for tasks or categories marked as "Not Required".

SCHEDULING RULES:
- Each team member works ~8 hours per day.
- Tasks are scheduled based on dependencies and team availability.
- Start day is 1 (not 0).
- Parallel work is allowed for independent tasks with enough team members.
- Add reasonable buffer time for integration and testing across the project timeline.

TEAM ALLOCATION:
- Create team member roles based on team size.
- For a 3-person team: e.g., "Developer 1 (Full-Stack)", "Developer 2 (Backend)", "Developer 3 (Frontend)"
- Assign tasks based on role fit.

FEASIBILITY:
- "feasible": Timeline fits comfortably within deadline
- "tight": Timeline fits but with little buffer
- "unrealistic": Timeline exceeds deadline or is dangerously compressed

feasibility_score: 0-100
- 90-100: Very comfortable
- 70-89: Feasible with normal effort
- 50-69: Tight, needs discipline
- 30-49: Very risky
- 0-29: Unrealistic
"""


def run_timeline_agent(
    requirements: ProjectRequirements,
    task_plan: TaskPlan,
    selected_technologies: Dict[str, str],
) -> TimelinePlan:
    """Run the Timeline & Resource Agent.

    Args:
        requirements: Structured project requirements.
        task_plan: Generated task plan with tasks and dependencies.
        selected_technologies: Locked technology selections.

    Returns:
        TimelinePlan with schedule, team allocation, and feasibility.
    """
    logger.info("Timeline & Resource Agent: Creating timeline")

    try:
        llm = LLMFactory.get_provider_for_agent("timeline")

        tasks_text = _format_tasks(task_plan.tasks)
        tech_text = "\n".join(f"  {cat}: {tech}" for cat, tech in selected_technologies.items())

        system_prompt = SYSTEM_PROMPT.format(deadline_days=requirements.deadline_days)

        prompt = f"""Create a realistic project timeline and team allocation.

PROJECT:
  Name: {requirements.project_name}
  Team Size: {requirements.team_size} people
  Target Deadline: {requirements.deadline_days} days
  Skill Level: {requirements.skill_level}

TECHNOLOGY STACK:
{tech_text}

TASKS TO SCHEDULE:
{tasks_text}

MILESTONES:
{chr(10).join(f'  - {m.name} (target day: {m.target_day})' for m in task_plan.milestones)}

Create:
1. A schedule mapping each task (with task_id, title, start_day, end_day) distributed across the {requirements.deadline_days}-day deadline
2. Team member definitions for {requirements.team_size} people with appropriate roles
3. Task assignments to specific team members
4. Identification of critical path tasks (is_critical=true)
5. Realistic milestone dates that NEVER exceed {requirements.deadline_days} days
6. Feasibility assessment (feasible/tight/unrealistic) with a score

Generate the complete timeline now.
"""

        result = llm.generate_structured(
            prompt=prompt,
            output_schema=TimelinePlan,
            system_prompt=system_prompt,
            temperature=0.3,
        )

        logger.info(f"Timeline Agent: Scheduled {len(result.schedule)} tasks, "
                    f"feasibility={result.feasibility} ({result.feasibility_score}%)")
        return result

    except Exception as e:
        logger.warning(
            f"Timeline Agent: AI generation failed ({e}). "
            "Using fallback structured timeline plan."
        )
        return get_fallback_timeline_plan(requirements, task_plan, selected_technologies)


def get_fallback_timeline_plan(
    requirements: ProjectRequirements,
    task_plan: TaskPlan,
    selected_technologies: Dict[str, str],
) -> TimelinePlan:
    """Generate a clean fallback TimelinePlan when AI providers fail."""
    total_days = requirements.deadline_days if requirements.deadline_days else 30
    tasks = task_plan.tasks if task_plan and task_plan.tasks else []

    schedule: List[Dict[str, Any]] = []
    team_members = [
        {"name": f"Developer {i+1}", "role": "Fullstack Developer", "tasks": [], "hours": 0.0}
        for i in range(max(1, requirements.team_size))
    ]

    current_day = 1
    days_per_task = max(1, total_days // max(1, len(tasks)))

    for idx, t in enumerate(tasks):
        start_day = current_day
        end_day = min(total_days, start_day + days_per_task)
        assigned = team_members[idx % len(team_members)]
        assigned["tasks"].append(t.task_id)
        assigned["hours"] += t.estimated_hours

        schedule.append({
            "task_id": t.task_id,
            "title": t.title,
            "start_day": start_day,
            "end_day": end_day,
            "assigned_to": assigned["name"],
            "is_critical": idx in [0, 1, 3, 5, len(tasks)-1],
        })

        if (idx + 1) % max(1, len(team_members)) == 0:
            current_day = min(total_days, current_day + days_per_task)

    team_alloc = [
        {
            "role": tm["role"],
            "member_name": tm["name"],
            "assigned_tasks": tm["tasks"],
            "total_hours": tm["hours"]
        }
        for tm in team_members
    ]

    crit_path = [s["task_id"] for s in schedule if s.get("is_critical")]

    return TimelinePlan(
        total_duration_days=total_days,
        feasibility="feasible",
        feasibility_score=85,
        feasibility_reason=f"Structured schedule distributed across {total_days} days for {requirements.team_size} team members.",
        schedule=schedule,
        team_allocation=team_alloc,
        critical_path=crit_path if crit_path else ["T1", "T4", "T5", "T10"],
        risks_identified=["Tight schedule buffer", "Dependency sequencing"]
    )


def _format_tasks(tasks: List[TaskItem]) -> str:
    """Format tasks into a readable text block for the LLM."""
    lines = []
    for t in tasks:
        deps = f" (depends on: {', '.join(t.dependencies)})" if t.dependencies else ""
        lines.append(
            f"  {t.task_id}: {t.title} "
            f"[{t.estimated_hours}h, {t.priority}, phase {t.phase}]{deps}"
        )
    return "\n".join(lines)
