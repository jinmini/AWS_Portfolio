"use client"

import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, ExternalLink, Github } from "lucide-react"
import RootLayout from "@/components/layout/root-layout"
import { Button } from "@/components/ui/button"
import { Tag } from "@/components/ui/tag"

// 예시 프로젝트 데이터 (실제로는 데이터베이스나 CMS에서 가져올 것입니다)
const projectData = {
  title: "개인 포트폴리오 웹사이트",
  imageUrl: "/placeholder.svg?height=600&width=1200",
  overview:
    "이 프로젝트는 Next.js와 Tailwind CSS를 활용하여 개발한 개인 포트폴리오 웹사이트입니다. 반응형 디자인과 모던한 UI/UX를 구현하였습니다.",
  role: "이 프로젝트에서 저는 디자인부터 개발, 배포까지 전 과정을 담당했습니다. UI/UX 디자인, 프론트엔드 개발, 백엔드 API 구현, 그리고 Vercel을 통한 배포를 진행했습니다.",
  challenges:
    "가장 큰 도전 과제는 다양한 화면 크기에서 최적의 사용자 경험을 제공하는 것이었습니다. 이를 해결하기 위해 Tailwind CSS의 반응형 유틸리티를 활용하고, 컴포넌트 단위로 모듈화하여 개발했습니다.",
  results:
    "이 프로젝트를 통해 웹 개발 기술을 향상시키고, 포트폴리오를 효과적으로 전시할 수 있게 되었습니다. 또한, 이 웹사이트는 Google 검색 결과 상위에 노출되어 더 많은 기회를 얻을 수 있었습니다.",
  techStack: ["Next.js", "React", "Tailwind CSS", "TypeScript", "Vercel"],
  demoUrl: "https://example.com",
  githubUrl: "https://github.com/yourusername/portfolio",
}

export default function ProjectDetailPage() {
  return (
    <RootLayout>
      <div className="container mx-auto py-12 px-6">
        <Link href="/portfolio" className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-8">
          <ArrowLeft className="mr-2 h-4 w-4" />
          모든 프로젝트 보기
        </Link>

        <h1 className="text-3xl md:text-4xl font-bold mb-8">{projectData.title}</h1>

        <div className="relative w-full h-[300px] md:h-[500px] mb-12 rounded-lg overflow-hidden">
          <Image
            src={projectData.imageUrl || "/placeholder.svg"}
            alt={projectData.title}
            fill
            className="object-cover"
          />
        </div>

        <div className="flex flex-col lg:flex-row gap-12">
          <div className="w-full lg:w-2/3 space-y-8">
            <section>
              <h2 className="text-2xl font-semibold mb-4">프로젝트 개요</h2>
              <p className="text-gray-700">{projectData.overview}</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">나의 역할</h2>
              <p className="text-gray-700">{projectData.role}</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">도전 과제 및 해결 방법</h2>
              <p className="text-gray-700">{projectData.challenges}</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">결과 및 성과</h2>
              <p className="text-gray-700">{projectData.results}</p>
            </section>
          </div>

          <div className="w-full lg:w-1/3 space-y-8">
            <section className="bg-gray-50 p-6 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">기술 스택</h2>
              <div className="flex flex-wrap gap-2">
                {projectData.techStack.map((tech) => (
                  <Tag key={tech}>{tech}</Tag>
                ))}
              </div>
            </section>

            <section className="space-y-4">
              {projectData.demoUrl && (
                <Button variant="primary" className="w-full" onClick={() => window.open(projectData.demoUrl, "_blank")}>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  라이브 데모 보기
                </Button>
              )}

              {projectData.githubUrl && (
                <Button
                  variant="secondary"
                  className="w-full"
                  onClick={() => window.open(projectData.githubUrl, "_blank")}
                >
                  <Github className="mr-2 h-4 w-4" />
                  GitHub에서 보기
                </Button>
              )}
            </section>
          </div>
        </div>
      </div>
    </RootLayout>
  )
}
