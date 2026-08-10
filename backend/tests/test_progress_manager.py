"""ProjectForge AI — Tests for SSE Progress Manager Fan-out & Replay."""
import json
import pytest
import asyncio
from backend.app.services.progress_manager import (
    send_progress, progress_stream, cleanup_queue
)


@pytest.mark.asyncio
async def test_progress_manager_fan_out_multiple_subscribers():
    """Verify that multiple concurrent SSE subscribers receive 100% of events without event theft."""
    project_id = 9999
    cleanup_queue(project_id)

    # Start 2 progress streams
    gen1 = progress_stream(project_id)
    gen2 = progress_stream(project_id)

    # Await connection to register both subscribers before emitting events
    conn1 = await gen1.__anext__()
    conn2 = await gen2.__anext__()
    assert "connected" in conn1
    assert "connected" in conn2

    # Send progress events sequentially
    send_progress(project_id, "architecture", "running")
    send_progress(project_id, "architecture", "completed")
    send_progress(project_id, "blueprint", "completed")

    # Subscriber 1 should see all 3 events
    e1_sub1 = json.loads((await gen1.__anext__())[6:])
    e2_sub1 = json.loads((await gen1.__anext__())[6:])
    e3_sub1 = json.loads((await gen1.__anext__())[6:])

    assert e1_sub1 == {"agent": "architecture", "status": "running"}
    assert e2_sub1 == {"agent": "architecture", "status": "completed"}
    assert e3_sub1 == {"agent": "blueprint", "status": "completed"}

    # Subscriber 2 MUST ALSO see all 3 events (no event theft!)
    e1_sub2 = json.loads((await gen2.__anext__())[6:])
    e2_sub2 = json.loads((await gen2.__anext__())[6:])
    e3_sub2 = json.loads((await gen2.__anext__())[6:])

    assert e1_sub2 == {"agent": "architecture", "status": "running"}
    assert e2_sub2 == {"agent": "architecture", "status": "completed"}
    assert e3_sub2 == {"agent": "blueprint", "status": "completed"}

    cleanup_queue(project_id)


@pytest.mark.asyncio
async def test_progress_manager_late_subscriber_replay():
    """Verify that a late-connecting subscriber receives an instant replay of current agent statuses."""
    project_id = 8888
    cleanup_queue(project_id)

    # Progress events emitted before stream connects
    send_progress(project_id, "requirement_analyst", "completed")
    send_progress(project_id, "technology_advisor", "completed")
    send_progress(project_id, "user_selection", "completed")
    send_progress(project_id, "blueprint", "completed")

    # Now subscriber connects late
    gen = progress_stream(project_id)
    conn = await gen.__anext__()
    assert "connected" in conn

    # Collect replayed events
    replayed = []
    for _ in range(4):
        msg = await gen.__anext__()
        replayed.append(json.loads(msg[6:]))

    agents_replayed = {item["agent"]: item["status"] for item in replayed}
    assert agents_replayed["requirement_analyst"] == "completed"
    assert agents_replayed["technology_advisor"] == "completed"
    assert agents_replayed["user_selection"] == "completed"
    assert agents_replayed["blueprint"] == "completed"

    cleanup_queue(project_id)
