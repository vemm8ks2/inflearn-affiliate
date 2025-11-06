// lib/types.ts
/**
 * 인프런 강의 추천 시스템 타입 정의
 *
 * 이 파일은 애플리케이션 전체에서 사용되는 타입을 중앙화하여 관리합니다.
 * Supabase 데이터베이스 스키마와 일치하도록 유지해야 합니다.
 */

/**
 * 강의 정보 타입
 * Supabase의 courses 테이블과 매핑됩니다.
 */
export type Course = {
  /** 강의 고유 ID (UUID) */
  id: string;

  /** 강의 제목 */
  title: string;

  /** 강사명 */
  instructor: string;

  /** 인프런 강의 URL */
  url: string;

  /** 정가 (원화) */
  price_krw: number | null;

  /** 할인가 (원화) */
  discount_price_krw: number | null;

  /** 평점 (0-5) */
  rating: number | null;

  /** 수강생 수 */
  student_count: number;

  /** 카테고리 (예: IT/프로그래밍) */
  category: string | null;

  /** 서브카테고리 (예: 웹 개발, 데이터 사이언스) */
  subcategory: string | null;

  /** 난이도 (초급/중급/고급) */
  difficulty_level: string | null;

  /** 강의 시간 (시간 단위) */
  duration_hours: number | null;

  /** 인기 강의 여부 */
  is_trending: boolean;

  /** 생성 일시 */
  created_at: string;

  /** 수정 일시 */
  updated_at: string;
};

/**
 * 카테고리 정보 타입
 * 강의 분류를 위한 카테고리 정보
 */
export type Category = {
  /** 카테고리 ID */
  id: string;

  /** 카테고리 이름 */
  name: string;

  /** URL 슬러그 */
  slug: string;

  /** 부모 카테고리 ID (서브카테고리인 경우) */
  parent_id: string | null;

  /** 정렬 순서 */
  sort_order: number;

  /** 생성 일시 */
  created_at: string;
};

/**
 * 리뷰 정보 타입
 * AI가 생성한 강의 리뷰 정보
 */
export type Review = {
  /** 리뷰 ID */
  id: string;

  /** 강의 ID (외래키) */
  course_id: string;

  /** AI 생성 리뷰 내용 */
  content: string;

  /** AI 평가 점수 (0-5) */
  rating: number;

  /** 리뷰 요약 (짧은 버전) */
  summary: string | null;

  /** 장점 */
  pros: string[] | null;

  /** 단점 */
  cons: string[] | null;

  /** 추천 대상 */
  recommended_for: string[] | null;

  /** 생성 일시 */
  created_at: string;

  /** 수정 일시 */
  updated_at: string;
};

/**
 * 강의 목록 조회 옵션
 */
export type CoursesQueryOptions = {
  /** 카테고리 필터 */
  category?: string;

  /** 서브카테고리 필터 */
  subcategory?: string;

  /** 난이도 필터 */
  difficulty_level?: string;

  /** 인기 강의만 조회 */
  trending_only?: boolean;

  /** 정렬 기준 */
  sort_by?: 'created_at' | 'rating' | 'student_count' | 'price_krw';

  /** 정렬 방향 */
  sort_order?: 'asc' | 'desc';

  /** 페이지 번호 (1부터 시작) */
  page?: number;

  /** 페이지당 항목 수 */
  limit?: number;
};

/**
 * 페이지네이션 결과 타입
 */
export type PaginatedResult<T> = {
  /** 데이터 배열 */
  data: T[];

  /** 현재 페이지 */
  page: number;

  /** 페이지당 항목 수 */
  limit: number;

  /** 전체 항목 수 */
  total: number;

  /** 전체 페이지 수 */
  total_pages: number;

  /** 다음 페이지 존재 여부 */
  has_next: boolean;

  /** 이전 페이지 존재 여부 */
  has_prev: boolean;
};

/**
 * API 응답 타입
 */
export type ApiResponse<T> = {
  /** 성공 여부 */
  success: boolean;

  /** 응답 데이터 */
  data?: T;

  /** 에러 메시지 */
  error?: string;

  /** 에러 코드 */
  code?: string;
};
