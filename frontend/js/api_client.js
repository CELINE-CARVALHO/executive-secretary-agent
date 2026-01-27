const API_BASE = 'http://localhost:5000/api';

class APIClient {
    async request(endpoint, options = {}) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            credentials: "include",   // 🔥 REQUIRED
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        });

        return response.json();
    }

    get(endpoint) {
        return this.request(endpoint, { method: "GET" });
    }

    getGoogleAuthURL() {
        return this.get("/auth/google/url");
    }
}

window.apiClient = new APIClient();
