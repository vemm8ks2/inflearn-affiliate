# scripts/src/scraper.py
"""
인프런 강의 스크래핑 스크립트 (API 버전)
- API 직접 호출로 안정성 향상
- 로깅 시스템 적용
- 함수 분리 및 모듈화
- 설정 관리 개선
- Phase 6: Playwright 레거시 코드 완전 제거
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Optional, List

# 로컬 모듈 import
from src.logger_config import logger
from src.config import config
from src.db_utils import upsert_courses


# ============================================================================
# API 기반 스크래핑 함수
# ============================================================================

def scrape_inflearn_courses_api(max_courses: Optional[int] = None) -> tuple[List[Dict], Dict]:
    """
    인프런 강의 목록 스크래핑 (API 버전 - 메타데이터 포함)

    Args:
        max_courses: 수집할 최대 강의 수 (기본값: config.MAX_COURSES)

    Returns:
        tuple: (강의 정보 딕셔너리 리스트, 메타데이터 딕셔너리)
    """
    from src.api_client import InflearnAPIClient

    # 기본값 설정
    max_courses = max_courses if max_courses is not None else config.MAX_COURSES

    # 스크래핑 시작 시간 기록
    start_time = time.time()
    start_datetime = datetime.now(timezone.utc)

    logger.info("=" * 60)
    logger.info("🚀 인프런 강의 스크래핑 시작 (API 버전)")
    logger.info(f"설정: max_courses={max_courses}")
    logger.info("=" * 60)

    try:
        # API 클라이언트 생성
        client = InflearnAPIClient(language="ko")

        # 데이터 가져오기
        logger.info(f"🔍 강의 수집 시작 (목표: {max_courses}개)")
        courses = client.get_all_courses(max_courses=max_courses, category=config.CATEGORY)

        # 스크래핑 종료 시간 계산
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        # 메타데이터 생성
        metadata = {
            "version": "1.0.0",
            "scraper_version": "4.0.0",  # Phase 6: Playwright 코드 완전 제거
            "total_courses": len(courses),
            "failed_courses": 0,  # API 방식은 실패 없음
            "scraped_at": start_datetime.isoformat(),
            "scraping_duration_seconds": duration,
            "config": {
                "max_courses": max_courses,
                "category": config.CATEGORY,
                "base_url": "https://course-api.inflearn.com/client/api/v2",
                "method": "API"  # API 방식 명시
            }
        }

        logger.info(f"\n✅ 총 {len(courses)}개 강의 수집 완료 (소요 시간: {duration}초)")
        return courses, metadata

    except Exception as e:
        logger.error(f"스크래핑 중 치명적 오류 발생: {e}", exc_info=True)
        # 에러 발생 시에도 메타데이터 반환
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        metadata = {
            "version": "1.0.0",
            "scraper_version": "4.0.0",
            "total_courses": 0,
            "scraped_at": start_datetime.isoformat(),
            "scraping_duration_seconds": duration,
            "config": {
                "max_courses": max_courses,
                "category": config.CATEGORY,
                "method": "API"
            },
            "error": str(e)
        }
        return [], metadata


# ============================================================================
# 데이터 저장 및 출력 함수
# ============================================================================

def save_to_json(courses: List[Dict], metadata: Optional[Dict] = None, filename: Optional[str] = None):
    """
    수집한 강의 데이터를 JSON 파일로 저장 (메타데이터 포함)

    Args:
        courses: 강의 데이터 리스트
        metadata: 메타데이터 딕셔너리 (선택적)
        filename: 저장할 파일 경로 (기본값: config.JSON_OUTPUT)
    """
    filename = filename or config.JSON_OUTPUT

    try:
        # 메타데이터가 있으면 구조화된 형식으로 저장
        if metadata:
            output_data = {
                "metadata": metadata,
                "courses": courses
            }
        else:
            # 하위 호환성: 메타데이터 없으면 기존 형식 유지
            output_data = courses

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 데이터 저장 완료: {filename}")
    except Exception as e:
        logger.error(f"JSON 저장 실패: {e}", exc_info=True)


def print_summary(courses: List[Dict]):
    """
    수집 결과 요약 출력

    Args:
        courses: 강의 데이터 리스트
    """
    if not courses:
        logger.warning("❌ 수집된 데이터가 없습니다.")
        return

    logger.info("\n📊 수집 결과 요약:")
    logger.info(f"  - 총 강의 수: {len(courses)}")
    logger.info(f"  - 제목 있는 강의: {sum(1 for c in courses if c.get('title'))}")
    logger.info(f"  - 강사명 있는 강의: {sum(1 for c in courses if c.get('instructor'))}")
    logger.info(f"  - URL 있는 강의: {sum(1 for c in courses if c.get('url'))}")
    logger.info(f"  - 썸네일 있는 강의: {sum(1 for c in courses if c.get('thumbnail_url'))}")
    logger.info(f"  - 정가 있는 강의: {sum(1 for c in courses if c.get('original_price'))}")
    logger.info(f"  - 할인가 있는 강의: {sum(1 for c in courses if c.get('sale_price'))}")
    logger.info(f"  - 할인율 있는 강의: {sum(1 for c in courses if c.get('discount_rate'))}")
    logger.info(f"  - 평점 있는 강의: {sum(1 for c in courses if c.get('rating'))}")
    logger.info(f"  - 리뷰 수 있는 강의: {sum(1 for c in courses if c.get('review_count'))}")
    logger.info(f"  - 수강생 수 있는 강의: {sum(1 for c in courses if c.get('student_count'))}")


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    """메인 실행 함수"""
    try:
        # 스크래핑 실행 (API 버전 - 메타데이터 포함)
        courses, metadata = scrape_inflearn_courses_api()

        if courses:
            # JSON 저장 (메타데이터 포함)
            save_to_json(courses, metadata)

            # Supabase 저장
            logger.info("\n💾 Supabase 저장 중...")
            saved_count = upsert_courses(courses)

            # 결과 요약
            print_summary(courses)

            # 메타데이터 요약 출력
            logger.info("\n📋 메타데이터:")
            logger.info(f"  - 데이터 버전: {metadata['version']}")
            logger.info(f"  - 스크래퍼 버전: {metadata['scraper_version']}")
            logger.info(f"  - 수집 시간: {metadata['scraped_at']}")
            logger.info(f"  - 소요 시간: {metadata['scraping_duration_seconds']}초")

            # 최종 결과 요약
            logger.info("\n📊 최종 결과:")
            logger.info(f"  - 수집: {len(courses)}개")
            logger.info(f"  - 저장: {saved_count}개")
            logger.info(f"  - 시간: {datetime.now()}")
        else:
            logger.warning("수집된 데이터가 없습니다.")

        logger.info("\n" + "=" * 60)
        logger.info("✅ 작업 완료")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"메인 함수 실행 중 오류: {e}", exc_info=True)


if __name__ == "__main__":
    main()
