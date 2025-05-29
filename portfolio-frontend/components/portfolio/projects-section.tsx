import ProjectCard from "./project-card"

// 예시 프로젝트 데이터
const projects = [
  {
    title: "개인 포트폴리오 웹사이트",
    description: "Next.js와 Tailwind CSS를 활용한 반응형 포트폴리오 웹사이트입니다.",
    imageUrl: "/placeholder.svg?height=300&width=600",
    tags: ["Next.js", "Tailwind", "React"],
    slug: "portfolio-website",
  },
  {
    title: "실시간 채팅 애플리케이션",
    description: "Socket.io와 React를 활용한 실시간 채팅 애플리케이션입니다.",
    imageUrl: "/placeholder.svg?height=300&width=600",
    tags: ["React", "Socket.io", "Express"],
    slug: "chat-application",
  },
  {
    title: "데이터 시각화 대시보드",
    description: "D3.js와 React를 활용한 데이터 시각화 대시보드입니다.",
    imageUrl: "/placeholder.svg?height=300&width=600",
    tags: ["React", "D3.js", "API"],
    slug: "data-dashboard",
  },
  {
    title: "AI 기반 이미지 분석 도구",
    description: "Python과 TensorFlow를 활용한 이미지 분석 웹 애플리케이션입니다.",
    imageUrl: "/placeholder.svg?height=300&width=600",
    tags: ["Python", "TensorFlow", "Flask"],
    slug: "image-analysis",
  },
]

export default function ProjectsSection() {
  return (
    <section className="py-16 px-6 bg-white">
      <div className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">Projects</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects.map((project) => (
            <ProjectCard key={project.slug} {...project} />
          ))}
        </div>
      </div>
    </section>
  )
}
