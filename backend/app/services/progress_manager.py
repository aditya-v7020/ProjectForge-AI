"""ProjectForge AI — SSE Progress Manager.

In-memory fan-out progress tracking for real-time agent status updates.
Supports multiple concurrent SSE client subscribers per project with instant status replay.
"""
import asyncio
import json
import logging
from typing import Dict, AsyncGenerator, Set

logger = logging.getLogger(__name__)

# Active subscriber queues per project: project_id -> Set[asyncio.Queue]
_subscribers: Dict[int, Set[asyncio.Queue]] = {}

# Latest status for each agent per project: project_id -> Dict[agent_name, status]
_agent_states: Dict[int, Dict[str, str]] = {}


def send_progress(project_id: int, agent: str, status: str, extra: dict = None) -> None:
    """Send a progress update to all active SSE subscribers for project_id.

    Called synchronously from agent nodes or service layer.
    """
    if project_id not in _agent_states:
        _agent_states[project_id] = {}
    _agent_states[project_id][agent] = status

    event = {"agent": agent, "status": status}
    if extra:
        event.update(extra)

    payload = json.dumps(event)

    queues = _subscribers.get(project_id, set())
    for queue in list(queues):
        try:
            queue.put_nowait(payload)
        except Exception as e:
            logger.warning(f"Progress queue put_nowait failed for project {project_id}: {e}")


async def progress_stream(project_id: int) -> AsyncGenerator[str, None]:
    """Async generator yielding SSE events for a project with multi-subscriber fan-out."""
    client_queue: asyncio.Queue = asyncio.Queue()

    # Add subscriber queue FIRST so all live events are captured from this instant
    if project_id not in _subscribers:
        _subscribers[project_id] = set()
    _subscribers[project_id].add(client_queue)

    # Take snapshot of past states BEFORE connection
    current_states = dict(_agent_states.get(project_id, {}))

    # Initial connection message
    yield f"data: {json.dumps({'agent': 'system', 'status': 'connected'})}\n\n"

    # Replay past states
    has_completed = False
    for agent_name, agent_status in current_states.items():
        replay_payload = json.dumps({"agent": agent_name, "status": agent_status})
        yield f"data: {replay_payload}\n\n"
        if agent_status in ("completed", "failed") and agent_name in ("blueprint", "system"):
            has_completed = True

    if has_completed:
        return

    try:
        while True:
            try:
                event = await asyncio.wait_for(client_queue.get(), timeout=30.0)
                yield f"data: {event}\n\n"

                event_data = json.loads(event)
                if event_data.get("status") in ("completed", "failed") and \
                   event_data.get("agent") in ("blueprint", "system"):
                    break

            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'agent': 'system', 'status': 'keepalive'})}\n\n"
            except (asyncio.CancelledError, GeneratorExit):
                break

    finally:
        if project_id in _subscribers:
            _subscribers[project_id].discard(client_queue)
            if not _subscribers[project_id]:
                _subscribers.pop(project_id, None)


def cleanup_queue(project_id: int) -> None:
    """Remove subscriber queues and state for a project."""
    _subscribers.pop(project_id, None)
    _agent_states.pop(project_id, None)

