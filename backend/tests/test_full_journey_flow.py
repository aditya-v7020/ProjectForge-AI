"""ProjectForge AI — End-to-End Journey & Persistence Test.

Verifies complete flow:
Create Project → Seed/Phase 1 → Lock Technologies → Generate Plan (Phase 2) →
Verify Architecture, Tasks, Timeline, Risks, and Blueprint endpoints load generated data.
"""
import pytest
from unittest.mock import patch


@patch("backend.app.services.agent_service.run_phase2")
def test_full_project_journey_flow_and_data_persistence(mock_run_phase2, client, auth_headers):
    """Test full journey from project creation to final blueprint delivery."""
    # Mock Phase 2 output
    mock_run_phase2.return_value = {
        "architecture": {
            "system_overview": "Mocked Microservice Architecture",
            "components": [{"name": "Frontend React SPA", "description": "Client app"}],
            "frontend_architecture": {"framework": "React"},
            "backend_architecture": {"framework": "FastAPI"},
            "database_design": {"engine": "PostgreSQL"},
            "api_design": {"protocol": "REST"},
            "auth_flow": {"scheme": "JWT"},
            "data_flow": {"pipeline": "Async"},
            "deployment_plan": {"platform": "Docker"},
            "diagrams": [{"title": "Overview", "definition": "graph TD\n User-->API"}]
        },
        "task_plan": {
            "phases": [{"name": "Phase 1: Setup"}],
            "tasks": [
                {
                    "task_id": "T1",
                    "title": "Setup React Project",
                    "description": "Initialize SPA",
                    "phase": 1,
                    "priority": "high",
                    "estimated_hours": 4.0,
                    "complexity": 2,
                    "dependencies": [],
                    "assigned_role": "Frontend Dev"
                }
            ],
            "milestones": [{"name": "Foundation Ready", "target_day": 7, "associated_tasks": ["T1"]}]
        },
        "timeline": {
            "schedule": [
                {"task_id": "T1", "start_day": 1, "end_day": 4, "assigned_member": "Dev 1", "is_critical": True}
            ],
            "team_allocation": [{"role": "Frontend Dev", "name": "Dev 1", "assigned_tasks": ["T1"]}],
            "milestones": [{"name": "Foundation Ready", "target_day": 7, "associated_tasks": ["T1"]}],
            "feasibility": "feasible",
            "feasibility_score": 90,
            "feasibility_notes": "Well planned"
        },
        "critique": {
            "decision": "approved",
            "issues": [],
            "corrections": [],
            "risks": [
                {
                    "category": "technical",
                    "severity": "high",
                    "probability": "medium",
                    "impact": "high",
                    "explanation": "API rate limits",
                    "mitigation": "Implement exponential backoff"
                }
            ],
            "overall_assessment": "Solid plan",
            "feasibility_score": 90
        },
        "blueprint": {
            "project_overview": {"name": "E2E E-Commerce App", "description": "Desc"},
            "requirements": {"goals": ["Goal 1"]},
            "selected_technology_stack": {"frontend": "React", "backend": "FastAPI"},
            "system_architecture": {"overview": "Mocked Microservice Architecture"},
            "development_tasks": [{"title": "Setup React Project"}],
            "timeline": [{"task_id": "T1", "start_day": 1, "end_day": 4}],
            "risk_analysis": [{"category": "technical", "severity": "high", "mitigation": "Backoff"}]
        },
        "status": "completed",
        "warnings": []
    }

    # 1. Create Project
    create_res = client.post("/api/projects", json={
        "name": "E2E E-Commerce App",
        "description": "Full end to end test project",
        "raw_idea": "Build an AI powered online shopping store",
    }, headers=auth_headers)
    assert create_res.status_code == 201
    proj_id = create_res.json()["id"]

    # 2. Seed Demo Data (populates Phase 1 requirements & technology options)
    seed_res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    demo_id = seed_res.json()["project_id"]

    # Verify Requirements exist
    req_res = client.get(f"/api/projects/{demo_id}/requirements", headers=auth_headers)
    assert req_res.status_code == 200
    assert "features" in req_res.json()

    # 3. Submit Technology Selection & LOCK
    selections = {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "ai_ml": "Scikit-learn",
        "deployment": "Render",
        "authentication": "JWT",
    }
    lock_res = client.post(
        f"/api/projects/{demo_id}/technology-selection",
        json={"selections": selections},
        headers=auth_headers,
    )
    assert lock_res.status_code == 200
    assert lock_res.json()["locked"] is True

    # 4. Generate Plan (Phase 2 execution: Architecture → Tasks → Timeline → Critic → Blueprint)
    plan_res = client.post(f"/api/projects/{demo_id}/generate-plan", headers=auth_headers)
    assert plan_res.status_code == 200

    # 5. Verify Architecture Endpoint
    arch_res = client.get(f"/api/projects/{demo_id}/architecture", headers=auth_headers)
    assert arch_res.status_code == 200
    arch_data = arch_res.json()
    assert "system_architecture" in arch_data
    assert arch_data["system_architecture"]["overview"] == "Mocked Microservice Architecture"

    # 6. Verify Tasks Endpoint
    tasks_res = client.get(f"/api/projects/{demo_id}/tasks", headers=auth_headers)
    assert tasks_res.status_code == 200
    tasks_data = tasks_res.json()
    assert "tasks" in tasks_data
    assert len(tasks_data["tasks"]) == 1
    assert tasks_data["tasks"][0]["title"] == "Setup React Project"

    # 7. Verify Timeline Endpoint
    timeline_res = client.get(f"/api/projects/{demo_id}/timeline", headers=auth_headers)
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert "schedule" in timeline_data

    # 8. Verify Risks Endpoint
    risks_res = client.get(f"/api/projects/{demo_id}/risks", headers=auth_headers)
    assert risks_res.status_code == 200
    risks_data = risks_res.json()
    assert "risks" in risks_data
    assert len(risks_data["risks"]) == 1
    assert risks_data["risks"][0]["category"] == "technical"

    # 9. Verify Blueprint Endpoint
    bp_res = client.get(f"/api/projects/{demo_id}/blueprint", headers=auth_headers)
    assert bp_res.status_code == 200
    bp_data = bp_res.json()
    assert "content" in bp_data
    content = bp_data["content"]
    assert content["system_architecture"]["overview"] == "Mocked Microservice Architecture"
