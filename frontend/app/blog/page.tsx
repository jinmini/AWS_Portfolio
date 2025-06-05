'use client';

import { useState } from "react"
import RootLayout from "@/components/layout/root-layout"
import PostCard from "@/components/blog/post-card"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, Filter } from "lucide-react"
import { usePosts, useCategories } from "@/hooks/use-blog-simple"
import type { PostSummary } from "@/lib/blog-api"

export default function BlogPage() {
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>()
  const [selectedPostType, setSelectedPostType] = useState<'DEV' | 'ESG' | undefined>()
  
  const postsPerPage = 6
  
  // 디버깅: 환경변수 확인
  console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL)
  console.log('NODE_ENV:', process.env.NODE_ENV)
  
  // API 호출 (새로운 단순한 훅 사용)
  const { data: postsData, isLoading: postsLoading, error: postsError } = usePosts({
    page: currentPage,
    size: postsPerPage,
    category_id: selectedCategory,
    post_type: selectedPostType,
  })
  
  // 디버깅: API 응답 확인
  console.log('postsData:', postsData)
  console.log('postsLoading:', postsLoading)
  console.log('postsError:', postsError)
  
  const { data: categories } = useCategories()

  // 로딩 상태
  if (postsLoading) {
    return (
      <RootLayout>
        <div className="container mx-auto py-12 px-6">
          <h1 className="text-3xl md:text-4xl font-bold mb-8">블로그</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-gray-200 rounded-lg h-48 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </div>
      </RootLayout>
    )
  }

  // 에러 상태
  if (postsError) {
    return (
      <RootLayout>
        <div className="container mx-auto py-12 px-6">
          <h1 className="text-3xl md:text-4xl font-bold mb-8">블로그</h1>
          <div className="text-center py-12">
            <p className="text-red-600 mb-4">게시글을 불러오는 중 오류가 발생했습니다.</p>
            <Button onClick={() => window.location.reload()}>다시 시도</Button>
          </div>
        </div>
      </RootLayout>
    )
  }

  const posts = postsData?.posts || []
  const totalPosts = postsData?.total || 0
  const totalPages = postsData?.pages || 1

  // PostSummary를 PostCard가 기대하는 형식으로 변환
  const transformedPosts = posts.map((post: PostSummary) => ({
    title: post.title,
    excerpt: post.summary || '내용을 확인해보세요.', 
    imageUrl: "/placeholder.svg?height=300&width=600", // 추후 이미지 필드 추가 시 수정
    date: post.created_at.split('T')[0], // ISO 날짜를 YYYY-MM-DD 형식으로 변환
    tags: post.tags.map(tag => tag.name),
    slug: post.slug,
  }))

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleCategoryFilter = (categoryId: number | undefined) => {
    setSelectedCategory(categoryId)
    setCurrentPage(1) // 필터 변경 시 첫 페이지로
  }

  const handlePostTypeFilter = (postType: 'DEV' | 'ESG' | undefined) => {
    setSelectedPostType(postType)
    setCurrentPage(1) // 필터 변경 시 첫 페이지로
  }
  return (
    <RootLayout>
      <div className="container mx-auto py-12 px-6">
        <h1 className="text-3xl md:text-4xl font-bold mb-8">블로그</h1>

        {/* 필터 및 통계 */}
        <div className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="text-gray-600">총 {totalPosts}개의 게시글</div>

          <div className="flex flex-wrap gap-2">
            {/* 포스트 타입 필터 */}
            <Button 
              variant={selectedPostType === undefined ? "primary" : "secondary"} 
              onClick={() => handlePostTypeFilter(undefined)}
              size="sm"
            >
              전체
            </Button>
            <Button 
              variant={selectedPostType === 'DEV' ? "primary" : "secondary"} 
              onClick={() => handlePostTypeFilter('DEV')}
              size="sm"
            >
              개발
            </Button>
            <Button 
              variant={selectedPostType === 'ESG' ? "primary" : "secondary"} 
              onClick={() => handlePostTypeFilter('ESG')}
              size="sm"
            >
              ESG
            </Button>
            
            {/* 카테고리 필터 */}
            {categories && categories.length > 0 && (
              <select 
                value={selectedCategory || ''} 
                onChange={(e) => handleCategoryFilter(e.target.value ? Number(e.target.value) : undefined)}
                className="px-3 py-1 border rounded-md text-sm"
              >
                <option value="">모든 카테고리</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        {/* 게시글 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {transformedPosts.map((post) => (
            <PostCard key={post.slug} {...post} />
          ))}
        </div>

        {/* 게시글이 없는 경우 */}
        {transformedPosts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">게시글이 없습니다.</p>
          </div>
        )}

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className="flex justify-center">
            <nav className="inline-flex rounded-md shadow-sm">
              <Button 
                variant="secondary" 
                className="rounded-l-md rounded-r-none"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  variant={page === currentPage ? "primary" : "secondary"}
                  className="rounded-none border-l-0 border-r-0"
                  onClick={() => handlePageChange(page)}
                >
                  {page}
                </Button>
              ))}
              
              <Button 
                variant="secondary" 
                className="rounded-r-md rounded-l-none"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </nav>
          </div>
        )}
      </div>
    </RootLayout>
  )
}
