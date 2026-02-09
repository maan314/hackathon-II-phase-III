'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import SignInForm from '@/components/forms/signin-form';

export default function SignInPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const handleSignInSuccess = () => {
    // Redirect to dashboard after successful sign in
    // Using window.location to ensure redirect happens even if router.push fails
    window.location.href = '/dashboard';
  };

  const handleSignInError = (errorMessage: string) => {
    setError(errorMessage);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
      <div className="w-full max-w-md rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 shadow-2xl shadow-cyan-500/20">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent mb-2">
            Welcome Back
          </h1>
          <p className="text-gray-400">Sign in to your account to continue</p>
        </div>

        <div className="mb-6">
          <SignInForm
            onSuccess={handleSignInSuccess}
            onError={handleSignInError}
          />
          {error && (
            <div className="mt-4 rounded-lg bg-red-900/30 p-4 border border-red-500/50">
              <p className="text-sm text-red-200">{error}</p>
            </div>
          )}
        </div>

        <div className="text-center space-y-3">
          <p className="text-gray-300">
            Don't have an account?{' '}
            <Link href="/signup" className="font-medium text-cyan-400 hover:text-cyan-300 hover:underline transition-colors">
              Sign up
            </Link>
          </p>
          <p className="text-xs text-gray-400">
            By signing in, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
}