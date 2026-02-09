// Authentication request types
export interface SignUpRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

// Authentication response types
export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export interface SignUpResponse extends AuthResponse {}

export interface SignInResponse extends AuthResponse {}

// Token payload type (decoded JWT)
export interface TokenPayload {
  userId: string;
  email: string;
  exp: number;
  iat: number;
}

// Authentication context type
export interface AuthContextType {
  user: User | null;
  token: string | null;
  signIn: (credentials: SignInRequest) => Promise<void>;
  signUp: (userData: SignUpRequest) => Promise<void>;
  signOut: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// User type for general use
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

// Error response type
export interface ApiError {
  message: string;
  statusCode?: number;
  fieldErrors?: Record<string, string[]>;
}