"use client"

import { useState, use } from "react"
import Image from "next/image"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import RootLayout from "@/components/layout/root-layout"
import LevelSwitcher, { type LevelType } from "@/components/blog/level-switcher"
import { CodeBlock } from "@/components/ui/code-block"
import RelatedPosts from "@/components/blog/related-posts"
import { formatDate } from "@/lib/utils"
import { usePost, usePosts } from "@/hooks/use-blog"
import { Button } from "@/components/ui/button"

// 예시 블로그 포스트 데이터
const postData = {
  title: "Next.js 앱 라우터 완벽 가이드",
  date: "2024-05-15",
  author: "YourName",
  imageUrl: "/placeholder.svg?height=600&width=1200",
  content: {
    beginner: {
      sections: [
        {
          title: "앱 라우터란 무엇인가요?",
          content:
            "Next.js 13에서 도입된 앱 라우터(App Router)는 기존의 페이지 라우터(Pages Router)를 대체하는 새로운 라우팅 시스템입니다. 앱 라우터는 React 서버 컴포넌트를 기반으로 하며, 더 직관적인 파일 시스템 기반 라우팅을 제공합니다.",
          code: {
            language: "jsx",
            content: `// app/page.js - 홈페이지
export default function Home() {
  return <h1>Welcome to my website!</h1>
}

// app/about/page.js - 소개 페이지
export default function About() {
  return <h1>About Us</h1>
}`,
          },
        },
        {
          title: "기본 구조 이해하기",
          content:
            "앱 라우터에서는 app 디렉토리 내의 폴더 구조가 URL 경로와 직접 매핑됩니다. 각 경로 세그먼트에 해당하는 폴더 안에 page.js 파일을 생성하면 해당 경로에 접근할 수 있는 페이지가 만들어집니다.",
        },
      ],
    },
    intermediate: {
      sections: [
        {
          title: "레이아웃과 템플릿 활용하기",
          content:
            "앱 라우터에서는 layout.js 파일을 사용하여 여러 페이지에서 공유되는 UI를 정의할 수 있습니다. 레이아웃은 자식 컴포넌트를 감싸며, 페이지 간 이동 시에도 상태를 유지합니다.",
          code: {
            language: "jsx",
            content: `// app/layout.js
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <header>My Website</header>
        <main>{children}</main>
        <footer>© 2024</footer>
      </body>
    </html>
  )
}`,
          },
        },
        {
          title: "데이터 페칭 전략",
          content:
            "앱 라우터에서는 서버 컴포넌트를 활용하여 컴포넌트 레벨에서 직접 데이터를 가져올 수 있습니다. fetch API를 사용한 데이터 페칭은 기본적으로 자동 중복 제거(deduplication)와 캐싱 기능을 제공합니다.",
          code: {
            language: "jsx",
            content: `// app/users/page.js
async function getUsers() {
  const res = await fetch('https://api.example.com/users')
  return res.json()
}

export default async function UsersPage() {
  const users = await getUsers()
  
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}`,
          },
        },
      ],
    },
    advanced: {
      sections: [
        {
          title: "병렬 라우트와 인터셉트 라우트",
          content:
            "앱 라우터는 병렬 라우트(@folder)와 인터셉트 라우트((.)folder)를 통해 복잡한 UI 패턴을 구현할 수 있습니다. 이를 활용하면 모달, 탭, 분할 뷰 등의 고급 UI 패턴을 쉽게 구현할 수 있습니다.",
          code: {
            language: "jsx",
            content: `// app/@dashboard/analytics/page.js
export default function AnalyticsPage() {
  return <div>Analytics Content</div>
}

// app/@dashboard/settings/page.js
export default function SettingsPage() {
  return <div>Settings Content</div>
}

// app/layout.js
export default function Layout({ children, dashboard }) {
  return (
    <div className="flex">
      <div className="w-1/2">{children}</div>
      <div className="w-1/2">{dashboard}</div>
    </div>
  )
}`,
          },
        },
        {
          title: "서버 액션과 폼 처리",
          content:
            "서버 액션(Server Actions)은 앱 라우터에서 제공하는 강력한 기능으로, 클라이언트에서 서버 함수를 직접 호출할 수 있게 해줍니다. 이를 통해 폼 제출, 데이터 변경 등의 작업을 더 효율적으로 처리할 수 있습니다.",
          code: {
            language: "jsx",
            content: `// app/actions.js
'use server'

export async function createTodo(formData) {
  const title = formData.get('title')
  
  // 데이터베이스에 저장
  await db.todos.create({ title })
  
  // 캐시 무효화
  revalidatePath('/todos')
}

// app/todos/page.js
import { createTodo } from '../actions'

export default function TodosPage() {
  return (
    <form action={createTodo}>
      <input name="title" placeholder="New todo" />
      <button type="submit">Add Todo</button>
    </form>
  )
}`,
          },
        },
      ],
    },
  },
  relatedPosts: [
    { title: "React 서버 컴포넌트 심층 분석", slug: "react-server-components" },
    { title: "Next.js 미들웨어 활용 가이드", slug: "nextjs-middleware-guide" },
    { title: "Next.js 성능 최적화 전략", slug: "nextjs-performance-optimization" },
  ],
}

interface BlogPostPageProps {
  params: Promise<{ slug: string }>
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const [currentLevel, setCurrentLevel] = useState<LevelType>("intermediate")
  const { slug } = use(params)

  const handleLevelChange = (level: LevelType) => {
    setCurrentLevel(level)
  }

  // API 호출
  const { data: post, isLoading, error } = usePost(slug)
  const { data: relatedPostsData } = usePosts({ 
    size: 3,
    post_type: post?.post_type 
  })

  // 로딩 상태
  if (isLoading) {
    return (
      <RootLayout>
        <div className="container mx-auto py-12 px-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-8"></div>
            <div className="h-64 bg-gray-200 rounded mb-8"></div>
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6"></div>
            </div>
          </div>
        </div>
      </RootLayout>
    )
  }

  // 에러 상태
  if (error) {
    return (
      <RootLayout>
        <div className="container mx-auto py-12 px-6">
          <Link href="/blog" className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-8">
            <ArrowLeft className="mr-2 h-4 w-4" />
            모든 글 보기
          </Link>
          <div className="text-center py-12">
            <p className="text-red-600 mb-4">게시글을 불러오는 중 오류가 발생했습니다.</p>
            <Button onClick={() => window.location.reload()}>다시 시도</Button>
          </div>
        </div>
      </RootLayout>
    )
  }

  // 게시글이 없는 경우
  if (!post) {
    return (
      <RootLayout>
        <div className="container mx-auto py-12 px-6">
          <Link href="/blog" className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-8">
            <ArrowLeft className="mr-2 h-4 w-4" />
            모든 글 보기
          </Link>
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">게시글을 찾을 수 없습니다.</p>
            <Button onClick={() => window.location.href = '/blog'}>블로그로 돌아가기</Button>
          </div>
        </div>
      </RootLayout>
    )
  }

  // 관련 포스트 (현재 포스트 제외)
  const relatedPosts = relatedPostsData?.posts
    ?.filter(relatedPost => relatedPost.slug !== slug)
    ?.slice(0, 3)
    ?.map(relatedPost => ({
      title: relatedPost.title,
      slug: relatedPost.slug
    })) || []

  // 현재는 하드코딩된 content 구조를 사용하지만, 추후 CMS나 마크다운 파싱으로 교체 가능
  const currentContent = postData.content[currentLevel]

  return (
    <RootLayout>
      <div className="container mx-auto py-12 px-6">
        <Link href="/blog" className="inline-flex items-center text-indigo-600 hover:text-indigo-800 mb-8">
          <ArrowLeft className="mr-2 h-4 w-4" />
          모든 글 보기
        </Link>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* 왼쪽 사이드바 (Sticky) */}
          <div className="w-full lg:w-1/4">
            <div className="lg:sticky lg:top-24 bg-white p-6 rounded-lg shadow-sm">
              <LevelSwitcher onLevelChange={handleLevelChange} currentLevel={currentLevel} />
            </div>
          </div>

          {/* 메인 콘텐츠 */}
          <div className="w-full lg:w-3/4">
            <article>
              <h1 className="text-3xl md:text-4xl font-bold mb-4">{post.title}</h1>

              <div className="flex items-center text-gray-500 mb-8">
                <time dateTime={post.created_at}>{formatDate(post.created_at.split('T')[0])}</time>
                <span className="mx-2">•</span>
                <span className={`px-2 py-1 rounded text-xs ${
                  post.post_type === 'DEV' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                }`}>
                  {post.post_type}
                </span>
                {post.category && (
                  <>
                    <span className="mx-2">•</span>
                    <span>{post.category.name}</span>
                  </>
                )}
              </div>

              {/* 태그 */}
              {post.tags && post.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-8">
                  {post.tags.map((tag) => (
                    <span key={tag.id} className="bg-gray-200 px-3 py-1 rounded-full text-sm">
                      #{tag.name}
                    </span>
                  ))}
                </div>
              )}

              {/* 플레이스홀더 이미지 */}
              <div className="relative w-full h-[300px] md:h-[400px] mb-8 rounded-lg overflow-hidden">
                <Image
                  src="/placeholder.svg?height=400&width=800"
                  alt={post.title}
                  fill
                  className="object-cover"
                />
              </div>

              {/* 메인 콘텐츠 */}
              <div className="prose prose-lg max-w-none">
                {/* 현재는 하드코딩된 레벨 시스템을 유지하지만, 실제 content를 함께 표시 */}
                <div className="mb-8 p-6 bg-blue-50 rounded-lg">
                  <h2 className="text-2xl font-semibold mb-4">게시글 내용</h2>
                  <div className="whitespace-pre-wrap">{post.content}</div>
                </div>

                {/* 기존 레벨별 콘텐츠도 유지 (데모용) */}
                {currentContent.sections.map((section, index) => (
                  <div key={index} className="mb-8 p-4 border-l-4 border-gray-200">
                    {section.title && <h3 className="text-xl font-semibold mb-4 text-gray-600">[데모] {section.title}</h3>}
                    <p className="mb-4 text-gray-500">{section.content}</p>
                    {section.code && (
                      <CodeBlock language={section.code.language} code={section.code.content} className="my-6" />
                    )}
                  </div>
                ))}
              </div>

              <RelatedPosts posts={relatedPosts} />
            </article>
          </div>
        </div>
      </div>
    </RootLayout>
  )
}
