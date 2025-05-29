import Image from "next/image"
import Link from "next/link"
import { Tag } from "../ui/tag"

interface ProjectCardProps {
  title: string
  description: string
  imageUrl: string
  tags: string[]
  slug: string
}

export default function ProjectCard({ title, description, imageUrl, tags, slug }: ProjectCardProps) {
  return (
    <Link href={`/portfolio/${slug}`} className="block group">
      <div className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
        <div className="relative h-48 w-full">
          <Image src={imageUrl || "/placeholder.svg"} alt={title} fill className="object-cover" />
        </div>

        <div className="p-6">
          <h3 className="text-xl font-bold mb-2 group-hover:text-indigo-600 transition-colors">{title}</h3>
          <p className="text-gray-600 mb-4 line-clamp-2">{description}</p>

          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <Tag key={tag}>#{tag}</Tag>
            ))}
          </div>
        </div>
      </div>
    </Link>
  )
}
