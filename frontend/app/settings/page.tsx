'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { useTheme } from '@/lib/theme-context';

// Force dynamic rendering to prevent static generation issues with context
export const dynamic = 'force-dynamic';

export default function SettingsPage() {
  const { user, isLoading, signOut } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const router = useRouter();

  // State for settings
  const [emailNotifications, setEmailNotifications] = useState(true);

  const handleSignOut = () => {
    signOut();
    router.push('/signin');
  };

  // Handle email notifications toggle
  const toggleEmailNotifications = () => {
    setEmailNotifications(!emailNotifications);
    // In a real app, you would save this to the backend
    console.log('Email notifications:', !emailNotifications);
  };

  // Handle dark mode toggle
  const toggleDarkMode = () => {
    toggleTheme();
  };

  // Set initial state based on current theme
  useEffect(() => {
    setEmailNotifications(true); // Set your preferred default
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          <span className="ml-3 text-gray-400">Loading settings...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    router.push('/signin');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-4">
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-500 bg-clip-text text-transparent">
              Account Settings
            </h1>
            <p className="text-gray-400 mt-2">Manage your account preferences</p>
          </div>
          <Button
            onClick={() => router.push('/dashboard')}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white"
          >
            Back to Dashboard
          </Button>
        </div>

        <div className="max-w-2xl mx-auto space-y-8">
          <div className="rounded-2xl border border-purple-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 shadow-xl shadow-purple-500/10">
            <h2 className="text-xl font-bold text-purple-400 mb-6">Account Preferences</h2>

            <div className="space-y-6">
              <div className="flex items-center justify-between py-4 border-b border-gray-700">
                <div>
                  <h3 className="font-medium text-white">Email notifications</h3>
                  <p className="text-sm text-gray-400">Receive updates via email</p>
                </div>
                <button
                  onClick={toggleEmailNotifications}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                    emailNotifications ? 'bg-purple-600' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ease-in-out ${
                      emailNotifications ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between py-4">
                <div>
                  <h3 className="font-medium text-white">Dark mode</h3>
                  <p className="text-sm text-gray-400">Optimize for reduced lighting</p>
                </div>
                <button
                  onClick={toggleDarkMode}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                    theme === 'dark' ? 'bg-purple-600' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ease-in-out ${
                      theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-red-500/30 bg-gradient-to-br from-red-900/10 to-gray-900/50 backdrop-blur-sm p-8 shadow-xl shadow-red-500/10">
            <h2 className="text-xl font-bold text-red-400 mb-6">Danger Zone</h2>

            <div className="flex flex-wrap gap-4">
              <Button
                variant="destructive"
                onClick={handleSignOut}
                className="bg-red-600/80 hover:bg-red-600 text-white"
              >
                Sign Out
              </Button>
              <Button
                variant="outline"
                className="border-red-500 text-red-400 hover:bg-red-500/10"
              >
                Delete Account
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}