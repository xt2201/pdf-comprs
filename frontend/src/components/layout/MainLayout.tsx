import { Header } from './Header'
import { Footer } from './Footer'
import { Background3D } from '@/components/three/Background3D'

interface MainLayoutProps {
  children: React.ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="relative flex min-h-screen flex-col">
      {/* 3D Background */}
      <Background3D />
      
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      <main className="flex-1">
        <div className="container mx-auto px-4 py-8">
          {children}
        </div>
      </main>
      
      {/* Footer */}
      <Footer />
    </div>
  )
}
