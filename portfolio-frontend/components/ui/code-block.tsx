"use client"

import { Copy } from "lucide-react"
import { cn } from "@/lib/utils"

interface CodeBlockProps {
  language?: string
  code: string
  className?: string
}

export function CodeBlock({ language, code, className }: CodeBlockProps) {
  return (
    <div className={cn("relative rounded-lg overflow-hidden", className)}>
      {language && <div className="absolute top-2 left-4 text-xs text-gray-400">{language}</div>}
      <button
        className="absolute top-2 right-2 p-1.5 rounded-md bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white transition-colors"
        onClick={() => navigator.clipboard.writeText(code)}
        aria-label="Copy code"
      >
        <Copy size={16} />
      </button>
      <pre className="bg-gray-800 text-gray-100 p-4 pt-10 overflow-x-auto font-mono text-sm">
        <code>{code}</code>
      </pre>
    </div>
  )
}
