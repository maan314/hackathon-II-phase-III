import { AuthResponse, SignUpRequest, SignInRequest, TokenPayload } from '@/types/auth';
import { api } from '@/lib/api-client';

// Store token in localStorage
export const setToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token);
  }
};

// Get token from localStorage
export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

// Remove token from localStorage
export const removeToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
};

// Decode JWT token to get payload
export const decodeToken = (token: string): TokenPayload | null => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

// Check if token is expired
export const isTokenExpired = (token: string): boolean => {
  const payload = decodeToken(token);
  if (!payload) return true;

  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp < currentTime;
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  const token = getToken();
  if (!token) return false;
  return !isTokenExpired(token);
};

// Sign up function
export const signUp = async (userData: SignUpRequest): Promise<AuthResponse> => {
  try {
    // Map camelCase to snake_case for backend compatibility
    const backendData = {
      email: userData.email,
      password: userData.password,
      first_name: userData.first_name,
      last_name: userData.last_name
    };

    const response = await api.post<AuthResponse>('/auth/signup', backendData);
    const { token, user } = response.data;

    // Store the token and user data
    setToken(token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Sign up failed');
  }
};

// Sign in function
export const signIn = async (credentials: SignInRequest): Promise<AuthResponse> => {
  try {
    const response = await api.post<AuthResponse>('/auth/signin', credentials);
    const { token, user } = response.data;

    // Store the token and user data
    setToken(token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }

    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Sign in failed');
  }
};

// Sign out function
export const signOut = (): void => {
  removeToken();
  if (typeof window !== 'undefined') {
    localStorage.removeItem('user');
  }
};

// Refresh token (if needed)
export const refreshToken = async (): Promise<string | null> => {
  const refreshTokenStored = localStorage.getItem('refreshToken');
  if (!refreshTokenStored) {
    return null;
  }

  try {
    const response = await api.post<{ token: string }>('/auth/refresh', {
      refreshToken: refreshTokenStored,
    });

    const { token } = response.data;
    setToken(token);

    return token;
  } catch (error) {
    console.error('Error refreshing token:', error);
    removeToken();
    return null;
  }
};