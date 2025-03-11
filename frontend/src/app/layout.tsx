import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Quiz Dashboard',
  description: 'Manage your quiz sets',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <header className="bg-blue-600 text-white p-4">
          <h1 className="text-2xl font-bold">Quiz Dashboard</h1>
        </header>
        <main className="container mx-auto p-4">
          {children}
        </main>
      </body>
    </html>
  )
}
