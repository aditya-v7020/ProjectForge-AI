import axios from 'axios';

const getBackendUrl = () => {
  let url = import.meta.env.VITE_BACKEND_URL;
  if (!url || (import.meta.env.PROD && (url.includes('localhost') || url.includes('127.0.0.1')))) {
    url = 'https://projectforge-ai-1.onrender.com';
  }
  return url.replace(/\/+$/, '');
};

const API_BASE = getBackendUrl();

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      if (!window.location.pathname.includes('/login') && 
          !window.location.pathname.includes('/register') && 
          window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
