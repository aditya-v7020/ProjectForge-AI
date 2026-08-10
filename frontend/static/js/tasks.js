/* ============================================
   ProjectForge AI — Kanban Task Board JS
   ============================================ */

async function loadKanbanBoard(projectId) {
    showLoading('kanban-board-container', 'Loading tasks...');
    try {
        const data = await apiRequest(`/api/projects/${projectId}/tasks`);
        renderKanbanBoard(data.tasks || []);
    } catch (err) {
        document.getElementById('kanban-board-container').innerHTML = `
            <div class="alert alert-danger">Failed to load tasks: ${err.message}</div>
        `;
    }
}

function renderKanbanBoard(tasks) {
    const container = document.getElementById('kanban-board-container');
    if (!container) return;

    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <h3>No Tasks Found</h3>
                <p>Complete technology selection and generate plan to create tasks.</p>
            </div>
        `;
        return;
    }

    const columns = {
        'backlog': { title: 'Backlog', tasks: [] },
        'todo': { title: 'To Do', tasks: [] },
        'in_progress': { title: 'In Progress', tasks: [] },
        'completed': { title: 'Completed', tasks: [] },
    };

    tasks.forEach(task => {
        const col = columns[task.status] ? task.status : 'backlog';
        columns[col].tasks.push(task);
    });

    let html = '<div class="kanban-board">';

    Object.keys(columns).forEach(colKey => {
        const col = columns[colKey];
        html += `
            <div class="kanban-column">
                <div class="kanban-column-header">
                    <span class="kanban-column-title">${col.title}</span>
                    <span class="kanban-count">${col.tasks.length}</span>
                </div>
                <div class="kanban-cards-list">
        `;

        col.tasks.forEach(t => {
            const priorityClass = t.priority === 'critical' ? 'badge-danger' : 
                                 t.priority === 'high' ? 'badge-warning' : 
                                 t.priority === 'medium' ? 'badge-primary' : 'badge-info';

            html += `
                <div class="kanban-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span class="badge ${priorityClass}">${t.priority}</span>
                        <span class="text-xs text-muted">Phase ${t.phase}</span>
                    </div>
                    <div class="kanban-card-title">${t.task_id}: ${t.title}</div>
                    <p class="text-xs text-secondary" style="margin-bottom:8px;">${t.description.substring(0, 90)}...</p>
                    <div class="kanban-card-meta">
                        <span class="badge badge-info">${t.estimated_hours}h</span>
                        ${t.assigned_role ? `<span class="badge badge-primary">${t.assigned_role}</span>` : ''}
                    </div>
                    ${t.dependencies && t.dependencies.length > 0 ? `
                        <div class="text-xs text-muted" style="margin-top:6px;">
                            <strong>Deps:</strong> ${t.dependencies.join(', ')}
                        </div>
                    ` : ''}
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}
