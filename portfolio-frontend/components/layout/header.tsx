"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu } from "lucide-react"

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full bg-white shadow-sm py-4 px-6">
      <div className="container mx-auto flex items-center justify-between">
        <Link href="/" className="text-xl font-bold">
          Dev. <span className="text-indigo-600">YourName</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          <NavLink href="/portfolio" label="Portfolio" />
          <NavLink href="/blog" label="Blog" />
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-gray-700 hover:text-indigo-600 transition-colors"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <Menu size={24} />
        </button>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden container mx-auto mt-2 pb-4">
          <nav className="flex flex-col space-y-4">
            <NavLink href="/portfolio" label="Portfolio" />
            <NavLink href="/blog" label="Blog" />
          </nav>
        </div>
      )}
    </header>
  )
}

function NavLink({ href, label }: { href: string; label: string }) {
  // In a real app, you would check if the current path matches href
  const isActive = false

  return (
    <Link
      href={href}
      className={`font-medium transition-colors ${
        isActive ? "text-indigo-600 border-b-2 border-indigo-600" : "text-gray-700 hover:text-indigo-600"
      }`}
    >
      {label}
    </Link>
  )
}
