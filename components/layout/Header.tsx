// components/layout/Header.tsx
import Link from "next/link";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-primary-600">
              인프런 강의 추천
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              href="/courses"
              className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              전체 강의
            </Link>
            <Link
              href="/categories"
              className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              카테고리
            </Link>
            <Link
              href="/about"
              className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              소개
            </Link>
          </nav>

          {/* Mobile Menu Button */}
          <button className="md:hidden">
            <svg
              className="h-6 w-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
