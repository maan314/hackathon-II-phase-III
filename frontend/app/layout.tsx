import './globals.css';
import { AuthProvider } from '@/lib/auth-context';
import { ThemeProvider } from '@/lib/theme-context';
import { ActivityProvider } from '@/lib/activity-context';

export const metadata = {
  title: 'Todo Management App',
  description: 'Manage your tasks efficiently with our intuitive todo application',
  icons: {
    icon: '/icon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <ActivityProvider>
          <ThemeProvider>
            <AuthProvider>
              <main>{children}</main>
              <footer className="w-full py-4 text-center text-sm text-gray-500 border-t border-gray-800">
                <p>
                  Created by{' '}
                  <span className="bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent font-semibold">
                    Muhammad Usman
                  </span>
                  {' '}&copy; 2026
                </p>
              </footer>
            </AuthProvider>
          </ThemeProvider>
        </ActivityProvider>
      </body>
    </html>
  )
}
