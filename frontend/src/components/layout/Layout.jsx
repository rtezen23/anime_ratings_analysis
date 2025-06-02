import React from 'react'
import Header from './Header'
import Footer from './Footer'

const Layout = ({ children }) => (
  <div className="min-h-screen flex flex-col bg-gradient-to-br from-[#1A1A2E] to-[#0F3460]">
    <Header />
    <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-8 py-6">
      {children}
    </main>
    <Footer />
  </div>
)

export default Layout
