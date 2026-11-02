/**
 * Geosense API Client
 * Reusable fetch wrapper for FastAPI backend endpoints.
 * Never exposes service-role keys; uses standard JWT Bearer tokens and anon keys.
 */

const API_CONFIG = {
  BASE_URL: window.GEOSENSE_API_URL || 'http://127.0.0.1:8001/api/v1',
  AUTH_TOKEN_KEY: 'geosense_auth_token',
  USER_DATA_KEY: 'geosense_user_data'
};

class ApiClient {
  static getToken() {
    return localStorage.getItem(API_CONFIG.AUTH_TOKEN_KEY);
  }

  static setSession(token, user) {
    if (token) localStorage.setItem(API_CONFIG.AUTH_TOKEN_KEY, token);
    if (user) localStorage.setItem(API_CONFIG.USER_DATA_KEY, JSON.stringify(user));
  }

  static clearSession() {
    localStorage.removeItem(API_CONFIG.AUTH_TOKEN_KEY);
    localStorage.removeItem(API_CONFIG.USER_DATA_KEY);
  }

  static getUser() {
    const data = localStorage.getItem(API_CONFIG.USER_DATA_KEY);
    return data ? JSON.parse(data) : null;
  }

  static async request(endpoint, options = {}) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    const headers = options.headers || {};

    const token = this.getToken();
    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorDetail = `HTTP Error ${response.status}: ${response.statusText}`;
        try {
          const errData = await response.json();
          errorDetail = errData.detail || errorDetail;
        } catch (_) {}
        throw new Error(errorDetail);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error on ${endpoint}:`, error);
      throw error;
    }
  }

  // --- Module 1: Soil Analysis ---
  static async analyzeSoilImage(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);

    return this.request('/soil/analyze', {
      method: 'POST',
      body: formData
    });
  }

  static async submitManualSoilTest(testData) {
    return this.request('/soil/manual', {
      method: 'POST',
      body: JSON.stringify(testData)
    });
  }

  static async getSoilHistory() {
    return this.request('/soil/history', {
      method: 'GET'
    });
  }

  // --- Module 2: Crop Recommendation ---
  static async getCropRecommendation(data) {
    return this.request('/crop/recommend', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static async getCropHistory() {
    return this.request('/crop/history', {
      method: 'GET'
    });
  }

  // --- Module 3: Smart Irrigation ---
  static async calculateIrrigation(data) {
    return this.request('/irrigation/calculate', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static async getIrrigationHistory() {
    return this.request('/irrigation/history', {
      method: 'GET'
    });
  }

  // --- Dashboard Overview ---
  static async getDashboardOverview() {
    return this.request('/overview/stats', {
      method: 'GET'
    });
  }

  // --- Module 8: AI Assistant ---
  static async chatWithAssistant(message) {
    return this.request('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ message })
    });
  }

  // --- Module 4: Weather Intelligence ---
  static async getWeather(lat = 20.5937, lon = 78.9629, locationName = 'Farm Location') {
    const params = new URLSearchParams({ lat, lon, location_name: locationName });
    return this.request(`/weather/current?${params.toString()}`, {
      method: 'GET'
    });
  }

  // --- Module 5: Market Intelligence ---
  static async getMarketPrices(commodity, state, mandi) {
    const params = new URLSearchParams();
    if (commodity) params.append('commodity', commodity);
    if (state) params.append('state', state);
    if (mandi) params.append('mandi', mandi);
    return this.request(`/market/prices?${params.toString()}`, {
      method: 'GET'
    });
  }

  static async getCommodityAnalysis(commodity = 'Wheat') {
    return this.request(`/market/analysis?commodity=${encodeURIComponent(commodity)}`, {
      method: 'GET'
    });
  }

  // --- Module 6: Community ---
  static async getCommunityPosts(category, search) {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);
    return this.request(`/community/posts?${params.toString()}`, {
      method: 'GET'
    });
  }

  static async createCommunityPost(postData) {
    return this.request('/community/posts', {
      method: 'POST',
      body: JSON.stringify(postData)
    });
  }

  static async togglePostLike(postId) {
    return this.request(`/community/posts/${postId}/like`, {
      method: 'POST'
    });
  }

  static async getPostComments(postId) {
    return this.request(`/community/posts/${postId}/comments`, {
      method: 'GET'
    });
  }

  static async addPostComment(postId, content) {
    return this.request(`/community/posts/${postId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content })
    });
  }

  // --- Module 7: Authentication ---
  static async registerUser(registrationData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(registrationData)
    });
  }

  static async loginUser(email, password) {
    const result = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (result.access_token) {
      this.setSession(result.access_token, result.user);
    }
    return result;
  }

  static async getProfile() {
    return this.request('/auth/me', {
      method: 'GET'
    });
  }
}

// Expose globally
window.GeosenseApi = ApiClient;

