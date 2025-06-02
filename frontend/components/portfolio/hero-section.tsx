export default function HeroSection() {
  return (
    <section className="py-20 px-6 bg-gradient-to-r from-indigo-50 to-purple-50">
      <div className="container mx-auto text-center max-w-3xl">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
          개발자 <span className="text-indigo-600">YourName</span>
        </h1>
        <h2 className="text-xl md:text-2xl text-gray-700 mb-8">Python & Next.js 웹 개발자</h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          코드로 가치를 창조하고 지식을 나누는 개발자입니다. 사용자 경험과 성능을 모두 고려한 웹 애플리케이션을
          만듭니다.
        </p>
      </div>
    </section>
  )
}
