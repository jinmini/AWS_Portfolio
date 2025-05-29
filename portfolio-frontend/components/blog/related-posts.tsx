import Link from "next/link"

interface RelatedPost {
  title: string
  slug: string
}

interface RelatedPostsProps {
  posts: RelatedPost[]
}

export default function RelatedPosts({ posts }: RelatedPostsProps) {
  if (posts.length === 0) return null

  return (
    <div className="border-t border-gray-200 pt-8 mt-12">
      <h3 className="text-xl font-semibold mb-4">함께 읽으면 좋은 글</h3>
      <ul className="space-y-3">
        {posts.map((post) => (
          <li key={post.slug}>
            <Link href={`/blog/${post.slug}`} className="text-indigo-600 hover:text-indigo-800 hover:underline">
              {post.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
