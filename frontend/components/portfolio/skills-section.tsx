import { Code, Database, FileCode, LayoutGrid, Server, Workflow } from "lucide-react"

const skills = [
  { name: "Python", icon: <FileCode className="h-8 w-8" /> },
  { name: "Next.js", icon: <Server className="h-8 w-8" /> },
  { name: "React", icon: <Code className="h-8 w-8" /> },
  { name: "PostgreSQL", icon: <Database className="h-8 w-8" /> },
  { name: "Tailwind CSS", icon: <LayoutGrid className="h-8 w-8" /> },
  { name: "Docker", icon: <Workflow className="h-8 w-8" /> },
]

export default function SkillsSection() {
  return (
    <section className="py-16 px-6 bg-gray-50">
      <div className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">My Tech Stack</h2>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {skills.map((skill) => (
            <div
              key={skill.name}
              className="flex flex-col items-center p-6 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="text-indigo-600 mb-3">{skill.icon}</div>
              <span className="font-medium">{skill.name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
