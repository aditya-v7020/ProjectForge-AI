"""ProjectForge AI — Agent Orchestration Service.

Coordinates the two-phase LangGraph workflow execution and persists
results to the database.
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.services.project_service import ProjectService
from backend.app.services.progress_manager import send_progress
from backend.app.graph.workflow import run_phase1, run_phase2
from backend.app.graph.nodes import set_progress_callback

logger = logging.getLogger(__name__)


class AgentService:
    """Orchestrates agent workflow execution."""

    def __init__(self, db: Session):
        self.db = db
        self.project_service = ProjectService(db)

    def run_requirements_and_tech_analysis(
        self, project_id: int, raw_idea: str
    ) -> Dict[str, Any]:
        """Run Phase 1: Requirements → Technology Analysis."""
        logger.info(f"AgentService: Running Phase 1 for project {project_id}")

        def progress_cb(agent: str, status: str):
            send_progress(project_id, agent, status)

        set_progress_callback(progress_cb)

        # Initialize Phase 1 agent statuses
        send_progress(project_id, "requirement_analyst", "pending")
        send_progress(project_id, "technology_advisor", "pending")

        try:
            state = run_phase1(project_id, raw_idea)

            if state.get("error"):
                raise Exception(state["error"])

            requirements = state.get("requirements") or {}
            tech_options = state.get("technology_options") or {}

            self.project_service.save_requirements(project_id, requirements)

            user_id = self._get_project_user_id(project_id)
            project = self.project_service.get_project(project_id, user_id)
            if project and requirements.get("project_name"):
                project.name = requirements["project_name"]
                if requirements.get("project_description"):
                    project.description = requirements["project_description"]

            if tech_options.get("categories"):
                self.project_service.save_technology_options(
                    project_id, tech_options["categories"]
                )

            self.project_service.update_status(project_id, "tech_analysis_done")
            self.db.commit()

            return {
                "requirements": requirements,
                "technology_options": tech_options,
                "status": "tech_analysis_done",
            }

        finally:
            set_progress_callback(None)

    def run_plan_generation(
        self, project_id: int
    ) -> Dict[str, Any]:
        """Run Phase 2: Architecture → Tasks → Timeline → Critic → Blueprint."""
        logger.info(f"AgentService: Running Phase 2 for project {project_id}")

        selected = self.project_service.get_selected_technologies(project_id)
        if not selected:
            raise ValueError(
                "No technologies selected. Please select technologies before "
                "generating the plan."
            )

        requirements = self.project_service.get_requirements(project_id)
        if not requirements:
            raise ValueError("No requirements found. Please run requirements analysis first.")

        tech_options = self.project_service.get_technology_options(project_id)

        def progress_cb(agent: str, status: str):
            send_progress(project_id, agent, status)

        set_progress_callback(progress_cb)

        # Initialize Phase 2 agent statuses
        send_progress(project_id, "requirement_analyst", "completed")
        send_progress(project_id, "technology_advisor", "completed")
        send_progress(project_id, "user_selection", "completed")
        send_progress(project_id, "architecture", "pending")
        send_progress(project_id, "task_planner", "pending")
        send_progress(project_id, "timeline", "pending")
        send_progress(project_id, "critic", "pending")
        send_progress(project_id, "blueprint", "pending")

        try:
            state = {
                "project_id": project_id,
                "raw_idea": "",
                "requirements": requirements.get("raw_data", requirements),
                "technology_options": {"categories": tech_options},
                "selected_technologies": selected,
                "architecture": None,
                "task_plan": None,
                "timeline": None,
                "critique": None,
                "status": "tech_selected",
                "revision_count": 0,
                "max_revisions": 3,
                "current_agent": "",
                "blueprint": None,
                "error": None,
                "warnings": [],
            }

            result = run_phase2(state)

            if result.get("error"):
                raise Exception(result["error"])

            # Safely extract sub-dicts
            arch_data = result.get("architecture")
            task_data = result.get("task_plan") or {}
            timeline_data = result.get("timeline")
            critique_data = result.get("critique") or {}
            blueprint_data = result.get("blueprint")

            if arch_data:
                self.project_service.save_architecture(project_id, arch_data)

            if task_data and task_data.get("tasks"):
                self.project_service.save_tasks(project_id, task_data["tasks"])

            if timeline_data:
                self.project_service.save_timeline(project_id, timeline_data)

            if critique_data:
                self.project_service.save_critique(
                    project_id, critique_data,
                    revision_number=result.get("revision_count", 0)
                )
                if critique_data.get("risks"):
                    self.project_service.save_risks(project_id, critique_data["risks"])

            if blueprint_data:
                feasibility = str(critique_data.get("feasibility_score", ""))
                self.project_service.save_blueprint(
                    project_id, blueprint_data, feasibility
                )

            self.project_service.update_status(project_id, "completed")
            self.db.commit()

            return {
                "architecture": arch_data,
                "task_plan": task_data,
                "timeline": timeline_data,
                "critique": critique_data,
                "blueprint": blueprint_data,
                "status": "completed",
                "warnings": result.get("warnings", []),
            }

        finally:
            set_progress_callback(None)

    def _get_project_user_id(self, project_id: int) -> int:
        from backend.app.models import Project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        return project.user_id if project else 0

    def regenerate_stage(
        self, project_id: int, stage: str, feedback: str = ""
    ) -> Dict[str, Any]:
        """Regenerate or improve an individual agent's output without restarting the whole workflow."""
        user_id = self._get_project_user_id(project_id)
        project = self.project_service.get_project(project_id, user_id)
        if not project:
            raise ValueError("Project not found.")

        from backend.app.graph.nodes import (
            node_requirement_analyst, node_technology_advisor, node_architecture,
            node_task_planner, node_timeline, node_critic, node_generate_blueprint,
        )

        raw_idea = project.raw_idea
        if feedback:
            raw_idea += f"\nUser Feedback / Refinement: {feedback}"

        if stage == "requirements":
            state = {"raw_idea": raw_idea, "project_id": project_id}
            res = node_requirement_analyst(state)
            reqs = res.get("requirements") or self.project_service.get_requirements(project_id) or {
                "project_name": project.name,
                "goals": ["Build application"],
                "features": ["User Auth", "Dashboard"],
                "complexity": "medium",
                "team_size": 1,
                "deadline_days": 30,
            }
            self.project_service.save_requirements(project_id, reqs)
            return {"stage": stage, "data": reqs}

        elif stage == "technology":
            reqs = self.project_service.get_requirements(project_id)
            state = {"requirements": reqs, "project_id": project_id}
            res = node_technology_advisor(state)
            tech = res.get("technology_options") or {}
            if tech.get("categories"):
                self.project_service.save_technology_options(project_id, tech["categories"])
            return {"stage": stage, "data": tech}

        elif stage == "architecture":
            reqs = self.project_service.get_requirements(project_id)
            selected = self.project_service.get_selected_technologies(project_id)
            state = {"requirements": reqs, "selected_technologies": selected, "project_id": project_id}
            res = node_architecture(state)
            arch = res.get("architecture") or {}
            if arch:
                self.project_service.save_architecture(project_id, arch)
            return {"stage": stage, "data": arch}

        elif stage == "tasks":
            reqs = self.project_service.get_requirements(project_id)
            selected = self.project_service.get_selected_technologies(project_id)
            arch = self.project_service.get_architecture(project_id)
            state = {"requirements": reqs, "selected_technologies": selected, "architecture": arch, "project_id": project_id}
            res = node_task_planner(state)
            tp = res.get("task_plan") or {}
            if tp.get("tasks"):
                self.project_service.save_tasks(project_id, tp["tasks"])
            return {"stage": stage, "data": tp}

        elif stage == "timeline":
            reqs = self.project_service.get_requirements(project_id)
            selected = self.project_service.get_selected_technologies(project_id)
            arch = self.project_service.get_architecture(project_id)
            tp = self.project_service.get_tasks(project_id)
            state = {"requirements": reqs, "selected_technologies": selected, "architecture": arch, "task_plan": tp, "project_id": project_id}
            res = node_timeline(state)
            tl = res.get("timeline") or {}
            if tl:
                self.project_service.save_timeline(project_id, tl)
            return {"stage": stage, "data": tl}

        elif stage == "risks":
            reqs = self.project_service.get_requirements(project_id)
            selected = self.project_service.get_selected_technologies(project_id)
            arch = self.project_service.get_architecture(project_id)
            tp = self.project_service.get_tasks(project_id)
            tl = self.project_service.get_timeline(project_id)
            state = {"requirements": reqs, "selected_technologies": selected, "architecture": arch, "task_plan": tp, "timeline": tl, "project_id": project_id}
            res = node_critic(state)
            crit = res.get("critique") or {}
            if crit.get("risks"):
                self.project_service.save_risks(project_id, crit["risks"])
            return {"stage": stage, "data": crit}

        elif stage == "blueprint":
            reqs = self.project_service.get_requirements(project_id)
            selected = self.project_service.get_selected_technologies(project_id)
            arch = self.project_service.get_architecture(project_id)
            tp = self.project_service.get_tasks(project_id)
            tl = self.project_service.get_timeline(project_id)
            crit = {"decision": "approved", "issues": [], "corrections": []}
            state = {"requirements": reqs, "selected_technologies": selected, "architecture": arch, "task_plan": tp, "timeline": tl, "critique": crit, "project_id": project_id}
            res = node_generate_blueprint(state)
            bp = res.get("blueprint") or {}
            if bp:
                self.project_service.save_blueprint(project_id, bp, "92")
            return {"stage": stage, "data": bp}

        else:
            raise ValueError(f"Invalid stage '{stage}' for regeneration.")

