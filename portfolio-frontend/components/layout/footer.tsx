import type React from "react"
import Link from "next/link"
import { Github, Linkedin, Mail } from "lucide-react"

export default function Footer() {
  return (
    <footer className="w-full bg-white py-6 px-6 border-t border-gray-100">
      <div className="container mx-auto flex flex-col md:flex-row justify-between items-center">
        <div className="text-sm text-gray-600 mb-4 md:mb-0">
          © {new Date().getFullYear()} YourName. All Rights Reserved.
        </div>

        <div className="flex items-center space-x-6">
          <SocialLink href="https://github.com/yourusername" icon={<Github size={20} />} label="GitHub" />
          <SocialLink href="https://linkedin.com/in/yourusername" icon={<Linkedin size={20} />} label="LinkedIn" />
          <SocialLink href="mailto:your.email@example.com" icon={<Mail size={20} />} label="Email" />
        </div>
      </div>
    </footer>
  )
}

function SocialLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link href={href} className="text-gray-600 hover:text-indigo-600 transition-colors" aria-label={label}>
      {icon}
    </Link>
  )
}
