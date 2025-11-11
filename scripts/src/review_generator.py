# scripts/src/review_generator.py
"""
리뷰 생성 엔진 (Phase 7)
Supabase에서 리뷰 없는 강의를 조회하고 배치로 AI 리뷰 생성
"""

import time
from typing import List, Dict, Tuple
from datetime import datetime, timezone
from src.logger_config import logger
from src.db_utils import get_courses_without_reviews, save_review_to_db
from src.ai_reviewer import AIReviewer
from src.config import config


def chunk_list(lst: List, size: int) -> List[List]:
    """
    리스트를 지정된 크기로 분할

    Args:
        lst: 분할할 리스트
        size: 청크 크기

    Returns:
        분할된 리스트들의 리스트
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def calculate_cost(reviews: List[Dict]) -> Tuple[float, Dict]:
    """
    리뷰 생성 비용 계산

    Args:
        reviews: 생성된 리뷰 데이터 리스트

    Returns:
        (총 비용, 상세 정보)
    """
    # GPT 모델별 가격 (2025년 기준)
    PRICING = {
        "gpt-4-turbo": {"input": 0.01 / 1000, "output": 0.03 / 1000},
        "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
        "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000},
    }

    total_cost = 0.0
    total_tokens = 0
    model_usage = {}

    for review in reviews:
        model = review.get("model_version", "gpt-3.5-turbo")
        tokens = review.get("tokens_used", 0)

        # 모델별 가격 가져오기 (기본값: gpt-3.5-turbo)
        pricing = PRICING.get(model, PRICING["gpt-3.5-turbo"])

        # 간단한 추정: input 40%, output 60%
        input_tokens = tokens * 0.4
        output_tokens = tokens * 0.6

        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])
        total_cost += cost
        total_tokens += tokens

        # 모델별 사용량 집계
        if model not in model_usage:
            model_usage[model] = {"count": 0, "tokens": 0, "cost": 0.0}

        model_usage[model]["count"] += 1
        model_usage[model]["tokens"] += tokens
        model_usage[model]["cost"] += cost

    details = {
        "total_reviews": len(reviews),
        "total_tokens": total_tokens,
        "total_cost_usd": total_cost,
        "average_tokens_per_review": total_tokens / len(reviews) if reviews else 0,
        "average_cost_per_review": total_cost / len(reviews) if reviews else 0,
        "model_usage": model_usage
    }

    return total_cost, details


def print_cost_summary(cost: float, details: Dict):
    """
    비용 요약 출력

    Args:
        cost: 총 비용
        details: 상세 정보
    """
    logger.info("\n" + "=" * 60)
    logger.info("💰 비용 리포트")
    logger.info("=" * 60)

    logger.info(f"생성된 리뷰: {details['total_reviews']}개")
    logger.info(f"총 토큰 사용량: {details['total_tokens']:,} tokens")
    logger.info(f"평균 토큰/리뷰: {details['average_tokens_per_review']:.1f} tokens")
    logger.info(f"\n총 비용: ${cost:.4f}")
    logger.info(f"평균 비용/리뷰: ${details['average_cost_per_review']:.4f}")

    # 모델별 사용량
    if details.get("model_usage"):
        logger.info("\n모델별 사용량:")
        for model, usage in details["model_usage"].items():
            logger.info(
                f"  {model}: {usage['count']}개 리뷰, "
                f"{usage['tokens']:,} tokens, ${usage['cost']:.4f}"
            )

    # 예상 월간 비용
    daily_cost = cost
    monthly_cost = daily_cost * 30
    logger.info(f"\n예상 일일 비용: ${daily_cost:.2f}")
    logger.info(f"예상 월간 비용: ${monthly_cost:.2f}")
    logger.info("=" * 60)


def generate_reviews_batch(
    courses: List[Dict],
    reviewer: AIReviewer,
    batch_size: int = 10,
    delay: float = 1.0
) -> Tuple[List[Dict], List[Dict]]:
    """
    배치 단위로 리뷰 생성

    Args:
        courses: 강의 리스트
        reviewer: AIReviewer 인스턴스
        batch_size: 배치 크기 (기본값: 10)
        delay: 각 리뷰 생성 간 대기 시간 (초, Rate limit 방지)

    Returns:
        (성공한 리뷰 리스트, 실패한 강의 리스트)
    """
    successful_reviews = []
    failed_courses = []

    # 배치로 분할
    batches = chunk_list(courses, batch_size)

    logger.info(f"\n📦 총 {len(batches)}개 배치로 처리 예정 (배치 크기: {batch_size})")

    for batch_idx, batch in enumerate(batches, 1):
        logger.info(f"\n--- 배치 {batch_idx}/{len(batches)} 시작 ---")

        for course in batch:
            course_title = course.get("title", "제목 없음")

            try:
                # 1. AI 리뷰 생성
                logger.info(f"🤖 리뷰 생성 중: {course_title[:50]}...")
                review_data = reviewer.generate_review(course)

                # 2. DB 저장
                course_id = course.get("id")
                if not course_id:
                    logger.error(f"❌ course_id 누락: {course_title}")
                    failed_courses.append({
                        "course": course,
                        "error": "course_id 누락"
                    })
                    continue

                success = save_review_to_db(course_id, review_data)

                if success:
                    successful_reviews.append(review_data)
                    logger.info(
                        f"✅ 저장 완료 ({len(successful_reviews)}/{len(courses)}): "
                        f"{len(review_data['review_text'])}자, "
                        f"{review_data['tokens_used']} tokens"
                    )
                else:
                    failed_courses.append({
                        "course": course,
                        "error": "DB 저장 실패"
                    })

                # Rate limit 방지 대기
                if delay > 0:
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"❌ 리뷰 생성 실패: {course_title[:50]}... - {e}")
                failed_courses.append({
                    "course": course,
                    "error": str(e)
                })
                continue

        logger.info(f"--- 배치 {batch_idx} 완료 ---")

    return successful_reviews, failed_courses


def validate_environment():
    """
    환경 설정 검증

    Raises:
        ValueError: 필수 환경 변수가 설정되지 않은 경우
    """
    errors = []

    # OpenAI API 키 확인
    if not config.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY가 설정되지 않았습니다.")

    # Supabase 설정 확인 (db_utils에서 이미 확인하지만 명시적으로 체크)
    import os
    if not os.getenv("SUPABASE_URL"):
        errors.append("SUPABASE_URL이 설정되지 않았습니다.")

    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        errors.append("SUPABASE_SERVICE_ROLE_KEY가 설정되지 않았습니다.")

    if errors:
        error_msg = "\n❌ 환경 설정 오류:\n  " + "\n  ".join(errors)
        error_msg += "\n\n.env 파일을 확인하세요."
        raise ValueError(error_msg)


def main(max_courses: int = 20, batch_size: int = 10, delay: float = 1.0):
    """
    메인 실행 함수

    Args:
        max_courses: 처리할 최대 강의 수 (기본값: 20)
        batch_size: 배치 크기 (기본값: 10)
        delay: API 호출 간 대기 시간 초 (기본값: 1.0)
    """
    start_time = time.time()

    logger.info("=" * 60)
    logger.info("🚀 AI 리뷰 생성 시작")
    logger.info("=" * 60)
    logger.info(f"실행 시각: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info(f"설정: max_courses={max_courses}, batch_size={batch_size}, delay={delay}s")

    try:
        # 1. 환경 설정 검증
        logger.info("\n🔍 환경 설정 검증 중...")
        validate_environment()
        logger.info("✅ 환경 설정 정상")

        # 2. AIReviewer 초기화
        logger.info("\n🤖 AIReviewer 초기화 중...")
        reviewer = AIReviewer()
        logger.info(f"✅ 모델: {reviewer.model}, 프롬프트 버전: {reviewer.prompt_version}")

        # 3. 리뷰 없는 강의 조회
        logger.info(f"\n📊 리뷰 없는 강의 조회 중 (최대 {max_courses}개)...")
        courses = get_courses_without_reviews(limit=max_courses)

        if not courses:
            logger.info("ℹ️  처리할 강의가 없습니다.")
            return

        logger.info(f"✅ {len(courses)}개 강의 발견")

        # 4. 배치로 리뷰 생성
        logger.info("\n🔄 리뷰 생성 시작...")
        successful_reviews, failed_courses = generate_reviews_batch(
            courses=courses,
            reviewer=reviewer,
            batch_size=batch_size,
            delay=delay
        )

        # 5. 결과 요약
        logger.info("\n" + "=" * 60)
        logger.info("📊 실행 결과")
        logger.info("=" * 60)

        success_count = len(successful_reviews)
        fail_count = len(failed_courses)
        total_count = len(courses)

        logger.info(f"총 처리: {total_count}개")
        logger.info(f"✅ 성공: {success_count}개 ({success_count/total_count*100:.1f}%)")
        logger.info(f"❌ 실패: {fail_count}개 ({fail_count/total_count*100:.1f}%)")

        # 실패한 강의 상세 출력
        if failed_courses:
            logger.warning(f"\n⚠️  실패한 강의 {len(failed_courses)}개:")
            for idx, failed in enumerate(failed_courses[:5], 1):  # 최대 5개만 출력
                course_title = failed["course"].get("title", "제목 없음")
                error = failed["error"]
                logger.warning(f"  {idx}. {course_title[:50]}... - {error}")

            if len(failed_courses) > 5:
                logger.warning(f"  ... 외 {len(failed_courses) - 5}개")

        # 6. 비용 리포트
        if successful_reviews:
            cost, details = calculate_cost(successful_reviews)
            print_cost_summary(cost, details)

        # 7. 실행 시간
        elapsed = time.time() - start_time
        logger.info(f"\n⏱️  총 실행 시간: {elapsed:.2f}초")
        logger.info("=" * 60)
        logger.info("✅ AI 리뷰 생성 완료")
        logger.info("=" * 60)

    except ValueError as e:
        logger.error(f"\n{e}")
        logger.error("\n실행을 중단합니다.")
        return

    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return


if __name__ == "__main__":
    # 설정값 조정 가능
    MAX_COURSES = 20  # 처리할 최대 강의 수
    BATCH_SIZE = 10   # 배치 크기
    DELAY = 1.0       # API 호출 간 대기 시간 (초)

    main(
        max_courses=MAX_COURSES,
        batch_size=BATCH_SIZE,
        delay=DELAY
    )
