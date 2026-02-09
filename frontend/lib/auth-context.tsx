'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { isAuthenticated, getToken, decodeToken, signIn as signInUtil, signUp as signUpUtil, signOut as signOutUtil } from './auth-utils';
import { AuthContextType, User } from '@/types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize auth state on mount
    initializeAuth();
  }, []);

  const initializeAuth = () => {
    try {
      const storedToken = getToken();
      const storedUser = typeof window !== 'undefined' ? localStorage.getItem('user') : null;

      if (storedToken && storedUser) {
        setToken(storedToken);
        try {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
        } catch (parseError) {
          console.error('Error parsing stored user data:', parseError);
        }
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const signIn = async (credentials: { email: string; password: string }) => {
    try {
      const response = await signInUtil(credentials);
      setToken(response.token);

      // Update user state with data from response
      setUser(response.user);
    } catch (error) {
      throw error;
    }
  };

  const signUp = async (userData: { email: string; password: string; first_name: string; last_name: string }) => {
    try {
      const response = await signUpUtil(userData);
      setToken(response.token);

      // Update user state with data from response
      setUser(response.user);
    } catch (error) {
      throw error;
    }
  };

  const signOut = () => {
    signOutUtil();
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    signIn,
    signUp,
    signOut,
    isAuthenticated: !!user && !!token,
    isLoading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}