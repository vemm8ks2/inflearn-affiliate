// app/about/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "서비스 소개",
  description: "인프런 강의 추천 플랫폼 소개",
};

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-6">서비스 소개</h1>

        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold mb-3">인프런 강의 추천은?</h2>
            <p className="leading-relaxed">
              검증된 인프런 강의를 추천하고 상세한 리뷰를 제공하는 플랫폼입니다.
              AI 기술과 자동화를 활용하여 최신 강의 정보를 빠르게 제공합니다.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">주요 기능</h2>
            <ul className="list-disc list-inside space-y-2">
              <li>인프런 강의 자동 수집 및 업데이트</li>
              <li>AI 기반 강의 리뷰 생성</li>
              <li>카테고리별 강의 분류</li>
              <li>평점 및 수강생 수 기반 추천</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">기술 스택</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="border rounded-lg p-4 text-center">
                <p className="font-semibold">Next.js 14</p>
                <p className="text-sm text-gray-500">Frontend</p>
              </div>
              <div className="border rounded-lg p-4 text-center">
                <p className="font-semibold">Supabase</p>
                <p className="text-sm text-gray-500">Database</p>
              </div>
              <div className="border rounded-lg p-4 text-center">
                <p className="font-semibold">GPT-4</p>
                <p className="text-sm text-gray-500">AI</p>
              </div>
              <div className="border rounded-lg p-4 text-center">
                <p className="font-semibold">Vercel</p>
                <p className="text-sm text-gray-500">Hosting</p>
              </div>
            </div>
          </section>

          <section className="bg-gray-50 p-6 rounded-lg">
            <h3 className="font-semibold mb-2">📢 고지사항</h3>
            <p className="text-sm text-gray-600">
              본 사이트는 인프런 어필리에이트 프로그램에 참여하고 있습니다.
              링크를 통한 구매 시 소정의 수수료를 받을 수 있으며, 이는 사이트
              운영에 도움이 됩니다.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
