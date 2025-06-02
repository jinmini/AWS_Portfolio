import Image from "next/image"
import Link from "next/link"
import { Tag } from "../ui/tag"
import { formatDate } from "@/lib/utils"

interface PostCardProps {
  title: string
  excerpt: string
  imageUrl?: string
  date: string
  tags: string[]
  slug: string
}

export default function PostCard({ title, excerpt, imageUrl, date, tags, slug }: PostCardProps) {
  return (
    <Link href={`/blog/${slug}`} className="block group">
      <article className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
        {imageUrl && (
          <div className="relative h-48 w-full">
            <Image src={imageUrl || "/placeholder.svg"} alt={title} fill className="object-cover" />
          </div>
        )}

        <div className="p-6">
          <div className="flex items-center text-sm text-gray-500 mb-3">
            <time dateTime={date}>{formatDate(date)}</time>
            {tags.length > 0 && (
              <>
                <span className="mx-2">•</span>
                <Tag>{tags[0]}</Tag>
              </>
            )}
          </div>

          <h3 className="text-xl font-bold mb-2 group-hover:text-indigo-600 transition-colors">{title}</h3>

          <p className="text-gray-600 mb-4 line-clamp-3">{excerpt}</p>

          <div className="text-indigo-600 font-medium group-hover:text-indigo-700">더 보기</div>
        </div>
      </article>
    </Link>
  )
}
