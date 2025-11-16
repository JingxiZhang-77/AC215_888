/**
 * API Service Layer
 * 
 * Centralized API calls using axios with authentication.
 * Following best practices for error handling and token management.
 */

import axios from 'axios';
import { BASE_API_URL, getAuthToken, removeAuthToken } from './Common';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: BASE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      removeAuthToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

const DataService = {
  /**
   * Initialize service
   */
  Init: function () {
    console.log('DataService initialized with API URL:', BASE_API_URL);
  },

  /**
   * Authentication APIs
   */
  Auth: {
    /**
     * User login
     */
    login: async function (username, password) {
      const response = await api.post('/auth/login', { username, password });
      return response.data;
    },

    /**
     * Password reset request
     */
    forgotPassword: async function (username, email) {
      const response = await api.post('/auth/forgot-password', { username, email });
      return response.data;
    },

    /**
     * Reset password with token
     */
    resetPassword: async function (token, newPassword) {
      const response = await api.post('/auth/reset-password', { token, new_password: newPassword });
      return response.data;
    },

    /**
     * Verify token
     */
    verifyToken: async function () {
      const response = await api.get('/auth/verify');
      return response.data;
    },
  },

  /**
   * Classification APIs
   */
  Classification: {
    /**
     * Classify single incident
     */
    classifySingle: async function (description, department = null) {
      const response = await api.post('/classify/', { 
        description, 
        department 
      });
      return response.data;
    },

    /**
     * Classify batch from file
     */
    classifyBatch: async function (file) {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/classify/batch', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },

    /**
     * Classify from audio
     */
    classifyAudio: async function (audioFile, language = 'en-US', department = null, autoTranslate = true) {
      const formData = new FormData();
      formData.append('file', audioFile);
      formData.append('language', language);
      if (department) formData.append('department', department);
      formData.append('auto_translate', autoTranslate);

      const response = await api.post('/classify/audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
  },

  /**
   * Audio APIs
   */
  Audio: {
    /**
     * Transcribe audio without classification
     */
    transcribe: async function (audioFile, language = 'en-US', autoTranslate = true) {
      const formData = new FormData();
      formData.append('file', audioFile);
      formData.append('language', language);
      formData.append('auto_translate', autoTranslate);

      const response = await api.post('/audio/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },

    /**
     * Get supported languages
     */
    getSupportedLanguages: async function () {
      const response = await api.get('/audio/languages');
      return response.data;
    },
  },

  /**
   * User Management APIs (Admin only)
   */
  Users: {
    /**
     * List all users
     */
    listUsers: async function () {
      const response = await api.get('/users/');
      return response.data;
    },

    /**
     * Get user details
     */
    getUser: async function (username) {
      const response = await api.get(`/users/${username}`);
      return response.data;
    },

    /**
     * Get current user
     */
    getCurrentUser: async function () {
      const response = await api.get('/users/me');
      return response.data;
    },

    /**
     * Update user
     */
    updateUser: async function (username, updateData) {
      const response = await api.patch(`/users/${username}`, updateData);
      return response.data;
    },

    /**
     * Delete user
     */
    deleteUser: async function (username) {
      const response = await api.delete(`/users/${username}`);
      return response.data;
    },
  },
};

export default DataService;
