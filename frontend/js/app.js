// Main Application Entry Point
window.isDemo = () => window.DEMO_MODE === true;


class ExecutiveSecretaryApp {
    constructor() {
        this.initialized = false;
        this.version = '1.0.0';
    }
    
    async initialize() {
        if (this.initialized) return;
        
        try {
            console.log(`Executive Secretary AI v${this.version} - Initializing...`);
            
            // Check authentication
            if (!window.DEMO_MODE) {
                if (!authManager.isAuthenticated()) {
                    console.log('User not authenticated, redirecting to login...');
                    return;
                }

                // Load user data
                await authManager.loadCurrentUser();
            } else {
                console.log('DEMO MODE: Skipping authentication');
            }

            
            // Load user data
            await authManager.loadCurrentUser();
            
            // Initialize dashboard if on dashboard page
            if (document.getElementById('overview') && window.dashboardManager) {
                await dashboardManager.initialize?.();
            }

            
            // Initialize approval manager if on approval page
            if (document.getElementById('approvalsList') && window.approvalManager) {
                await approvalManager.initialize?.();
            }

            
            // Setup global event listeners
            this.setupGlobalEventListeners();
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            // Check for updates periodically
            this.startUpdateChecker();
            
            this.initialized = true;
            console.log('Executive Secretary AI initialized successfully');
            
        } catch (error) {
            console.error('Application initialization error:', error);
            Toast.error('Failed to initialize application');
        }
    }
    
    // Setup global event listeners
    setupGlobalEventListeners() {
        // Handle online/offline events
        window.addEventListener('online', () => {
            Toast.success('Back online');
            this.syncWhenOnline();
        });
        
        window.addEventListener('offline', () => {
            Toast.warning('You are offline. Changes will sync when back online.');
        });
        
        // Handle visibility change (tab focus)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.initialized) {
                this.onPageFocus();
            }
        });
        
        // Handle beforeunload (warn about unsaved changes)
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K: Global search (placeholder)
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                Toast.info('Global search coming soon');
            }
            
            // Ctrl/Cmd + R: Refresh data
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                if (dashboardManager && dashboardManager.refreshData) {
                    dashboardManager.refreshData();
                }
            }
            
            // Ctrl/Cmd + /: Show keyboard shortcuts
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                this.showKeyboardShortcuts();
            }
        });
    }
    
    // Show keyboard shortcuts help
    showKeyboardShortcuts() {
        const shortcuts = `
            <div style="padding: 20px;">
                <h3 style="margin-bottom: 16px;">Keyboard Shortcuts</h3>
                <div style="display: grid; gap: 12px;">
                    <div><kbd>Ctrl/Cmd + K</kbd> - Global Search</div>
                    <div><kbd>Ctrl/Cmd + R</kbd> - Refresh Data</div>
                    <div><kbd>Ctrl/Cmd + /</kbd> - Show Shortcuts</div>
                    <div><kbd>ESC</kbd> - Close Modal</div>
                </div>
            </div>
        `;
        
        // Create a temporary modal or use toast
        Toast.info('See console for keyboard shortcuts', 3000);
        console.log('Keyboard Shortcuts:\n- Ctrl/Cmd + K: Global Search\n- Ctrl/Cmd + R: Refresh\n- Ctrl/Cmd + /: Shortcuts\n- ESC: Close Modal');
    }
    
    // Handle page focus
    async onPageFocus() {
        // Refresh data when user returns to the page
        if (dashboardManager && typeof dashboardManager.loadApprovalCount === 'function') {
            await dashboardManager.loadApprovalCount();
        }
    }
    
    // Sync data when coming back online
    async syncWhenOnline() {
        try {
            if (!window.DEMO_MODE && dashboardManager?.refreshData) {
            await dashboardManager.refreshData();
        }

        } catch (error) {
            console.error('Sync error:', error);
        }
    }
    
    // Check for unsaved changes
    hasUnsavedChanges() {
        // Implement logic to check for unsaved form data
        // This is a placeholder
        return false;
    }
    
    // Start periodic update checker
    startUpdateChecker() {
        // Check for app updates every 30 minutes
        setInterval(() => {
            this.checkForUpdates();
        }, 30 * 60 * 1000);
    }
    
    // Check for application updates
    async checkForUpdates() {
        if (window.DEMO_MODE) return;

        try {
            const response = await fetch('/api/version');
            const data = await response.json();

            if (data.version && data.version !== this.version) {
                this.notifyUpdate(data.version);
            }
        } catch (error) {
            console.debug('Update check failed:', error);
        }
    }

    
    // Notify user of available update
    notifyUpdate(newVersion) {
        const toast = Toast.info(
            `New version ${newVersion} available. <a href="#" onclick="location.reload()">Reload</a> to update.`,
            0 // Don't auto-hide
        );
    }
    
    // Get application info
    getInfo() {
        return {
            version: this.version,
            initialized: this.initialized,
            user: authManager.getCurrentUser(),
            online: navigator.onLine
        };
    }
}

// Create global app instance
const app = new ExecutiveSecretaryApp();

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    await app.initialize();
});

// Handle page load
window.addEventListener('load', () => {
    // Hide any loading spinners
    Loading.hide();
});

// Handle errors
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    
    // Don't show toast for script loading errors
    if (event.message.includes('Script error')) {
        return;
    }
    
    Toast.error('An unexpected error occurred');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Check if it's an authentication error
    if (event.reason && event.reason.message && event.reason.message.includes('401')) {
        return; // Auth handler will deal with it
    }
    
    Toast.error('An unexpected error occurred');
});

// Export app instance
window.app = app;

// Console welcome message
console.log('%cExecutive Secretary AI', 'font-size: 24px; font-weight: bold; color: #667eea;');
console.log('%cv' + app.version, 'font-size: 14px; color: #718096;');
console.log('%cType app.getInfo() to see application status', 'font-size: 12px; color: #a0aec0;');