/**
 * Auth state management (placeholder for Stage 4)
 */

const Auth = {
    isAuthenticated: false,
    isDemo: false,
    user: null,

    /**
     * Enter demo mode
     */
    enterDemo() {
        this.isDemo = true;
        this.isAuthenticated = true;
        this.user = {
            name: 'Demo User',
            email: 'demo@example.com',
            picture: null,
            gmail_connected: true
        };
    },

    /**
     * Exit demo / logout
     */
    logout() {
        this.isDemo = false;
        this.isAuthenticated = false;
        this.user = null;
        Router.navigate('/');
    },

    /**
     * Get user initials for avatar
     */
    getInitials() {
        if (!this.user || !this.user.name) return '?';
        return this.user.name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }
};
