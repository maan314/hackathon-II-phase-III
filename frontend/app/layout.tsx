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
            </AuthProvider>
          </ThemeProvider>
        </ActivityProvider>
      </body>
    </html>
  )
}
