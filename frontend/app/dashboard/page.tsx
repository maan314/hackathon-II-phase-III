'use client';

import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useActivity } from '@/lib/activity-context';

export default function DashboardPage() {
  const { user, isLoading, signOut } = useAuth();
  const { activities } = useActivity();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="container mx-auto flex min-h-[calc(100vh-4rem)] items-center justify-center py-10">
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (!user) {
    router.push('/signin');
    return null;
  }

  const handleSignOut = () => {
    signOut();
    router.push('/signin');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Dashboard
            </h1>
            <p className="text-gray-400 mt-2">Welcome back, {user?.first_name || user?.email?.split('@')[0]}!</p>
          </div>
          <Button
            onClick={handleSignOut}
            variant="outline"
            className="border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-gray-900 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/50"
          >
            Sign Out
          </Button>
        </div>

        <div className="grid gap-8 md:grid-cols-2 mb-10">
          <div className="rounded-xl border border-cyan-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 shadow-xl shadow-cyan-500/10">
            <div className="flex items-center space-x-4 mb-6">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center">
                <span className="text-lg font-bold">{(user?.first_name || user?.email?.charAt(0) || 'U').toUpperCase()}</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold">{user?.first_name || user?.email?.split('@')[0]}</h2>
                <p className="text-cyan-400">{user?.email}</p>
              </div>
            </div>
            <p className="text-gray-300">Ready to manage your tasks and boost productivity?</p>
          </div>

          <div className="rounded-xl border border-purple-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 shadow-xl shadow-purple-500/10">
            <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              Quick Actions
            </h2>
            <div className="grid grid-cols-1 gap-3">
              <Link
                href="/chat"
                className="px-4 py-3 rounded-lg border border-purple-500/30 bg-gradient-to-r from-purple-500/5 to-pink-500/5 hover:from-purple-500/10 hover:to-pink-500/10 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20 text-purple-300"
              >
                <span className="font-medium">💬 Chat with AI Assistant</span>
              </Link>
              <Link
                href="/tasks"
                className="px-4 py-3 rounded-lg border border-cyan-500/30 bg-cyan-500/5 hover:bg-cyan-500/10 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/20 text-cyan-300"
              >
                <span className="font-medium">Manage Tasks</span>
              </Link>
              <Link
                href="/profile"
                className="px-4 py-3 rounded-lg border border-purple-500/30 bg-purple-500/5 hover:bg-purple-500/10 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20 text-purple-300"
              >
                <span className="font-medium">Profile Settings</span>
              </Link>
              <Link
                href="/settings"
                className="px-4 py-3 rounded-lg border border-pink-500/30 bg-pink-500/5 hover:bg-pink-500/10 transition-all duration-300 hover:shadow-lg hover:shadow-pink-500/20 text-pink-300"
              >
                <span className="font-medium">Account Settings</span>
              </Link>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-green-500/30 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm p-8 shadow-xl shadow-green-500/10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
              Recent Activity
            </h2>
            <span className="text-sm text-gray-400">{activities.length} items</span>
          </div>

          {activities.length > 0 ? (
            <div className="space-y-4">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-gray-700 bg-gray-800/30 hover:bg-gray-800/50 transition-all duration-300"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-3 h-3 rounded-full ${
                      activity.type.includes('task') ? 'bg-cyan-500 animate-pulse' :
                      activity.type.includes('profile') ? 'bg-purple-500 animate-pulse' :
                      'bg-green-500 animate-pulse'
                    }`}></div>
                    <span className="font-medium">{activity.action}</span>
                  </div>
                  <span className="text-sm text-gray-400">{activity.timestamp}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">No recent activity to display. Start by creating your first task!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}