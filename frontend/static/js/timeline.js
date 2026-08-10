/* ============================================
   ProjectForge AI — Gantt Timeline JS
   ============================================ */

async function loadTimeline(projectId) {
    showLoading('timeline-container-wrapper', 'Rendering timeline...');
    try {
        const data = await apiRequest(`/api/projects/${projectId}/timeline`);
        renderGanttTimeline(data);
    } catch (err) {
        document.getElementById('timeline-container-wrapper').innerHTML = `
            <div class="alert alert-danger">Failed to load timeline: ${err.message}</div>
        `;
    }
}

function renderGanttTimeline(data) {
    const container = document.getElementById('timeline-container-wrapper');
    if (!container) return;

    const schedule = data.schedule || [];
    const milestones = data.milestones || [];
    const teamMembers = data.team_members || [];

    if (schedule.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <h3>No Timeline Data</h3>
                <p>Generate a project blueprint to view the timeline.</p>
            </div>
        `;
        return;
    }

    // Find max day for gantt width calculation
    let maxDay = 30;
    schedule.forEach(s => {
        if (s.end_day > maxDay) maxDay = s.end_day;
    });

    let html = `
        <div class="timeline-container">
            <div class="gantt-chart">
                <div class="gantt-header">
                    <div class="gantt-label-col">Task ID & Assigned Role</div>
                    <div class="gantt-bars-col">
    `;

    for (let d = 1; d <= maxDay; d++) {
        html += `<div class="gantt-day-marker">D${d}</div>`;
    }

    html += `
                    </div>
                </div>
    `;

    schedule.forEach(item => {
        const startPct = ((item.start_day - 1) / maxDay) * 100;
        const widthPct = Math.max(((item.end_day - item.start_day + 1) / maxDay) * 100, 3);
        const isCritical = item.is_critical;

        html += `
            <div class="gantt-row">
                <div class="gantt-task-label">
                    <strong>${item.task_id}</strong> (${item.assigned_member || 'Unassigned'})
                </div>
                <div class="gantt-task-bar-container">
                    <div class="gantt-task-bar ${isCritical ? 'critical' : ''}" 
                         style="left: ${startPct}%; width: ${widthPct}%;"
                         title="${item.task_id}: Day ${item.start_day} to ${item.end_day} (${item.assigned_member})">
                        ${item.task_id}
                    </div>
                </div>
            </div>
        `;
    });

    html += `
            </div>
        </div>
    `;

    // Render Milestones Section
    if (milestones.length > 0) {
        html += `
            <div class="card margin-top-lg" style="margin-top: 24px;">
                <h3>🚩 Project Milestones</h3>
                <div class="grid grid-3" style="margin-top: 16px;">
        `;
        milestones.forEach(m => {
            html += `
                <div class="card" style="padding: 16px; background: var(--color-bg);">
                    <div style="font-weight: 700; color: var(--color-warning);">Day ${m.target_day}</div>
                    <div style="font-weight: 600; margin-top: 4px;">${m.name}</div>
                    <div class="text-xs text-muted" style="margin-top: 4px;">Tasks: ${(m.associated_tasks || []).join(', ')}</div>
                </div>
            `;
        });
        html += `</div></div>`;
    }

    // Render Team Members Section
    if (teamMembers.length > 0) {
        html += `
            <div class="card margin-top-lg" style="margin-top: 24px;">
                <h3>👥 Team Member Allocations</h3>
                <div class="grid grid-3" style="margin-top: 16px;">
        `;
        teamMembers.forEach(tm => {
            html += `
                <div class="card" style="padding: 16px;">
                    <div class="badge badge-primary">${tm.role}</div>
                    <div style="font-weight: 700; font-size: 1.1rem; margin-top: 8px;">${tm.name || tm.role}</div>
                    <div class="text-sm text-secondary" style="margin-top: 6px;">
                        Assigned ${tm.assigned_tasks ? tm.assigned_tasks.length : 0} tasks
                    </div>
                </div>
            `;
        });
        html += `</div></div>`;
    }

    container.innerHTML = html;
}
