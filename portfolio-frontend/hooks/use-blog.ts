import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { blogApi, healthApi } from '@/lib/blog-api';
import { queryKeys } from '@/lib/query-client';
import type { Post, PostSummary, Category, Tag, PostListResponse } from '@/lib/blog-api';

// 헬스체크 훅
export function useHealthCheck() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: healthApi.checkHealth,
    staleTime: 30 * 1000, // 30초
  });
}

export function useSystemStatus() {
  return useQuery({
    queryKey: queryKeys.status,
    queryFn: healthApi.checkStatus,
    staleTime: 30 * 1000, // 30초
  });
}

// 카테고리 훅
export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories,
    queryFn: blogApi.getCategories,
    staleTime: 10 * 60 * 1000, // 10분 (카테고리는 자주 변경되지 않음)
  });
}

// 태그 훅
export function useTags() {
  return useQuery({
    queryKey: queryKeys.tags,
    queryFn: blogApi.getTags,
    staleTime: 10 * 60 * 1000, // 10분
  });
}

// 게시글 목록 훅
export function usePosts(params?: {
  page?: number;
  size?: number;
  post_type?: 'DEV' | 'ESG';
  category_id?: number;
  search?: string;
}) {
  return useQuery({
    queryKey: queryKeys.posts(params),
    queryFn: () => blogApi.getPosts(params),
    staleTime: 2 * 60 * 1000, // 2분
  });
}

// 개별 게시글 훅 (slug 기반)
export function usePost(slug: string) {
  return useQuery({
    queryKey: queryKeys.post(slug),
    queryFn: () => blogApi.getPostBySlug(slug),
    enabled: !!slug, // slug가 있을 때만 실행
    staleTime: 5 * 60 * 1000, // 5분
  });
}

// 개별 게시글 훅 (ID 기반)
export function usePostById(id: number) {
  return useQuery({
    queryKey: queryKeys.postById(id),
    queryFn: () => blogApi.getPostById(id),
    enabled: !!id && id > 0, // 유효한 ID일 때만 실행
    staleTime: 5 * 60 * 1000, // 5분
  });
}

// 댓글 목록 훅
export function useComments(postId: number, approvedOnly = true) {
  return useQuery({
    queryKey: queryKeys.comments(postId),
    queryFn: () => blogApi.getPostComments(postId, approvedOnly),
    enabled: !!postId && postId > 0,
    staleTime: 1 * 60 * 1000, // 1분 (댓글은 자주 업데이트될 수 있음)
  });
}

// 댓글 작성 훅
export function useCreateComment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: blogApi.createComment,
    onSuccess: (data) => {
      // 댓글 목록 캐시 무효화
      queryClient.invalidateQueries({
        queryKey: queryKeys.comments(data.post_id),
      });
    },
  });
}

// 편의 훅들
export function useDevPosts(params?: { page?: number; size?: number; search?: string }) {
  return usePosts({ ...params, post_type: 'DEV' });
}

export function useESGPosts(params?: { page?: number; size?: number; search?: string }) {
  return usePosts({ ...params, post_type: 'ESG' });
}

export function usePostsByCategory(categoryId: number, params?: { page?: number; size?: number }) {
  return usePosts({ ...params, category_id: categoryId });
} 