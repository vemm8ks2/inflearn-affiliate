// app/page.tsx
export default function Home() {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          최신 인프런 강의 추천
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          프로그래밍, 데이터 사이언스, 디자인 등 다양한 분야의
          <br />
          검증된 강의를 만나보세요.
        </p>
        <div className="flex justify-center gap-4">
          <a
            href="/courses"
            className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            전체 강의 보기
          </a>
          <a
            href="/about"
            className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:border-primary-600 hover:text-primary-600 transition-colors"
          >
            서비스 소개
          </a>
        </div>
      </div>
    </div>
  );
}
