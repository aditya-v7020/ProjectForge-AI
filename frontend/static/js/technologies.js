/* ============================================
   ProjectForge AI — Technology Selection JS
   Handles card rendering, selection, & locking
   ============================================ */

let selectedTechnologies = {};
let availableOptions = [];

async function loadTechnologyOptions(projectId) {
    showLoading('tech-options-container', 'Analyzing technology alternatives...');
    try {
        const data = await apiRequest(`/api/projects/${projectId}/technology-options`);
        availableOptions = data.categories || [];

        // Check if selections already exist
        const projData = await apiRequest(`/api/projects/${projectId}`);
        const existingSelections = projData.selected_technologies || [];

        if (existingSelections.length > 0) {
            existingSelections.forEach(s => {
                selectedTechnologies[s.category] = s.name;
            });
        } else {
            // Auto-select recommendations as default initial state (user can still change)
            availableOptions.forEach(cat => {
                const rec = cat.alternatives.find(a => a.is_recommended);
                if (rec) {
                    selectedTechnologies[cat.category] = rec.name;
                } else if (cat.alternatives.length > 0) {
                    selectedTechnologies[cat.category] = cat.alternatives[0].name;
                }
            });
        }

        renderTechnologyOptions(projectId);
    } catch (err) {
        document.getElementById('tech-options-container').innerHTML = `
            <div class="alert alert-danger">
                Failed to load technology options: ${err.message}. 
                Make sure requirement analysis has been completed.
            </div>
        `;
    }
}

function renderTechnologyOptions(projectId) {
    const container = document.getElementById('tech-options-container');
    if (!container) return;

    if (availableOptions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚙️</div>
                <h3>No Technology Alternatives Found</h3>
                <p>Please run the requirement analysis step first.</p>
            </div>
        `;
        return;
    }

    let html = '';

    availableOptions.forEach(cat => {
        const categoryName = cat.category;
        const currentSelected = selectedTechnologies[categoryName];

        html += `
            <div class="tech-category">
                <h3 class="tech-category-title">${categoryName.replace('_', ' / ')}</h3>
                <div class="tech-cards">
        `;

        cat.alternatives.forEach(alt => {
            const isSelected = currentSelected === alt.name;
            const isRecommended = alt.is_recommended;

            html += `
                <div class="tech-card ${isSelected ? 'selected' : ''} ${isRecommended ? 'recommended' : ''}"
                     onclick="selectTechnology('${categoryName}', '${alt.name}', ${projectId})">
                    ${isRecommended ? '<span class="tech-recommended-badge">⭐ AI Choice</span>' : ''}
                    ${isSelected ? '<span class="tech-locked-badge">🔒 Selected</span>' : ''}

                    <div class="tech-card-header">
                        <span class="tech-name">${alt.name}</span>
                        <span class="tech-score">${alt.suitability_score}% Match</span>
                    </div>

                    <div class="tech-detail">
                        <span class="badge badge-info">${alt.difficulty || 'medium'}</span>
                    </div>

                    <div class="tech-detail" style="margin-top: 10px;">
                        <div class="tech-detail-label">Advantages</div>
                        <ul class="tech-pros">
                            ${(alt.advantages || []).slice(0, 3).map(adv => `<li>${adv}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="tech-detail" style="margin-top: 10px;">
                        <div class="tech-detail-label">Disadvantages</div>
                        <ul class="tech-cons">
                            ${(alt.disadvantages || []).slice(0, 2).map(con => `<li>${con}</li>`).join('')}
                        </ul>
                    </div>

                    ${alt.fit_reason ? `
                        <div class="tech-detail" style="margin-top: 10px; font-size: 0.8rem; color: var(--color-text-secondary);">
                            <strong>Why it fits:</strong> ${alt.fit_reason}
                        </div>
                    ` : ''}

                    <div class="tech-actions">
                        <button class="btn btn-sm ${isSelected ? 'btn-success' : 'btn-secondary'}" style="width: 100%;">
                            ${isSelected ? '🔒 Selected & Locked' : 'Select Technology'}
                        </button>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    // Add Stack Summary & Confirm Button
    html += renderStackSummary(projectId);

    container.innerHTML = html;
}

function selectTechnology(category, name, projectId) {
    selectedTechnologies[category] = name;
    renderTechnologyOptions(projectId);
}

function renderStackSummary(projectId) {
    const categories = Object.keys(selectedTechnologies);

    let itemsHtml = categories.map(cat => `
        <div class="stack-item">
            <span class="stack-item-category">${cat.replace('_', ' / ')}:</span>
            <span class="stack-item-value">${selectedTechnologies[cat]} <span class="lock-icon">🔒</span></span>
        </div>
    `).join('');

    return `
        <div class="selected-stack card margin-top-lg">
            <h3>🔒 Selected Technology Stack</h3>
            <p class="text-sm text-secondary" style="margin-bottom: 16px;">
                Confirming will LOCK these selections. Subsequent agents (Architecture, Task Planner, Timeline, Critic) 
                will generate the complete plan strictly using these chosen technologies.
            </p>
            <div class="stack-items" style="margin-bottom: 20px;">
                ${itemsHtml}
            </div>
            <div style="display: flex; justify-content: flex-end;">
                <button id="lock-btn" onclick="confirmAndLockSelections(${projectId})" class="btn btn-primary btn-lg">
                    🔒 LOCK Selections & Generate Architecture
                </button>
            </div>
        </div>
    `;
}

async function confirmAndLockSelections(projectId) {
    const btn = document.getElementById('lock-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Locking Selections...';
    }

    try {
        // Step 1: Submit selections to backend
        await apiRequest(`/api/projects/${projectId}/technology-selection`, {
            method: 'POST',
            body: { selections: selectedTechnologies }
        });

        showAlert('Technologies locked successfully! Starting Architecture & Planning phase...', 'success');

        // Step 2: Trigger Phase 2 plan generation
        if (btn) {
            btn.innerHTML = '<span class="spinner"></span> Running Agents (Architecture → Tasks → Timeline → Critic)...';
        }

        // Show SSE progress modal / section if available
        if (window.startProgressStream) {
            window.startProgressStream(projectId);
        }

        await apiRequest(`/api/projects/${projectId}/generate-plan`, {
            method: 'POST'
        });

        showAlert('Project blueprint generated successfully!', 'success');
        setTimeout(() => {
            window.location.href = `/projects/${projectId}/architecture/`;
        }, 1500);

    } catch (err) {
        showAlert(`Failed to generate plan: ${err.message}`, 'danger');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '🔒 LOCK Selections & Generate Architecture';
        }
    }
}
