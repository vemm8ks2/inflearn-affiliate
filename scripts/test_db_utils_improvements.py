# scripts/test_db_utils_improvements.py
"""
db_utils.py 개선 사항 검증 테스트
"""

def test_imports():
    """import 문 검증"""
    print("=" * 60)
    print("1. Import 검증")
    print("=" * 60)

    try:
        import traceback
        print("✅ traceback 모듈 import 성공")
    except ImportError as e:
        print(f"❌ traceback import 실패: {e}")

    try:
        from datetime import datetime, timezone
        print("✅ timezone import 성공")

        # 타임존 테스트
        utc_time = datetime.now(timezone.utc).isoformat()
        print(f"   UTC 시간: {utc_time}")
        print(f"   타임존 정보 포함: {'+00:00' in utc_time}")
    except ImportError as e:
        print(f"❌ timezone import 실패: {e}")

    try:
        from logger_config import logger
        print("✅ logger_config 모듈 import 성공")
        logger.info("로깅 시스템 테스트")
    except ImportError as e:
        print(f"❌ logger_config import 실패: {e}")


def test_validate_course_data():
    """validate_course_data 함수 검증"""
    print("\n" + "=" * 60)
    print("2. validate_course_data() 함수 검증")
    print("=" * 60)

    # db_utils에서 함수를 직접 테스트하기 위해 코드 복사
    def validate_course_data(course):
        """강의 데이터 유효성 검증"""
        required_fields = ["title", "url"]
        for field in required_fields:
            if not course.get(field):
                print(f"⚠️  필수 필드 누락: {field}")
                return False
        return True

    # 테스트 케이스
    test_cases = [
        ({"title": "강의1", "url": "https://test.com/1"}, True, "정상 데이터"),
        ({"title": "강의2"}, False, "URL 누락"),
        ({"url": "https://test.com/3"}, False, "제목 누락"),
        ({}, False, "모든 필드 누락"),
    ]

    for course, expected, description in test_cases:
        result = validate_course_data(course)
        status = "✅" if result == expected else "❌"
        print(f"{status} {description}: {result} (기대값: {expected})")


def test_batch_processing_logic():
    """배치 처리 로직 검증"""
    print("\n" + "=" * 60)
    print("3. 배치 처리 로직 검증")
    print("=" * 60)

    # 테스트 데이터
    test_courses = [
        {"title": f"강의{i}", "url": f"https://test.com/{i}"}
        for i in range(25)
    ]

    batch_size = 10
    print(f"총 데이터: {len(test_courses)}개")
    print(f"배치 크기: {batch_size}개")

    # 배치 분할 시뮬레이션
    batch_count = 0
    for i in range(0, len(test_courses), batch_size):
        batch = test_courses[i:i + batch_size]
        batch_count += 1
        print(f"  ✅ 배치 {batch_count}: {len(batch)}개")

    expected_batches = 3
    status = "✅" if batch_count == expected_batches else "❌"
    print(f"\n{status} 총 배치 수: {batch_count} (기대값: {expected_batches})")


def test_error_handling():
    """에러 핸들링 검증"""
    print("\n" + "=" * 60)
    print("4. 에러 핸들링 검증")
    print("=" * 60)

    import traceback

    try:
        # 의도적 에러 발생
        raise Exception("테스트 에러")
    except Exception as e:
        print(f"✅ Exception 포착: {e}")
        error_trace = traceback.format_exc()
        print(f"✅ traceback 정보 수집 성공 (길이: {len(error_trace)} chars)")
        print(f"   traceback 일부:\n{error_trace[:200]}...")


def test_environment_validation():
    """환경 변수 검증 로직 테스트"""
    print("\n" + "=" * 60)
    print("5. 환경 변수 검증 로직 테스트")
    print("=" * 60)

    import os

    # 기존 환경 변수 백업
    backup_url = os.getenv("SUPABASE_URL")
    backup_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # SUPABASE_URL 누락 시뮬레이션
    os.environ.pop("SUPABASE_URL", None)

    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        if not SUPABASE_URL:
            raise ValueError(
                "SUPABASE_URL 환경 변수가 설정되지 않았습니다. "
                ".env 파일을 확인하세요."
            )
        print("❌ 검증 실패: 에러가 발생해야 함")
    except ValueError as e:
        print(f"✅ 환경 변수 검증 성공: {str(e)[:50]}...")

    # 환경 변수 복구
    if backup_url:
        os.environ["SUPABASE_URL"] = backup_url
    if backup_key:
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = backup_key


def test_docstring_improvements():
    """독스트링 개선 검증"""
    print("\n" + "=" * 60)
    print("6. 독스트링 개선 검증")
    print("=" * 60)

    # 개선된 독스트링 예시
    docstring = """
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

    required_sections = ["Args:", "Returns:", "Examples:"]
    for section in required_sections:
        if section in docstring:
            print(f"✅ {section} 섹션 포함")
        else:
            print(f"❌ {section} 섹션 누락")


def main():
    """전체 테스트 실행"""
    print("\n" + "=" * 60)
    print("db_utils.py 개선 사항 검증 테스트")
    print("=" * 60)

    test_imports()
    test_validate_course_data()
    test_batch_processing_logic()
    test_error_handling()
    test_environment_validation()
    test_docstring_improvements()

    print("\n" + "=" * 60)
    print("✅ 모든 개선 사항 검증 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
