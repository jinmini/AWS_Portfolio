/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Docker 빌드 최적화
  experimental: {
    esmExternals: false,
  },
  // standalone 모드 제거 (Windows symlink 문제 해결)
  // output: 'standalone',
}

export default nextConfig