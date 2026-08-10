"""ProjectForge AI — Project & Related Models.

All project-related entities: Requirements, TechnologyOption, SelectedTechnology,
Architecture, Task, TimelineEntry, Milestone, TeamMember, Risk, Critique, Blueprint.
"""
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


# ---------------------------------------------------------------------------
# Helpers for JSON storage in SQLite
# ---------------------------------------------------------------------------
class JSONEncodedText(Text):
    """Store Python objects as JSON text — works with SQLite and PostgreSQL."""
    pass


def _json_default() -> str:
    return "[]"


def _json_dict_default() -> str:
    return "{}"


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
class Project(Base):
    """Top-level project entity."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False, default="Untitled Project")
    description = Column(Text, default="")
    raw_idea = Column(Text, default="")
    status = Column(
        String(50),
        default="created",
        # created → requirements_done → tech_analysis_done →
        # tech_selected → architecture_done → tasks_done →
        # timeline_done → review_done → completed
    )
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="projects")
    requirements = relationship(
        "Requirements", back_populates="project", uselist=False,
        cascade="all, delete-orphan",
    )
    technology_options = relationship(
        "TechnologyOption", back_populates="project", cascade="all, delete-orphan",
    )
    selected_technologies = relationship(
        "SelectedTechnology", back_populates="project", cascade="all, delete-orphan",
    )
    architecture = relationship(
        "Architecture", back_populates="project", uselist=False,
        cascade="all, delete-orphan",
    )
    tasks = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan",
    )
    timeline_entries = relationship(
        "TimelineEntry", back_populates="project", cascade="all, delete-orphan",
    )
    milestones = relationship(
        "Milestone", back_populates="project", cascade="all, delete-orphan",
    )
    team_members = relationship(
        "TeamMember", back_populates="project", cascade="all, delete-orphan",
    )
    risks = relationship(
        "Risk", back_populates="project", cascade="all, delete-orphan",
    )
    critiques = relationship(
        "Critique", back_populates="project", cascade="all, delete-orphan",
    )
    blueprint = relationship(
        "Blueprint", back_populates="project", uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


# ---------------------------------------------------------------------------
# Requirements
# ---------------------------------------------------------------------------
class Requirements(Base):
    """Structured requirements extracted by the Requirement Analyst."""

    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    goals = Column(Text, default=_json_default)          # JSON list
    features = Column(Text, default=_json_default)       # JSON list
    team_size = Column(Integer, default=1)
    deadline_days = Column(Integer, default=30)
    budget = Column(Float, nullable=True)
    skill_level = Column(String(50), default="intermediate")  # beginner/intermediate/advanced
    preferred_technologies = Column(Text, default=_json_default)  # JSON list
    constraints = Column(Text, default=_json_default)    # JSON list
    complexity = Column(String(50), default="medium")    # low/medium/high
    raw_data = Column(Text, default=_json_dict_default)  # JSON dict — full LLM output

    project = relationship("Project", back_populates="requirements")

    # ---- JSON property helpers ----
    def get_goals(self) -> list:
        return json.loads(self.goals) if self.goals else []

    def set_goals(self, value: list) -> None:
        self.goals = json.dumps(value)

    def get_features(self) -> list:
        return json.loads(self.features) if self.features else []

    def set_features(self, value: list) -> None:
        self.features = json.dumps(value)

    def get_constraints(self) -> list:
        return json.loads(self.constraints) if self.constraints else []

    def set_constraints(self, value: list) -> None:
        self.constraints = json.dumps(value)

    def get_preferred_technologies(self) -> list:
        return json.loads(self.preferred_technologies) if self.preferred_technologies else []

    def set_preferred_technologies(self, value: list) -> None:
        self.preferred_technologies = json.dumps(value)

    def get_raw_data(self) -> dict:
        return json.loads(self.raw_data) if self.raw_data else {}

    def set_raw_data(self, value: dict) -> None:
        self.raw_data = json.dumps(value)


# ---------------------------------------------------------------------------
# Technology Option (generated alternatives)
# ---------------------------------------------------------------------------
class TechnologyOption(Base):
    """A single technology alternative generated by the Technology Advisor."""

    __tablename__ = "technology_options"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String(100), nullable=False)  # frontend, backend, database, ...
    name = Column(String(150), nullable=False)
    suitability_score = Column(Integer, default=0)  # 0-100
    advantages = Column(Text, default=_json_default)  # JSON list
    disadvantages = Column(Text, default=_json_default)  # JSON list
    difficulty = Column(String(50), default="medium")  # easy/medium/hard
    fit_reason = Column(Text, default="")
    not_fit_reason = Column(Text, default="")
    is_recommended = Column(Boolean, default=False)

    project = relationship("Project", back_populates="technology_options")

    def get_advantages(self) -> list:
        return json.loads(self.advantages) if self.advantages else []

    def get_disadvantages(self) -> list:
        return json.loads(self.disadvantages) if self.disadvantages else []


# ---------------------------------------------------------------------------
# Selected Technology (LOCKED)
# ---------------------------------------------------------------------------
class SelectedTechnology(Base):
    """A user-selected and LOCKED technology choice."""

    __tablename__ = "selected_technologies"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String(100), nullable=False)
    name = Column(String(150), nullable=False)
    is_locked = Column(Boolean, default=True)
    selected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="selected_technologies")


# ---------------------------------------------------------------------------
# Architecture
# ---------------------------------------------------------------------------
class Architecture(Base):
    """Project architecture generated using LOCKED technologies."""

    __tablename__ = "architectures"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    system_architecture = Column(Text, default=_json_dict_default)
    component_architecture = Column(Text, default=_json_dict_default)
    api_architecture = Column(Text, default=_json_dict_default)
    database_architecture = Column(Text, default=_json_dict_default)
    auth_flow = Column(Text, default=_json_dict_default)
    data_flow = Column(Text, default=_json_dict_default)
    deployment_architecture = Column(Text, default=_json_dict_default)
    diagrams = Column(Text, default=_json_dict_default)

    project = relationship("Project", back_populates="architecture")

    def _get_json(self, field: str) -> dict:
        val = getattr(self, field)
        return json.loads(val) if val else {}

    def _set_json(self, field: str, value: Any) -> None:
        setattr(self, field, json.dumps(value))


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class Task(Base):
    """A development task generated by the Task Planner."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(String(50), nullable=False)  # e.g., "T1", "T2"
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    phase = Column(Integer, default=1)
    priority = Column(String(50), default="medium")  # critical/high/medium/low
    estimated_hours = Column(Float, default=0)
    complexity = Column(Integer, default=1)  # 1-5
    dependencies = Column(Text, default=_json_default)  # JSON list of task_ids
    assigned_role = Column(String(150), default="")
    status = Column(String(50), default="backlog")  # backlog/todo/in_progress/completed

    project = relationship("Project", back_populates="tasks")

    def get_dependencies(self) -> list:
        return json.loads(self.dependencies) if self.dependencies else []


# ---------------------------------------------------------------------------
# Timeline Entry
# ---------------------------------------------------------------------------
class TimelineEntry(Base):
    """A scheduled task in the project timeline."""

    __tablename__ = "timeline_entries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(String(50), nullable=False)
    start_day = Column(Integer, nullable=False)
    end_day = Column(Integer, nullable=False)
    assigned_member = Column(String(150), default="")
    is_critical = Column(Boolean, default=False)

    project = relationship("Project", back_populates="timeline_entries")


# ---------------------------------------------------------------------------
# Milestone
# ---------------------------------------------------------------------------
class Milestone(Base):
    """A project milestone."""

    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    target_day = Column(Integer, nullable=False)
    associated_tasks = Column(Text, default=_json_default)  # JSON list of task_ids

    project = relationship("Project", back_populates="milestones")


# ---------------------------------------------------------------------------
# Team Member
# ---------------------------------------------------------------------------
class TeamMember(Base):
    """A team member allocated to the project."""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(150), nullable=False)
    name = Column(String(150), default="")
    assigned_tasks = Column(Text, default=_json_default)  # JSON list of task_ids

    project = relationship("Project", back_populates="team_members")


# ---------------------------------------------------------------------------
# Risk
# ---------------------------------------------------------------------------
class Risk(Base):
    """A project risk identified by the Critic & Risk Agent."""

    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String(100), nullable=False)  # technical/schedule/resource/budget/dependency
    severity = Column(String(50), default="medium")  # low/medium/high/critical
    probability = Column(String(50), default="medium")
    impact = Column(String(50), default="medium")
    explanation = Column(Text, default="")
    mitigation = Column(Text, default="")

    project = relationship("Project", back_populates="risks")


# ---------------------------------------------------------------------------
# Critique
# ---------------------------------------------------------------------------
class Critique(Base):
    """A critique/review from the Critic & Risk Agent."""

    __tablename__ = "critiques"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    revision_number = Column(Integer, default=1)
    decision = Column(String(50), default="needs_revision")  # approved / needs_revision
    issues = Column(Text, default=_json_default)       # JSON list
    corrections = Column(Text, default=_json_default)  # JSON list
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="critiques")


# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------
class Blueprint(Base):
    """The final project blueprint / report."""

    __tablename__ = "blueprints"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    content = Column(Text, default=_json_dict_default)  # JSON dict — full blueprint
    feasibility_score = Column(String(50), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="blueprint")
