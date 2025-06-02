'use client';

import { useHealthCheck, useSystemStatus, useCategories, usePosts } from '@/hooks/use-blog';
import { useState } from 'react';

export default function TestPage() {
  const [showDetails, setShowDetails] = useState(false);
  
  const healthQuery = useHealthCheck();
  const statusQuery = useSystemStatus();
  const categoriesQuery = useCategories();
  const postsQuery = usePosts({ page: 1, size: 5 });

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8">API 연동 테스트</h1>
      
      {/* 헬스체크 */}
      <div className="mb-8 p-6 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">🏥 헬스체크</h2>
        {healthQuery.isLoading && <p className="text-blue-600">로딩 중...</p>}
        {healthQuery.error && (
          <p className="text-red-600">
            오류: {healthQuery.error instanceof Error ? healthQuery.error.message : '알 수 없는 오류'}
          </p>
        )}
        {healthQuery.data && (
          <div className="bg-green-100 p-4 rounded">
            <p>✅ 상태: {healthQuery.data.status}</p>
            <p>🏷️ 서비스: {healthQuery.data.service}</p>
            <p>📦 버전: {healthQuery.data.version}</p>
          </div>
        )}
      </div>

      {/* 시스템 상태 */}
      <div className="mb-8 p-6 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">🚀 시스템 상태</h2>
        {statusQuery.isLoading && <p className="text-blue-600">로딩 중...</p>}
        {statusQuery.error && (
          <p className="text-red-600">
            오류: {statusQuery.error instanceof Error ? statusQuery.error.message : '알 수 없는 오류'}
          </p>
        )}
        {statusQuery.data && (
          <div className="space-y-2">
            <p>🛡️ Gateway: <span className="font-semibold">{statusQuery.data.gateway}</span></p>
            <div className="mt-4">
              <h3 className="font-semibold mb-2">서비스 상태:</h3>
              {Object.entries(statusQuery.data.services).map(([service, info]) => (
                <div key={service} className="flex items-center space-x-2 ml-4">
                  <span className={`w-2 h-2 rounded-full ${
                    info.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  <span>{service}: {info.status}</span>
                  {info.status_code && <span className="text-gray-500">({info.status_code})</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 카테고리 */}
      <div className="mb-8 p-6 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">📁 카테고리</h2>
        {categoriesQuery.isLoading && <p className="text-blue-600">로딩 중...</p>}
        {categoriesQuery.error && (
          <p className="text-red-600">
            오류: {categoriesQuery.error instanceof Error ? categoriesQuery.error.message : '알 수 없는 오류'}
          </p>
        )}
        {categoriesQuery.data && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categoriesQuery.data.map((category) => (
              <div key={category.id} className="bg-blue-50 p-4 rounded">
                <h3 className="font-semibold">{category.name}</h3>
                <p className="text-sm text-gray-600">{category.slug}</p>
                {category.description && (
                  <p className="text-sm mt-2">{category.description}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 게시글 목록 */}
      <div className="mb-8 p-6 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">📝 게시글 목록 (최근 5개)</h2>
        {postsQuery.isLoading && <p className="text-blue-600">로딩 중...</p>}
        {postsQuery.error && (
          <p className="text-red-600">
            오류: {postsQuery.error instanceof Error ? postsQuery.error.message : '알 수 없는 오류'}
          </p>
        )}
        {postsQuery.data && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              총 {postsQuery.data.total}개 게시글 중 {postsQuery.data.posts.length}개 표시
            </div>
            {postsQuery.data.posts.map((post) => (
              <div key={post.id} className="bg-gray-50 p-4 rounded">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold">{post.title}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    post.post_type === 'DEV' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {post.post_type}
                  </span>
                </div>
                {post.summary && <p className="text-sm text-gray-600 mb-2">{post.summary}</p>}
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>👁️ {post.view_count}</span>
                  <span>📅 {new Date(post.created_at).toLocaleDateString()}</span>
                  {post.category && <span>📁 {post.category.name}</span>}
                </div>
                {post.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {post.tags.map((tag) => (
                      <span key={tag.id} className="bg-gray-200 px-2 py-1 rounded text-xs">
                        #{tag.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 상세 정보 토글 */}
      <div className="text-center">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          {showDetails ? '상세 정보 숨기기' : '상세 정보 보기'}
        </button>
        
        {showDetails && (
          <div className="mt-4 p-4 bg-gray-100 rounded text-left">
            <h3 className="font-semibold mb-2">API 설정 정보:</h3>
            <p>API URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}</p>
            <p>현재 환경: {process.env.NODE_ENV}</p>
          </div>
        )}
      </div>
    </div>
  );
} 