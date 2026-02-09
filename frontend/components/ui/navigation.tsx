'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';

export default function Navigation() {
  const pathname = usePathname();
  const { user, isLoading, signOut } = useAuth();

  const handleSignOut = () => {
    signOut();
  };

  // Check if we're on a public page
  const isPublicPage = pathname === '/' || pathname === '/signin' || pathname === '/signup';

  return (
    <nav className="border-b bg-background">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center space-x-4">
          <Link href="/" className="text-xl font-bold">
            TodoApp
          </Link>

          {!isPublicPage && (
            <div className="flex space-x-2">
              <Link href="/dashboard" className={`px-3 py-2 rounded-md ${pathname === '/dashboard' ? 'bg-muted' : 'hover:bg-muted'}`}>
                Dashboard
              </Link>
              <Link href="/tasks" className={`px-3 py-2 rounded-md ${pathname === '/tasks' ? 'bg-muted' : 'hover:bg-muted'}`}>
                Tasks
              </Link>
              <Link href="/profile" className={`px-3 py-2 rounded-md ${pathname === '/profile' ? 'bg-muted' : 'hover:bg-muted'}`}>
                Profile
              </Link>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {isLoading ? (
            <div>Loading...</div>
          ) : user ? (
            <>
              <span className="hidden sm:inline">Welcome, {user.first_name || user.email}</span>
              <Button variant="outline" size="sm" onClick={handleSignOut}>
                Sign Out
              </Button>
            </>
          ) : (
            <>
              {!isPublicPage && (
                <>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href="/signin">Sign In</Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link href="/signup">Sign Up</Link>
                  </Button>
                </>
              )}
              {isPublicPage && pathname !== '/signup' && (
                <Button size="sm" asChild>
                  <Link href="/signup">Get Started</Link>
                </Button>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}