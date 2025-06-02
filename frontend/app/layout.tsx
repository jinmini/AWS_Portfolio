import type { Metadata } from 'next'
import './globals.css'
import QueryProvider from '@/components/providers/query-provider'

export const metadata: Metadata = {
  title: 'Jinmini Portfolio',
  description: 'Developer & ESG Consultant Portfolio',
  generator: 'Next.js',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko">
      <body>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  )
}
