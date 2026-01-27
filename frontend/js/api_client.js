const API_BASE = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.baseURL = "http://localhost:5000/api";
    }

    async request(endpoint, options = {}) {
        const res = await fetch(this.baseURL + endpoint, {
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            ...options
        });

        if (!res.ok) {
            throw new Error("API error");
        }

        return res.json();
    }

    get(endpoint) {
        return this.request(endpoint, { method: "GET" });
    }

    post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: "POST",
            body: JSON.stringify(data)
        });
    }
}

window.apiClient = new APIClient();
