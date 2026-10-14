/**
 * Gaia Detector — Centralized API Client
 * Uses native fetch with credentials: 'include' for secure httpOnly cookie authentication.
 * No tokens are stored in localStorage or sessionStorage.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = { ...options.headers };

  // If body is NOT FormData, default to application/json
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers,
    credentials: 'include', // Ensures httpOnly cookies are sent and received
  };

  try {
    const response = await fetch(url, config);

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const errorMsg =
        (data && data.detail) ||
        (data && data.message) ||
        `Request failed with status ${response.status}`;
      const error = new Error(errorMsg);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (error) {
    if (!error.status) {
      // Network or connection error
      error.message = error.message || 'Network error: could not connect to server.';
    }
    throw error;
  }
}

export const api = {
  // System
  getHealth: () => request('/health'),
  getReady: () => request('/ready'),

  // Authentication
  register: (name, email, password) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    }),

  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  logout: () =>
    request('/auth/logout', {
      method: 'POST',
    }),

  getMe: () => request('/auth/me'),

  // Upload
  uploadFile: (file, type = 'image') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    return request('/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Detection endpoints
  detectImage: (file, uploadId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (uploadId) formData.append('upload_id', uploadId);
    return request('/detect/image', {
      method: 'POST',
      body: formData,
    });
  },

  detectText: (text) =>
    request('/detect/text', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),

  detectDocument: (file, uploadId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (uploadId) formData.append('upload_id', uploadId);
    return request('/detect/document', {
      method: 'POST',
      body: formData,
    });
  },

  detectVideo: (file, uploadId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (uploadId) formData.append('upload_id', uploadId);
    return request('/detect/video', {
      method: 'POST',
      body: formData,
    });
  },

  // History & Reports
  getHistory: (limit = 20, skip = 0) =>
    request(`/history?limit=${limit}&skip=${skip}`),

  getHistoryDetail: (id) => request(`/history/${id}`),

  getReport: (id) => request(`/report/${id}`),
};

export default api;
