'use client';

import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export default function ProfilePage() {
  const { user, isLoading, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = () => {
    signOut();
    router.push('/signin');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
          <span className="ml-3 text-gray-400">Loading profile...</span>
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Profile Settings
          </h1>
          <p className="text-gray-400 mt-2">Manage your personal information</p>
        </div>

        <div className="max-w-2xl mx-auto">
          <div className="rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 shadow-xl shadow-cyan-500/10">
            <div className="space-y-8">
              <div>
                <h2 className="text-xl font-bold text-cyan-400 mb-4">Personal Information</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 border-b border-gray-700">
                    <span className="text-gray-400">Full Name</span>
                    <span className="text-white font-medium">{user.first_name} {user.last_name}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-gray-700">
                    <span className="text-gray-400">Email</span>
                    <span className="text-white font-medium">{user.email}</span>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-gray-400">Member Since</span>
                    <span className="text-white font-medium">{new Date(user.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-bold text-cyan-400 mb-4">Account Actions</h2>
                <div className="flex flex-wrap gap-4">
                  <Button
                    onClick={handleSignOut}
                    variant="outline"
                    className="border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-gray-900 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/50"
                  >
                    Sign Out
                  </Button>
                  <Button
                    onClick={() => router.push('/dashboard')}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white"
                  >
                    Back to Dashboard
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}