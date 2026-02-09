'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { signIn } from '@/lib/auth-utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Notification from '@/components/ui/notification';

// Define the validation schema using Zod
const signInSchema = z.object({
  email: z.string()
    .email('Please enter a valid email address'),
  password: z.string()
    .min(1, 'Password is required'),
});

type SignInFormData = z.infer<typeof signInSchema>;

interface SignInFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function SignInForm({ onSuccess, onError }: SignInFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SignInFormData>({
    resolver: zodResolver(signInSchema),
  });

  const onSubmit = async (data: SignInFormData) => {
    setIsLoading(true);

    try {
      await signIn(data);

      // Show success notification
      setNotification({ message: 'Signed in successfully!', type: 'success' });

      if (onSuccess) {
        onSuccess();
      }
      reset(); // Clear the form on successful submission
    } catch (error: any) {
      const errorMessage = error.message || 'An error occurred during sign in';
      setNotification({ message: errorMessage, type: 'error' });

      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative">
      {/* Notification Component */}
      {notification && (
        <div className="mb-4">
          <Notification
            message={notification.message}
            type={notification.type}
            duration={5000}
            onClose={() => setNotification(null)}
          />
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Email Field */}
        <div>
          <Label htmlFor="email" className="text-gray-200">Email</Label>
          <Input
            id="email"
            type="email"
            {...register('email')}
            placeholder="Enter your email"
            disabled={isLoading}
            className="bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:ring-cyan-500 focus:border-cyan-500"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
          )}
        </div>

        {/* Password Field */}
        <div>
          <Label htmlFor="password" className="text-gray-200">Password</Label>
          <Input
            id="password"
            type="password"
            {...register('password')}
            placeholder="Enter your password"
            disabled={isLoading}
            className="bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:ring-cyan-500 focus:border-cyan-500"
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
          )}
        </div>

        {/* Forgot Password Link */}
        <div className="text-right text-sm">
          <a href="/forgot-password" className="text-cyan-400 hover:text-cyan-300 hover:underline transition-colors">
            Forgot password?
          </a>
        </div>

        {/* Submit Button */}
        <Button 
          type="submit" 
          className="w-full bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white" 
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
            </span>
          ) : (
            'Sign In'
          )}
        </Button>
      </form>
    </div>
  );
}