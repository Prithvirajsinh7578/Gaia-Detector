// api.js - Centralized API Service for Gaia Content Authenticity Detector

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Helper to process API responses cleanly
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = 'Request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.error || JSON.stringify(errJson);
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

/**
 * Health & Diagnostics
 */
export async function checkBackendHealth() {
  const res = await fetch(`${API_BASE_URL}/health`, {
    headers: { 'Accept': 'application/json' }
  });
  return handleResponse(res);
}

export async function checkBackendReadiness() {
  const res = await fetch(`${API_BASE_URL}/ready`, {
    headers: { 'Accept': 'application/json' }
  });
  return handleResponse(res);
}

/**
 * AI Content Authenticity Detection APIs
 */

// 1. Text Detection (JSON body)
export async function detectText(text) {
  const res = await fetch(`${API_BASE_URL}/detect/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({ text })
  });
  return handleResponse(res);
}

// 2. Image Detection (Multipart FormData)
export async function detectImage(file, uploadId = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (uploadId) formData.append('upload_id', uploadId);

  const res = await fetch(`${API_BASE_URL}/detect/image`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(res);
}

// 3. Video Detection (Multipart FormData)
export async function detectVideo(file, uploadId = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (uploadId) formData.append('upload_id', uploadId);

  const res = await fetch(`${API_BASE_URL}/detect/video`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(res);
}

// 4. Document Detection (.pdf, .docx, .txt)
export async function detectDocument(file, uploadId = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (uploadId) formData.append('upload_id', uploadId);

  const res = await fetch(`${API_BASE_URL}/detect/document`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(res);
}

/**
 * Storage & File Upload
 */
export async function uploadFile(file, type = 'image') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', type);

  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(res);
}

/**
 * History & Reports
 */
export async function getDetectionHistory() {
  const res = await fetch(`${API_BASE_URL}/history`, {
    headers: { 'Accept': 'application/json' }
  });
  return handleResponse(res);
}

export async function getDetectionReport(reportId) {
  const res = await fetch(`${API_BASE_URL}/report/${encodeURIComponent(reportId)}`, {
    headers: { 'Accept': 'application/json' }
  });
  return handleResponse(res);
}

/**
 * Authentication (JWT)
 */
export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return handleResponse(res);
}

export async function registerUser(name, email, password) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });
  return handleResponse(res);
}

export async function getCurrentUser() {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { 'Accept': 'application/json' }
  });
  return handleResponse(res);
}
