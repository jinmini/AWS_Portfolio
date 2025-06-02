"use client"
import { BookOpen, Lightbulb, Zap } from "lucide-react"
import { cn } from "@/lib/utils"

export type LevelType = "beginner" | "intermediate" | "advanced"

interface LevelSwitcherProps {
  onLevelChange: (level: LevelType) => void
  currentLevel: LevelType
}

export default function LevelSwitcher({ onLevelChange, currentLevel }: LevelSwitcherProps) {
  const levels = [
    { id: "beginner", label: "초급", icon: <BookOpen className="h-5 w-5" /> },
    { id: "intermediate", label: "중급", icon: <Lightbulb className="h-5 w-5" /> },
    { id: "advanced", label: "고급", icon: <Zap className="h-5 w-5" /> },
  ]

  return (
    <div className="flex flex-col space-y-2">
      <h3 className="text-sm font-medium text-gray-500 mb-2">학습 수준</h3>

      {levels.map((level) => (
        <button
          key={level.id}
          className={cn(
            "flex items-center px-4 py-3 rounded-md transition-colors",
            currentLevel === level.id ? "bg-indigo-600 text-white" : "text-gray-700 hover:bg-gray-100",
          )}
          onClick={() => onLevelChange(level.id as LevelType)}
        >
          <span className="mr-3">{level.icon}</span>
          <span>{level.label}</span>
        </button>
      ))}
    </div>
  )
}
