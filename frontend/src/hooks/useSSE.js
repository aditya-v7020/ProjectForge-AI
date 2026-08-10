import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_BACKEND_URL || '';

export function useSSE(projectId) {
  const [agentProgress, setAgentProgress] = useState({
    requirement_analyst: 'pending',
    technology_advisor: 'pending',
    user_selection: 'pending',
    architecture: 'pending',
    task_planner: 'pending',
    timeline: 'pending',
    critic: 'pending',
    blueprint: 'pending',
  });
  const [isConnected, setIsConnected] = useState(false);
  const [isFinished, setIsFinished] = useState(false);

  useEffect(() => {
    if (!projectId) return;

    const token = localStorage.getItem('access_token');
    // Use relative path so the Vite proxy forwards to the backend,
    // avoiding CORS issues (EventSource cannot send custom headers).
    const sseUrl = token
      ? `/api/projects/${projectId}/progress?token=${encodeURIComponent(token)}`
      : `/api/projects/${projectId}/progress`;

    const eventSource = new EventSource(sseUrl);

    eventSource.onopen = () => {
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.agent && data.status) {
          setAgentProgress((prev) => ({
            ...prev,
            [data.agent]: data.status,
          }));

          if (
            (data.agent === 'technology_advisor' || data.agent === 'blueprint' || data.agent === 'critic') &&
            (data.status === 'completed' || data.status === 'done')
          ) {
            setIsFinished(true);
          }
        }
      } catch (e) {
        console.error("SSE parse error:", e);
      }
    };

    eventSource.onerror = (err) => {
      console.warn("SSE connection closed or errored:", err);
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [projectId]);

  return { agentProgress, isConnected, isFinished };
}
