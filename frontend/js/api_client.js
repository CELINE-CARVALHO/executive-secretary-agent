
// API Client for Executive Secretary Backend
const DEMO_MODE = window.DEMO_MODE === true;
const BASE_PATH = '/frontend';




class APIClient {
    getMockResponse(endpoint) {
    console.log(`DEMO MODE: Mock API call -> ${endpoint}`);

    // Dashboard
    if (endpoint.includes('/dashboard/stats')) {
        return {
            emails: 3,
            pendingApprovals: 1,
            tasks: 5,
            events: 2
        };
    }

    if (endpoint.includes('/dashboard/activity')) {
        return [
            { action: 'Processed email from CEO', time: '5 min ago' },
            { action: 'Approved task: Client Meeting', time: '30 min ago' }
        ];
    }

    // Emails
    if (endpoint.includes('/emails')) {
        return [];
    }

    // Tasks
    if (endpoint.includes('/tasks')) {
        return [];
    }

    // Approvals
    if (endpoint.includes('/approvals')) {
        return [];
    }

    // Calendar
    if (endpoint.includes('/calendar')) {
        return [];
    }

    // Settings
    if (endpoint.includes('/settings')) {
        return {};
    }

    return {};
}

    constructor(baseURL = DEMO_MODE ? null : '/api') {

        this.baseURL = baseURL;
        this.token = null;
    }
    
    // Set authentication token
    setToken(token) {
        this.token = token;
        if (token) {
            Storage.set('token', token);
        } else {
            Storage.remove('token');
        }
    }
    
    // Get authentication token
    getToken() {
        if (!this.token) {
            this.token = Storage.get('token');
        }
        return this.token;
    }
    
    // Get default headers
    getHeaders(customHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...customHeaders
        };
        
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }
    
    // Handle API response
    async handleResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            
            if (!response.ok) {
                // Handle authentication errors
                if (response.status === 401) {
                    this.setToken(null);

                    if (!DEMO_MODE) {
                        window.location.href = `${BASE_PATH}/login.html`;
                    }

                    throw new Error('Session expired. Please login again.');
                }

                
                throw new Error(data.message || data.error || 'API request failed');
            }
            
            return data;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response;
    }
    
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.headers)
        };
        
        try {
            if (DEMO_MODE) {
                return Promise.resolve(this.getMockResponse(endpoint));
            }

        const response = await fetch(url, config);
        return await this.handleResponse(response);

        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }
    
    // GET request
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET'
        });
    }
    
    // POST request
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // PUT request
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    // PATCH request
    async patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
    
    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
    
    // ========== Authentication Endpoints ==========
    
    async login(email) {
    if (DEMO_MODE) {
        return {
            token: 'demo-token',
            user: { email, fullName: 'Demo User' }
        };
    }

    return this.post('/auth/login', { email });
}

    
    async logout() {
    if (DEMO_MODE) {
        this.setToken(null);
        return;
    }

    await this.post('/auth/logout');
}

    
    async getCurrentUser() {
    if (DEMO_MODE) {
        return { user: { fullName: 'Demo User', email: 'demo@executive.ai' } };
    }

    return this.get('/auth/me');
}

    
    // ========== Email Endpoints ==========
    
    async getEmails(filters = {}) {
        return this.get('/emails', filters);
    }
    
    async getEmailById(id) {
        return this.get(`/emails/${id}`);
    }
    
    async syncEmails() {
        return this.post('/emails/sync');
    }
    
    async processEmail(emailId) {
        return this.post(`/emails/${emailId}/process`);
    }
    
    async markEmailAsRead(emailId) {
        return this.patch(`/emails/${emailId}`, { read: true });
    }
    
    // ========== Task Endpoints ==========
    
    async getTasks(filters = {}) {
        return this.get('/tasks', filters);
    }
    
    async getTaskById(id) {
        return this.get(`/tasks/${id}`);
    }
    
    async createTask(taskData) {
        return this.post('/tasks', taskData);
    }
    
    async updateTask(id, taskData) {
        return this.put(`/tasks/${id}`, taskData);
    }
    
    async deleteTask(id) {
        return this.delete(`/tasks/${id}`);
    }
    
    async completeTask(id) {
        return this.patch(`/tasks/${id}`, { status: 'completed' });
    }
    
    // ========== Approval Endpoints ==========
    
    async getPendingApprovals() {
        return this.get('/approvals', { status: 'pending' });
    }
    
    async getApprovalById(id) {
        return this.get(`/approvals/${id}`);
    }
    
    async approveTask(approvalId, modifications = {}) {
        return this.post(`/approvals/${approvalId}/approve`, modifications);
    }
    
    async rejectTask(approvalId, reason = '') {
        return this.post(`/approvals/${approvalId}/reject`, { reason });
    }
    
    async updateApproval(approvalId, updates) {
        return this.put(`/approvals/${approvalId}`, updates);
    }
    
    async approveAll() {
        return this.post('/approvals/approve-all');
    }
    
    // ========== Calendar Endpoints ==========
    
    async getCalendarEvents(startDate, endDate) {
        return this.get('/calendar/events', { 
            start: startDate, 
            end: endDate 
        });
    }
    
    async createCalendarEvent(eventData) {
        return this.post('/calendar/events', eventData);
    }
    
    async updateCalendarEvent(id, eventData) {
        return this.put(`/calendar/events/${id}`, eventData);
    }
    
    async deleteCalendarEvent(id) {
        return this.delete(`/calendar/events/${id}`);
    }
    
    async getAvailability(date) {
        return this.get('/calendar/availability', { date });
    }
    
    async syncCalendar() {
        return this.post('/calendar/sync');
    }
    
    // ========== Dashboard Endpoints ==========
    
    async getDashboardStats() {
        return this.get('/dashboard/stats');
    }
    
    async getRecentActivity(limit = 10) {
        return this.get('/dashboard/activity', { limit });
    }
    
    async getDailySummary(date = null) {
        return this.get('/dashboard/summary', date ? { date } : {});
    }
    
    // ========== Settings Endpoints ==========
    
    async getSettings() {
        return this.get('/settings');
    }
    
    async updateSettings(settings) {
        return this.put('/settings', settings);
    }
    
    async updateProfile(profileData) {
        return this.put('/settings/profile', profileData);
    }
    
    async changePassword(currentPassword, newPassword) {
        return this.post('/settings/password', { 
            currentPassword, 
            newPassword 
        });
    }
    
    async updateNotificationPreferences(preferences) {
        return this.put('/settings/notifications', preferences);
    }
    
    async updateAIPreferences(preferences) {
        return this.put('/settings/ai', preferences);
    }
    
    // ========== Integration Endpoints ==========
    
    async connectGmail() {
        return this.get('/integrations/gmail/authorize');
    }
    
    async disconnectGmail() {
        return this.delete('/integrations/gmail');
    }
    
    async getGmailStatus() {
        return this.get('/integrations/gmail/status');
    }
    
    async connectCalendar() {
        return this.get('/integrations/calendar/authorize');
    }
    
    async disconnectCalendar() {
        return this.delete('/integrations/calendar');
    }
    
    async getCalendarStatus() {
        return this.get('/integrations/calendar/status');
    }
    
    // ========== Notification Endpoints ==========
    
    async getNotifications(limit = 20) {
        return this.get('/notifications', { limit });
    }
    
    async markNotificationAsRead(id) {
        return this.patch(`/notifications/${id}`, { read: true });
    }
    
    async markAllNotificationsAsRead() {
        return this.post('/notifications/mark-all-read');
    }
    
    async deleteNotification(id) {
        return this.delete(`/notifications/${id}`);
    }
}



// Create global instance
const apiClient = new APIClient();

// Make it available globally
window.apiClient = apiClient;
window.APIClient = APIClient;