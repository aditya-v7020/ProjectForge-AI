"""ProjectForge AI — Project API & Technology Selection Tests."""

def test_project_crud_endpoints(client, auth_headers):
    """Test project creation, listing, getting, deleting via REST API."""
    # Create
    create_res = client.post("/api/projects", json={
        "name": "E-Commerce App",
        "description": "Online store",
        "raw_idea": "Build store for 3 people in 30 days"
    }, headers=auth_headers)
    assert create_res.status_code == 201
    proj_id = create_res.json()["id"]

    # List
    list_res = client.get("/api/projects", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Get
    get_res = client.get(f"/api/projects/{proj_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "E-Commerce App"

    # Delete
    del_res = client.delete(f"/api/projects/{proj_id}", headers=auth_headers)
    assert del_res.status_code == 204


def test_technology_selection_locking(client, auth_headers):
    """Test technology selection endpoint locks user choices."""
    # Seed demo technology options
    seed_res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    proj_id = seed_res.json()["project_id"]

    # Submit technology selections for all categories
    selections = {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "ai_ml": "OpenAI API",
        "deployment": "Docker + AWS",
        "authentication": "JWT",
    }
    sel_res = client.post(f"/api/projects/{proj_id}/technology-selection", json={
        "selections": selections
    }, headers=auth_headers)

    assert sel_res.status_code == 200
    assert sel_res.json()["locked"] is True

    # Verify locked selections in project details
    detail_res = client.get(f"/api/projects/{proj_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    locked_list = detail_res.json()["selected_technologies"]
    locked_dict = {item["category"]: item["name"] for item in locked_list}
    assert locked_dict["frontend"] == "React"
    assert locked_dict["backend"] == "FastAPI"
    assert locked_dict["database"] == "PostgreSQL"


def test_demo_seed_endpoint(client, auth_headers):
    """Test seeding demo data for testing without API keys."""
    res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert res.status_code == 200
    assert "project_id" in res.json()


def test_get_requirements_endpoint(client, auth_headers):
    """Test GET /api/projects/{id}/requirements returns stored requirements."""
    # Create a project
    create_res = client.post("/api/projects", json={
        "name": "Reqs Test",
        "description": "",
        "raw_idea": "Build a chat app",
    }, headers=auth_headers)
    assert create_res.status_code == 201
    proj_id = create_res.json()["id"]

    # Before any requirements: expect 404
    get_res = client.get(f"/api/projects/{proj_id}/requirements", headers=auth_headers)
    assert get_res.status_code == 404

    # Seed demo to get requirements
    seed_res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    demo_id = seed_res.json()["project_id"]

    # Now the demo project should have requirements
    get_res2 = client.get(f"/api/projects/{demo_id}/requirements", headers=auth_headers)
    assert get_res2.status_code == 200
    data = get_res2.json()
    assert "goals" in data
    assert "features" in data


def test_project_chat_endpoint(client, auth_headers):
    """Test POST /api/projects/{id}/chat endpoint."""
    seed_res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    demo_id = seed_res.json()["project_id"]

    chat_res = client.post(f"/api/projects/{demo_id}/chat", json={
        "message": "Summarize the tech stack"
    }, headers=auth_headers)
    assert chat_res.status_code == 200
    assert "reply" in chat_res.json()


def test_project_health_score_endpoint(client, auth_headers):
    """Test GET /api/projects/{id}/health-score endpoint."""
    seed_res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    demo_id = seed_res.json()["project_id"]

    hs_res = client.get(f"/api/projects/{demo_id}/health-score", headers=auth_headers)
    assert hs_res.status_code == 200
    data = hs_res.json()
    assert "overall_score" in data
    assert "grade" in data
    assert "factors" in data


def test_regenerate_stage_endpoint(client, auth_headers):
    """Test POST /api/projects/{id}/regenerate/{stage} endpoint."""
    seed_res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    demo_id = seed_res.json()["project_id"]

    regen_res = client.post(f"/api/projects/{demo_id}/regenerate/requirements", json={
        "feedback": "Add mobile offline mode requirement"
    }, headers=auth_headers)
    assert regen_res.status_code == 200
    assert regen_res.json()["stage"] == "requirements"


def test_export_project_endpoint(client, auth_headers):
    """Test GET /api/projects/{id}/export/{format} endpoint."""
    seed_res = client.post("/api/projects/demo/seed", headers=auth_headers)
    assert seed_res.status_code == 200
    demo_id = seed_res.json()["project_id"]

    for fmt in ["json", "markdown", "pdf"]:
        res = client.get(f"/api/projects/{demo_id}/export/{fmt}", headers=auth_headers)
        assert res.status_code == 200
        assert "filename" in res.json()




