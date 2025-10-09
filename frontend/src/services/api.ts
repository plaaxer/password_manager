// src/services/api.ts
import axios from 'axios';

// The base URL of your FastAPI backend
const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Interceptor to add the auth token to every protected request
api.interceptors.request.use((config) => {
  // Only add the token if the request is not for login or register
  if (!config.url?.endsWith('/login') && !config.url?.endsWith('/register')) {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;