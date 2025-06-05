import { useState, useEffect } from 'react';
import { blogApi, healthApi } from '@/lib/blog-api';
import type { PostSummary, Category, PostListResponse, Post } from '@/lib/blog-api';

// 간단한 API 호출 훅 (React Query 없이)
export function usePosts(params?: {
  page?: number;
  size?: number;
  post_type?: 'DEV' | 'ESG';
  category_id?: number;
  search?: string;
}) {
  const [data, setData] = useState<PostListResponse | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const result = await blogApi.getPosts(params);
        setData(result);
      } catch (err) {
        setError(err as Error);
        console.error('API 호출 오류:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPosts();
  }, [params?.page, params?.size, params?.post_type, params?.category_id, params?.search]);

  return { data, isLoading, error };
}

export function useCategories() {
  const [data, setData] = useState<Category[] | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const result = await blogApi.getCategories();
        setData(result);
      } catch (err) {
        setError(err as Error);
        console.error('카테고리 API 호출 오류:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { data, isLoading, error };
}

// 개별 포스트 조회 훅 추가
export function usePost(slug: string) {
  const [data, setData] = useState<Post | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!slug) return;

    const fetchPost = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const result = await blogApi.getPostBySlug(slug);
        setData(result);
      } catch (err) {
        setError(err as Error);
        console.error('포스트 API 호출 오류:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPost();
  }, [slug]);

  return { data, isLoading, error };
}

// 헬스체크 훅들 추가
export function useHealthCheck() {
  const [data, setData] = useState<any | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const result = await healthApi.checkHealth();
        setData(result);
      } catch (err) {
        setError(err as Error);
        console.error('헬스체크 API 호출 오류:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHealth();
  }, []);

  return { data, isLoading, error };
}

export function useSystemStatus() {
  const [data, setData] = useState<any | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const result = await healthApi.checkStatus();
        setData(result);
      } catch (err) {
        setError(err as Error);
        console.error('시스템 상태 API 호출 오류:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
  }, []);

  return { data, isLoading, error };
} 