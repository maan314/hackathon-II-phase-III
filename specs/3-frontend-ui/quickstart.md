# Quickstart Guide: Todo Web Application Frontend UI

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Next.js 16+ installed
- Access to the backend API endpoints
- Understanding of JWT authentication concepts

## Setup Instructions

### 1. Initialize Next.js Project
```bash
npx create-next-app@latest todo-frontend
cd todo-frontend
```

### 2. Install Dependencies
```bash
npm install axios react-hook-form zod @hookform/resolvers
# Or with yarn
yarn add axios react-hook-form zod @hookform/resolvers
```

### 3. Environment Configuration
Create a `.env.local` file with the following variables:
```bash
# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret-for-local-dev

# For Production
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
```

### 4. Project Structure
Create the following directory structure for Next.js App Router:
```
todo-frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── signup/
│   │   └── page.tsx
│   ├── signin/
│   │   └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   └── _middleware.ts
├── lib/
│   ├── api-client.ts
│   └── auth-utils.ts
├── components/
│   ├── forms/
│   │   ├── signup-form.tsx
│   │   └── signin-form.tsx
│   └── ui/
│       ├── button.tsx
│       └── input.tsx
├── types/
│   └── auth.ts
├── public/
└── package.json
```

## Implementation

### lib/api-client.ts - Centralized API Client
```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth state and redirect to sign-in
      localStorage.removeItem('accessToken');
      window.location.href = '/signin';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  signUp: (userData: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    agreeTerms: boolean;
  }) => apiClient.post('/api/auth/signup', userData),

  signIn: (credentials: { email: string; password: string }) =>
    apiClient.post('/api/auth/signin', credentials),
};

export default apiClient;
```

### types/auth.ts - Type Definitions
```typescript
export interface UserRegistrationData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  agreeTerms: boolean;
}

export interface UserSignInData {
  email: string;
  password: string;
}

export interface AuthTokenResponse {
  accessToken: string;
  refreshToken?: string;
  user: {
    id: number;
    email: string;
    firstName: string;
    lastName: string;
  };
}

export interface FormState {
  formData: Record<string, any>;
  errors: Record<string, string>;
  isLoading: boolean;
  successMessage?: string;
  errorMessage?: string;
}
```

### app/_middleware.ts - Route Protection
```typescript
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Define protected routes
  const protectedRoutes = ['/dashboard'];
  const isProtectedRoute = protectedRoutes.some(route =>
    request.nextUrl.pathname.startsWith(route)
  );

  // Check for auth token
  const token = request.cookies.get('accessToken')?.value ||
                request.headers.get('Authorization')?.replace('Bearer ', '');

  // If accessing protected route without token, redirect to sign-in
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/signin', request.url));
  }

  // If user is logged in and accessing auth pages, redirect to dashboard
  if ((request.nextUrl.pathname === '/signin' ||
       request.nextUrl.pathname === '/signup') && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### components/forms/signup-form.tsx - Sign Up Form Component
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authApi } from '@/lib/api-client';

const signUpSchema = z.object({
  email: z.string().email({ message: 'Invalid email format' }).min(1, { message: 'Email is required' }),
  password: z.string().min(8, { message: 'Password must be at least 8 characters' }),
  firstName: z.string().min(1, { message: 'First name is required' }).max(50),
  lastName: z.string().min(1, { message: 'Last name is required' }).max(50),
  agreeTerms: z.boolean().refine(val => val === true, { message: 'You must agree to the terms of service' }),
});

type SignUpFormData = z.infer<typeof signUpSchema>;

export default function SignUpForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
  });

  const onSubmit = async (data: SignUpFormData) => {
    setLoading(true);
    setError('');

    try {
      await authApi.signUp(data);
      // Redirect to sign-in after successful sign-up
      router.push('/signin');
    } catch (err: any) {
      setError(err.response?.data?.error || 'An error occurred during sign-up');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <input
          {...register('email')}
          type="email"
          placeholder="Email"
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.email && (
          <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
        )}
      </div>

      <div>
        <input
          {...register('password')}
          type="password"
          placeholder="Password"
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.password && (
          <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
        )}
      </div>

      <div>
        <input
          {...register('firstName')}
          type="text"
          placeholder="First Name"
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.firstName && (
          <p className="text-red-500 text-sm mt-1">{errors.firstName.message}</p>
        )}
      </div>

      <div>
        <input
          {...register('lastName')}
          type="text"
          placeholder="Last Name"
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.lastName && (
          <p className="text-red-500 text-sm mt-1">{errors.lastName.message}</p>
        )}
      </div>

      <div className="flex items-center">
        <input
          {...register('agreeTerms')}
          type="checkbox"
          id="agreeTerms"
          className="mr-2"
        />
        <label htmlFor="agreeTerms" className="text-sm">
          I agree to the Terms of Service
        </label>
      </div>
      {errors.agreeTerms && (
        <p className="text-red-500 text-sm">{errors.agreeTerms.message}</p>
      )}

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Signing up...' : 'Sign Up'}
      </button>
    </form>
  );
}
```

### app/signup/page.tsx - Sign Up Page
```typescript
import SignUpForm from '@/components/forms/signup-form';

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <SignUpForm />
        <div className="text-center text-sm text-gray-600">
          Already have an account?{' '}
          <a href="/signin" className="font-medium text-blue-600 hover:text-blue-500">
            Sign in
          </a>
        </div>
      </div>
    </div>
  );
}
```

## Testing the Authentication Flows

### Test Authentication Flows

1. **Successful signup → redirect to signin**
```bash
# Navigate to http://localhost:3000/signup
# Fill form with valid data and submit
# Should redirect to http://localhost:3000/signin
```

2. **Invalid signup → error shown**
```bash
# Navigate to http://localhost:3000/signup
# Fill form with invalid data (e.g., invalid email)
# Submit and verify error messages are shown
```

3. **Successful signin → dashboard access**
```bash
# Navigate to http://localhost:3000/signin
# Enter valid credentials and submit
# Should redirect to http://localhost:3000/dashboard
```

4. **Unauthorized access → redirect to signin**
```bash
# Navigate directly to http://localhost:3000/dashboard
# Should redirect to http://localhost:3000/signin
```

## Next Steps

1. Implement the sign-in form component
2. Create the dashboard page with protected content
3. Add loading and success state indicators
4. Implement proper error handling and user feedback
5. Add responsive design and accessibility features
6. Set up proper logging for authentication events