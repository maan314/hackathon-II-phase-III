'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import SignUpForm from '@/components/forms/signup-form';

export default function SignUpPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const handleSignUpSuccess = () => {
    router.push('/signin');
  };

  const handleSignUpError = (errorMessage: string) => {
    setError(errorMessage);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
      <div className="w-full max-w-lg rounded-2xl border border-purple-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 shadow-2xl shadow-purple-500/20">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-500 bg-clip-text text-transparent mb-2">
            Create Your Account
          </h1>
          <p className="text-gray-400 text-base">
            Join us today and get started with your personalized experience
          </p>
        </div>

        <div className="mb-6">
          <SignUpForm
            onSuccess={handleSignUpSuccess}
            onError={handleSignUpError}
          />
          {error && (
            <div className="mt-6 rounded-lg bg-red-900/30 p-4 border border-red-500/50">
              <p className="text-sm text-red-200 font-medium">{error}</p>
            </div>
          )}
        </div>

        <div className="text-center space-y-3">
          <p className="text-gray-300">
            Already have an account?{' '}
            <Link href="/signin" className="font-medium text-purple-400 hover:text-purple-300 hover:underline transition-colors">
              Sign in
            </Link>
          </p>
          <p className="text-sm text-gray-400 text-center leading-relaxed">
            By signing up, you agree to our{' '}
            <Link href="/terms" className="underline text-gray-300 hover:text-gray-200">Terms of Service</Link>{' '}
            and{' '}
            <Link href="/privacy" className="underline text-gray-300 hover:text-gray-200">Privacy Policy</Link>.
          </p>
        </div>
      </div>
    </div>
  );
}