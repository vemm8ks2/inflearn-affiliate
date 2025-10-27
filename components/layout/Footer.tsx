// components/layout/Footer.tsx
export default function Footer() {
  return (
    <footer className="border-t bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">
              인프런 강의 추천
            </h3>
            <p className="text-sm text-gray-600">
              최신 IT 강의를 추천하고 리뷰하는 플랫폼입니다.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">바로가기</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <a href="/courses" className="hover:text-primary-600">
                  전체 강의
                </a>
              </li>
              <li>
                <a href="/categories" className="hover:text-primary-600">
                  카테고리
                </a>
              </li>
              <li>
                <a href="/about" className="hover:text-primary-600">
                  소개
                </a>
              </li>
            </ul>
          </div>

          {/* Disclaimer */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">고지사항</h3>
            <p className="text-xs text-gray-500">
              본 사이트는 인프런 어필리에이트 프로그램에 참여하고 있으며, 링크를
              통한 구매 시 소정의 수수료를 받을 수 있습니다.
            </p>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-6 border-t text-center text-sm text-gray-500">
          © {new Date().getFullYear()} 인프런 강의 추천. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
