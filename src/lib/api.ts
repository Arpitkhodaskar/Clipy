// API Configuration for ClipVault Backend
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8001',
  ENDPOINTS: {
    AUTH: '/api/auth',
    USERS: '/api/users', 
    DEVICES: '/api/devices',
    CLIPBOARD: '/api/clipboard',
    SECURITY: '/api/security',
    AUDIT: '/api/audit'
  }
};

// API utility function
export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  const token = localStorage.getItem('access_token');
  
  console.log(`🌐 API Request: ${endpoint}`, { hasToken: !!token, url });
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    console.log(`🌐 API Response: ${endpoint}`, { 
      status: response.status, 
      ok: response.ok 
    });
    
    if (response.status === 401 && token) {
      // Token expired - redirect to login only if we had a token
      localStorage.removeItem('access_token');
      window.location.reload();
      throw new Error('Session expired');
    }
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`🌐 API Error: ${endpoint}`, { status: response.status, error: errorText });
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`🌐 API Success: ${endpoint}`, data);
    return data;
  } catch (error) {
    console.error('🌐 API request failed:', { endpoint, error });
    throw error;
  }
}
