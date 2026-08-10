import { useState, useEffect } from 'react';

const getBackendUrl = () => {
  let url = import.meta.env.VITE_BACKEND_URL;
  if (!url || (import.meta.env.PROD && (url.includes('localhost') || url.includes('127.0.0.1')))) {
    url = 'https://projectforge-ai-1.onrender.com';
  }
  return url.replace(/\/+$/, '');
};

const API_BASE = getBackendUrl();

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
    const path = token
      ? `/api/projects/${projectId}/progress?token=${encodeURIComponent(token)}`
      : `/api/projects/${projectId}/progress`;
    const sseUrl = `${API_BASE}${path}`;

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
