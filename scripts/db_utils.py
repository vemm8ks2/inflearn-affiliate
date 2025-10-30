# scripts/db_utils.py
import os
import traceback
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone
from logger_config import logger

# 환경 변수 로드
load_dotenv()

# Supabase 클라이언트 생성
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL 환경 변수가 설정되지 않았습니다. "
        ".env 파일을 확인하세요."
    )

if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_SERVICE_ROLE_KEY 환경 변수가 설정되지 않았습니다. "
        ".env 파일을 확인하세요."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def validate_course_data(course):
    """
    강의 데이터 유효성 검증

    Args:
        course (dict): 강의 데이터 딕셔너리

    Returns:
        bool: 유효 여부
    """
    required_fields = ["title", "url"]

    for field in required_fields:
        if not course.get(field):
            logger.warning(f"필수 필드 누락: {field} - {course}")
            return False

    return True


def upsert_courses(courses, batch_size=10):
    """
    강의 데이터를 Supabase에 배치 저장 (Upsert)

    URL을 기준으로 중복 데이터는 업데이트하고, 새 데이터는 삽입합니다.
    대량 데이터 처리를 위해 배치 단위로 분할하여 저장합니다.

    Args:
        courses (list): 강의 데이터 딕셔너리 리스트
        batch_size (int, optional): 배치 크기. 기본값 10개

    Returns:
        int: 성공적으로 저장된 강의 개수

    Examples:
        >>> courses = [{"title": "강의1", "url": "https://..."}, ...]
        >>> saved = upsert_courses(courses, batch_size=20)
        >>> print(f"저장 완료: {saved}개")
    """
    if not courses:
        logger.warning("⚠️  저장할 데이터가 없습니다.")
        return 0

    # 유효한 데이터만 필터링
    valid_courses = [c for c in courses if validate_course_data(c)]

    if len(valid_courses) < len(courses):
        logger.warning(
            f"유효하지 않은 데이터 {len(courses) - len(valid_courses)}개 제외"
        )

    total_saved = 0

    # 배치 단위로 분할
    for i in range(0, len(valid_courses), batch_size):
        batch = valid_courses[i:i + batch_size]

        # 데이터 변환 (Supabase 스키마에 맞게)
        db_records = []
        for course in batch:
            record = {
                "title": course.get("title"),
                "instructor": course.get("instructor"),
                "url": course.get("url"),
                "price_krw": course.get("price_krw"),
                "discount_price_krw": course.get("discount_price_krw"),
                "rating": course.get("rating"),
                "student_count": course.get("student_count", 0),
                "category": course.get("category"),
                "subcategory": course.get("subcategory"),
                "difficulty_level": course.get("difficulty_level"),
                "is_trending": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            db_records.append(record)

        try:
            # Upsert 실행 (url이 unique constraint)
            response = supabase.table("courses").upsert(
                db_records,
                on_conflict="url"
            ).execute()

            total_saved += len(db_records)
            logger.info(f"  ✅ 배치 {i//batch_size + 1} 저장: {len(db_records)}개")

        except Exception as e:
            logger.error(f"  ❌ 배치 {i//batch_size + 1} 저장 실패: {e}")
            logger.debug(traceback.format_exc())

    logger.info(f"✅ Supabase 총 저장: {total_saved}개")
    return total_saved


def get_all_courses():
    """
    Supabase에서 모든 강의 조회 (테스트용)

    Returns:
        list: 강의 데이터 리스트 (빈 리스트 if 실패)
    """
    try:
        response = supabase.table("courses").select("*").execute()
        logger.info(f"📊 조회 성공: {len(response.data)}개")
        return response.data
    except Exception as e:
        logger.error(f"❌ 조회 실패: {e}")
        logger.debug(traceback.format_exc())
        return []


if __name__ == "__main__":
    # 테스트: 기존 강의 조회
    logger.info("=" * 50)
    logger.info("db_utils 테스트 시작")
    logger.info("=" * 50)

    courses = get_all_courses()
    logger.info(f"📊 현재 DB에 저장된 강의: {len(courses)}개")

    if courses:
        logger.info("\n첫 번째 강의:")
        logger.info(f"  제목: {courses[0]['title']}")
        logger.info(f"  강사: {courses[0]['instructor']}")
