"use client"

import Link from "next/link"
import { Github, Linkedin, Mail } from "lucide-react"
import { Button } from "../ui/button"

export default function ContactSection() {
  return (
    <section className="py-16 px-6 bg-gray-50">
      <div className="container mx-auto max-w-3xl text-center">
        <h2 className="text-3xl font-bold mb-8">Get In Touch</h2>
        <p className="text-lg text-gray-700 mb-8">
          프로젝트 협업, 채용 문의, 또는 그냥 인사하고 싶으시다면 언제든지 연락주세요!
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
          <Button
            variant="primary"
            size="lg"
            onClick={() => (window.location.href = "mailto:your.email@example.com")}
            className="w-full sm:w-auto"
          >
            <Mail className="mr-2 h-5 w-5" />
            이메일 보내기
          </Button>

          <Button
            variant="outline"
            size="lg"
            onClick={() => window.open("https://linkedin.com/in/yourusername", "_blank")}
            className="w-full sm:w-auto"
          >
            <Linkedin className="mr-2 h-5 w-5" />
            LinkedIn 연결하기
          </Button>
        </div>

        <div className="flex justify-center items-center space-x-6">
          <Link
            href="https://github.com/yourusername"
            target="_blank"
            className="text-gray-700 hover:text-indigo-600 transition-colors"
          >
            <Github size={28} />
          </Link>
          <Link
            href="https://linkedin.com/in/yourusername"
            target="_blank"
            className="text-gray-700 hover:text-indigo-600 transition-colors"
          >
            <Linkedin size={28} />
          </Link>
          <Link href="mailto:your.email@example.com" className="text-gray-700 hover:text-indigo-600 transition-colors">
            <Mail size={28} />
          </Link>
        </div>
      </div>
    </section>
  )
}
