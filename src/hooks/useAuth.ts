import { useState, useEffect } from 'react';
import { apiRequest } from '../lib/api';
import type { User } from '../types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      console.log('🔍 Checking authentication status...');
      const token = localStorage.getItem('access_token');
      console.log('🎫 Token found in localStorage:', !!token);
      
      if (token) {
        try {
          console.log('✅ Token exists, verifying with backend...');
          // Verify token and get user info from backend
          const userData = await apiRequest('/api/auth/me');
          console.log('👤 User data received:', userData);
          setUser(userData);
          setIsAuthenticated(true);
          console.log('🎉 Authentication successful!');
        } catch (error) {
          // Token invalid, clear it
          console.log('❌ Token verification failed:', error);
          localStorage.removeItem('access_token');
          console.error('Auth check failed:', error);
        }
      } else {
        console.log('ℹ️ No token found, user needs to login');
      }
      
      setIsLoading(false);
      console.log('✅ Auth check complete, isLoading set to false');
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null); // Clear previous errors
    
    try {
      console.log('🔐 Attempting login with:', { email, backend: 'http://localhost:8001' });
      
      // Call backend login endpoint
      const response = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      
      console.log('✅ Login response:', response);
      
      // Store token
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token);
        console.log('💾 Token stored in localStorage');
        
        // Get user profile
        const userData = await apiRequest('/api/auth/me');
        console.log('👤 User data received:', userData);
        
        setUser(userData);
        setIsAuthenticated(true);
        console.log('🎉 Login successful!');
      } else {
        throw new Error('No access token received');
      }
      
      return response;
    } catch (error: any) {
      console.error('❌ Login failed:', error);
      const errorMessage = error.message || 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Call backend logout endpoint
      await apiRequest('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local storage
      localStorage.removeItem('access_token');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const register = async (email: string, password: string, name: string, organization?: string) => {
    setIsLoading(true);
    
    try {
      // Call backend registration endpoint
      const response = await apiRequest('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ 
          email, 
          password, 
          name, 
          organization 
        })
      });
      
      // Registration successful, now login
      await login(email, password);
      
      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    register
  };
}