/* ============================================
   ProjectForge AI — Main JavaScript Utilities
   API client, JWT token storage, & common helpers
   ============================================ */

const getBackendUrl = () => {
    let url = window.BACKEND_URL;
    if (!url || (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1' && (url.includes('localhost') || url.includes('127.0.0.1')))) {
        url = 'https://projectforge-ai-1.onrender.com';
    }
    return url.replace(/\/+$/, '');
};

const API_BASE = getBackendUrl();

// --- Auth Token Management ---
function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function removeToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
}

function getUser() {
    const userStr = localStorage.getItem('user_info');
    return userStr ? JSON.parse(userStr) : null;
}

function setUser(user) {
    localStorage.setItem('user_info', JSON.stringify(user));
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    removeToken();
    window.location.href = '/login/';
}

// --- Fetch Wrapper ---
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers,
    };

    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        
        if (response.status === 401) {
            // Token expired or invalid
            removeToken();
            if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register') && window.location.pathname !== '/') {
                window.location.href = '/login/';
            }
            throw new Error('Unauthorized');
        }

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const errorMsg = data.detail || data.message || `Request failed with status ${response.status}`;
            throw new Error(errorMsg);
        }

        return data;
    } catch (err) {
        console.error(`API Error (${endpoint}):`, err);
        throw err;
    }
}

// --- Common UI Helpers ---
function showAlert(message, type = 'info', containerId = 'alert-container') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} animate-in`;
    alert.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;margin-left:auto;font-weight:bold;">&times;</button>
    `;

    container.innerHTML = '';
    container.appendChild(alert);

    if (type !== 'danger') {
        setTimeout(() => alert.remove(), 5000);
    }
}

function showLoading(elementId, text = 'Loading...') {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = `
            <div class="loading-overlay">
                <div class="loading-spinner"></div>
                <p class="text-sm text-secondary">${text}</p>
            </div>
        `;
    }
}

// --- Check Auth Status on Protected Pages ---
document.addEventListener('DOMContentLoaded', () => {
    const publicPages = ['/', '/login/', '/register/'];
    const currentPath = window.location.pathname;

    if (!publicPages.includes(currentPath) && !isAuthenticated()) {
        window.location.href = '/login/';
    }

    // Update user name display if available
    const user = getUser();
    const userDisplay = document.getElementById('user-display-name');
    if (userDisplay && user) {
        userDisplay.textContent = user.username;
    }
});
