/* ============================================
   ProjectForge AI — Real-Time SSE Agent Progress
   ============================================ */

window.startProgressStream = function(projectId, onComplete) {
    const container = document.getElementById('agent-progress-container');
    if (!container) return;

    const token = getToken();
    const sseUrl = `${API_BASE}/api/projects/${projectId}/progress`;

    const agents = [
        { key: 'requirement_analyst', name: '1. Requirement Analyst Agent' },
        { key: 'technology_advisor', name: '2. Technology Advisor Agent' },
        { key: 'user_selection', name: '3. User Technology Selection (Locked 🔒)' },
        { key: 'architecture', name: '4. Architecture Agent' },
        { key: 'task_planner', name: '5. Task Planner Agent' },
        { key: 'timeline', name: '6. Timeline & Resource Agent' },
        { key: 'critic', name: '7. Critic & Risk Agent' },
        { key: 'blueprint', name: '8. Final Blueprint Generation' }
    ];

    const agentState = {};
    agents.forEach(a => agentState[a.key] = 'pending');

    function renderProgress() {
        let html = '<div class="progress-steps">';
        agents.forEach(a => {
            const status = agentState[a.key];
            let icon = '○';
            let statusClass = 'step-pending';

            if (status === 'completed') {
                icon = '✓';
                statusClass = 'step-completed';
            } else if (status === 'running') {
                icon = '⟳';
                statusClass = 'step-running';
            } else if (status === 'failed') {
                icon = '✗';
                statusClass = 'step-failed';
            }

            html += `
                <div class="progress-step ${statusClass}">
                    <span class="step-icon">${icon}</span>
                    <span>${a.name}</span>
                    <span class="text-xs text-muted" style="margin-left: auto;">${status}</span>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    }

    renderProgress();

    try {
        const eventSource = new EventSource(`${sseUrl}`);

        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                if (data.agent && data.status) {
                    agentState[data.agent] = data.status;
                    renderProgress();

                    if (data.agent === 'blueprint' && data.status === 'completed') {
                        eventSource.close();
                        if (onComplete) onComplete();
                    }
                }
            } catch (err) {
                console.error("SSE Error parsing data:", err);
            }
        };

        eventSource.onerror = function() {
            eventSource.close();
        };
    } catch (err) {
        console.error("SSE Connection error:", err);
    }
};
