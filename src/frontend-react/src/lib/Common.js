/**
 * API Configuration and Utilities
 * 
 * Centralized API configuration following best practices.
 */

export const BASE_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000/api/v1';
export const APP_VERSION = '1.0.0';

/**
 * Get authentication token from localStorage
 */
export function getAuthToken() {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
}

/**
 * Set authentication token in localStorage
 */
export function setAuthToken(token) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
}

/**
 * Remove authentication token from localStorage
 */
export function removeAuthToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }
}

/**
 * Get user data from localStorage
 */
export function getUserData() {
  if (typeof window !== 'undefined') {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }
  return null;
}

/**
 * Set user data in localStorage
 */
export function setUserData(userData) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user_data', JSON.stringify(userData));
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return !!getAuthToken();
}

/**
 * Check if user has required role
 */
export function hasRole(requiredRoles) {
  const userData = getUserData();
  if (!userData || !userData.role) return false;
  
  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
  return roles.includes(userData.role);
}

/**
 * Format date to readable string
 */
export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
}

/**
 * Generate unique ID
 */
export function uuid() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
    (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
  );
}
