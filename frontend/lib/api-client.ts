import axios from 'axios';

// Use environment variable for API URL (defaults to localhost for development)
const baseURL = process.env.NEXT_PUBLIC_API_URL || 'https://maan143-hackathon-ii-phase-ii-backend.hf.space';

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

export const api = {
  get: <T>(url: string, config?: any) => apiClient.get<T>(url, config),
  post: <T>(url: string, data?: any, config?: any) => apiClient.post<T>(url, data, config),
  put: <T>(url: string, data?: any, config?: any) => apiClient.put<T>(url, data, config),  // No change for /{id} routes
  delete: <T>(url: string, config?: any) => apiClient.delete<T>(url, config),  // No change for /{id} routes
  patch: <T>(url: string, data?: any, config?: any) => apiClient.patch<T>(url, data, config),
};