/**
 * API client for communicating with the FastAPI backend
 */

const API = {
    baseUrl: '',

    /**
     * Make an API request
     */
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Request failed (${response.status})`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error.message);
            throw error;
        }
    },

    // ─── Demo Endpoints ────────────────────────

    async getDemoEmails() {
        return this.request('/api/demo/emails');
    },

    async getDemoEmailDetail(emailId) {
        return this.request(`/api/demo/emails/${emailId}`);
    },

    async getDemoDashboard() {
        return this.request('/api/demo/dashboard');
    },

    async getDemoActions() {
        return this.request('/api/demo/actions');
    },

    async getDemoStats() {
        return this.request('/api/demo/stats');
    },

    // ─── Auth Endpoints (Stage 4) ──────────────

    async getCurrentUser() {
        return this.request('/api/me');
    },

    // ─── Health ────────────────────────────────

    async healthCheck() {
        return this.request('/api/health');
    }
};


/**
 * Toast notification system
 */
const Toast = {
    container: null,

    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    },

    show(message, type = 'default', duration = 3000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        this.container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'error');
    }
};
