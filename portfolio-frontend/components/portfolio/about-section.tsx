import Image from "next/image"

export default function AboutSection() {
  return (
    <section className="py-16 px-6 bg-white">
      <div className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">About Me</h2>

        <div className="flex flex-col md:flex-row items-center gap-12">
          <div className="w-full md:w-1/3 flex justify-center">
            <div className="relative w-64 h-64 rounded-full overflow-hidden border-4 border-indigo-100">
              <Image src="/placeholder.svg?height=256&width=256" alt="Profile" fill className="object-cover" />
            </div>
          </div>

          <div className="w-full md:w-2/3 space-y-4">
            <p className="text-lg text-gray-700">
              안녕하세요! 저는 웹 개발에 열정을 가진 개발자입니다. 대학에서 컴퓨터 과학을 전공하고, 다양한 프로젝트를
              통해 실무 경험을 쌓아왔습니다.
            </p>
            <p className="text-lg text-gray-700">
              저는 기술적 문제 해결뿐만 아니라, 사용자 중심의 디자인과 접근성 있는 웹 경험을 만드는 데 큰 관심을 가지고
              있습니다. 새로운 기술을 배우고 적용하는 것을 좋아하며, 지식 공유를 통해 개발 커뮤니티에 기여하고자 합니다.
            </p>
            <p className="text-lg text-gray-700">
              저의 목표는 기술을 통해 실질적인 가치를 창출하고, 사용자들의 삶을 더 편리하게 만드는 솔루션을 개발하는
              것입니다.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
