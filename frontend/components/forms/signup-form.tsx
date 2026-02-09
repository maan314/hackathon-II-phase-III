'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { signUp } from '@/lib/auth-utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Notification from '@/components/ui/notification';

// Define the validation schema using Zod
const signUpSchema = z.object({
  first_name: z.string()
    .min(1, 'First name is required')
    .max(50, 'First name must be less than 50 characters'),
  last_name: z.string()
    .min(1, 'Last name is required')
    .max(50, 'Last name must be less than 50 characters'),
  email: z.string()
    .email('Please enter a valid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(new RegExp('.*[A-Z].*'), 'Password must contain at least one uppercase letter')
    .regex(new RegExp('.*[a-z].*'), 'Password must contain at least one lowercase letter')
    .regex(new RegExp('.*\\d.*'), 'Password must contain at least one number'),
});

type SignUpFormData = z.infer<typeof signUpSchema>;

interface SignUpFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function SignUpForm({ onSuccess, onError }: SignUpFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
  });

  const onSubmit = async (data: SignUpFormData) => {
    setIsLoading(true);

    try {
      await signUp(data);

      // Show success notification
      setNotification({ message: 'Account created successfully!', type: 'success' });

      if (onSuccess) {
        onSuccess();
      }
      reset(); // Clear the form on successful submission
    } catch (error: any) {
      const errorMessage = error.message || 'An error occurred during sign up';
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

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Name Fields Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* First Name Field */}
          <div className="space-y-2">
            <Label htmlFor="first_name" className="text-base font-semibold text-gray-200">
              First Name
            </Label>
            <Input
              id="first_name"
              {...register('first_name')}
              placeholder="Enter your first name"
              disabled={isLoading}
              className="h-12 text-base px-4 py-3 bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
            />
            {errors.first_name && (
              <p className="mt-1 text-sm text-red-400 font-medium">{errors.first_name.message}</p>
            )}
          </div>

          {/* Last Name Field */}
          <div className="space-y-2">
            <Label htmlFor="last_name" className="text-base font-semibold text-gray-200">
              Last Name
            </Label>
            <Input
              id="last_name"
              {...register('last_name')}
              placeholder="Enter your last name"
              disabled={isLoading}
              className="h-12 text-base px-4 py-3 bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
            />
            {errors.last_name && (
              <p className="mt-1 text-sm text-red-400 font-medium">{errors.last_name.message}</p>
            )}
          </div>
        </div>

        {/* Email Field */}
        <div className="space-y-2">
          <Label htmlFor="email" className="text-base font-semibold text-gray-200">
            Email Address
          </Label>
          <Input
            id="email"
            type="email"
            {...register('email')}
            placeholder="Enter your email address"
            disabled={isLoading}
            className="h-12 text-base px-4 py-3 bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-400 font-medium">{errors.email.message}</p>
          )}
        </div>

        {/* Password Field */}
        <div className="space-y-2">
          <Label htmlFor="password" className="text-base font-semibold text-gray-200">
            Password
          </Label>
          <Input
            id="password"
            type="password"
            {...register('password')}
            placeholder="Create a strong password"
            disabled={isLoading}
            className="h-12 text-base px-4 py-3 bg-gray-700/50 border-gray-600 text-white placeholder:text-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-400 font-medium">{errors.password.message}</p>
          )}
          <p className="text-xs text-gray-400 mt-1">
            Password must be at least 8 characters with uppercase, lowercase, and number.
          </p>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          className="w-full h-12 text-lg font-semibold py-6 transition-all duration-200 hover:shadow-lg bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating Account...
            </span>
          ) : (
            'Create Account'
          )}
        </Button>
      </form>
    </div>
  );
}