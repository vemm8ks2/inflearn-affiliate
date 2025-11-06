# scripts/test_db_utils_mock.py
"""
db_utils.py Mock 테스트
- Supabase 외부 의존성을 Mock으로 격리
- validate_course_data() 유효성 검증 로직 테스트
- upsert_courses() 배치 처리 로직 테스트
"""

import sys
from pathlib import Path
from unittest import mock
import pytest

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))


class TestValidateCourseData:
    """validate_course_data() 함수 테스트"""

    def test_valid_minimal_course(self):
        """최소 필수 필드만 있는 유효한 강의"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동"
        }
        assert validate_course_data(course) is True

    def test_valid_full_course(self):
        """모든 필드가 있는 유효한 강의"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "rating": 4.5,
            "review_count": 100,
            "student_count": 500,
            "original_price": 55000,
            "sale_price": 33000
        }
        assert validate_course_data(course) is True

    def test_missing_required_field_title(self):
        """필수 필드 누락 - title"""
        from src.db_utils import validate_course_data

        course = {
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동"
        }
        assert validate_course_data(course) is False

    def test_missing_required_field_url(self):
        """필수 필드 누락 - url"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "instructor": "홍길동"
        }
        assert validate_course_data(course) is False

    def test_missing_required_field_instructor(self):
        """필수 필드 누락 - instructor"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test"
        }
        assert validate_course_data(course) is False

    def test_rating_valid_range(self):
        """평점 유효 범위 테스트 (0-5)"""
        from src.db_utils import validate_course_data

        # 최소값
        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "rating": 0.0
        }
        assert validate_course_data(course) is True

        # 최대값
        course["rating"] = 5.0
        assert validate_course_data(course) is True

        # 중간값
        course["rating"] = 3.5
        assert validate_course_data(course) is True

    def test_rating_invalid_range(self):
        """평점 범위 오류 테스트"""
        from src.db_utils import validate_course_data

        # 음수
        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "rating": -1.0
        }
        assert validate_course_data(course) is False

        # 5 초과
        course["rating"] = 5.1
        assert validate_course_data(course) is False

    def test_rating_invalid_type(self):
        """평점 타입 오류 테스트"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "rating": "invalid"
        }
        assert validate_course_data(course) is False

    def test_review_count_negative(self):
        """리뷰 수 음수 오류 테스트"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "review_count": -10
        }
        assert validate_course_data(course) is False

    def test_review_count_invalid_type(self):
        """리뷰 수 타입 오류 테스트"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "review_count": "invalid"
        }
        assert validate_course_data(course) is False

    def test_student_count_negative(self):
        """수강생 수 음수 오류 테스트"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "student_count": -100
        }
        assert validate_course_data(course) is False

    def test_student_count_invalid_type(self):
        """수강생 수 타입 오류 테스트"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "student_count": "invalid"
        }
        assert validate_course_data(course) is False

    def test_price_negative(self):
        """가격 음수 오류 테스트"""
        from src.db_utils import validate_course_data

        # original_price 음수
        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "original_price": -10000
        }
        assert validate_course_data(course) is False

        # sale_price 음수
        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "sale_price": -5000
        }
        assert validate_course_data(course) is False

    def test_price_invalid_type(self):
        """가격 타입 오류 테스트"""
        from src.db_utils import validate_course_data

        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "original_price": "invalid"
        }
        assert validate_course_data(course) is False

    def test_logical_consistency_warning(self):
        """논리 일관성 경고 테스트 (리뷰 수 > 수강생 수)"""
        from src.db_utils import validate_course_data

        # 경고만 하고 통과함 (실제 데이터에서 발생 가능)
        course = {
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "review_count": 1000,
            "student_count": 500
        }
        # 경고는 로그에만 남고 True 반환
        assert validate_course_data(course) is True


class TestUpsertCoursesMock:
    """upsert_courses() Mock 테스트"""

    @mock.patch('db_utils.supabase')
    def test_upsert_empty_list(self, mock_supabase):
        """빈 리스트 저장 테스트"""
        from src.db_utils import upsert_courses

        result = upsert_courses([])
        assert result == 0
        mock_supabase.table.assert_not_called()

    @mock.patch('db_utils.supabase')
    def test_upsert_single_course(self, mock_supabase):
        """단일 강의 저장 테스트"""
        from src.db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [{
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동"
        }]

        result = upsert_courses(courses, batch_size=10)

        assert result == 1
        mock_supabase.table.assert_called_once_with("courses")
        mock_table.upsert.assert_called_once()

    @mock.patch('db_utils.supabase')
    def test_upsert_batch_processing(self, mock_supabase):
        """배치 처리 테스트 (batch_size=3, 10개 강의)"""
        from src.db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 10개 강의 생성
        courses = [
            {
                "title": f"테스트 강의 {i}",
                "url": f"https://inflearn.com/course/test-{i}",
                "instructor": "홍길동"
            }
            for i in range(10)
        ]

        result = upsert_courses(courses, batch_size=3)

        # 10개 강의 → batch_size=3 → 4번 호출 (3, 3, 3, 1)
        assert result == 10
        assert mock_table.upsert.call_count == 4

    @mock.patch('db_utils.supabase')
    def test_upsert_invalid_data_filtering(self, mock_supabase):
        """유효하지 않은 데이터 필터링 테스트"""
        from src.db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [
            # 유효한 데이터
            {
                "title": "테스트 강의 1",
                "url": "https://inflearn.com/course/test-1",
                "instructor": "홍길동"
            },
            # 무효한 데이터 (title 누락)
            {
                "url": "https://inflearn.com/course/test-2",
                "instructor": "홍길동"
            },
            # 유효한 데이터
            {
                "title": "테스트 강의 3",
                "url": "https://inflearn.com/course/test-3",
                "instructor": "홍길동"
            }
        ]

        result = upsert_courses(courses, batch_size=10)

        # 유효한 데이터 2개만 저장됨
        assert result == 2
        mock_table.upsert.assert_called_once()

    @mock.patch('db_utils.supabase')
    def test_upsert_exception_handling(self, mock_supabase):
        """Supabase 저장 실패 예외 처리 테스트"""
        from src.db_utils import upsert_courses

        # Mock 설정 - 예외 발생
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.side_effect = Exception("DB 연결 실패")

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [{
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동"
        }]

        result = upsert_courses(courses, batch_size=10)

        # 예외 발생 시 0 반환
        assert result == 0
        mock_table.upsert.assert_called_once()

    @mock.patch('db_utils.supabase')
    def test_upsert_data_transformation(self, mock_supabase):
        """데이터 변환 로직 테스트 (Supabase 스키마 매핑)"""
        from src.db_utils import upsert_courses
        from datetime import datetime, timezone

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [{
            "title": "테스트 강의",
            "url": "https://inflearn.com/course/test",
            "instructor": "홍길동",
            "course_id": "test-123",
            "thumbnail_url": "https://example.com/image.jpg",
            "original_price": 55000,
            "sale_price": 33000,
            "discount_rate": 40,
            "is_on_sale": True,
            "rating": 4.5,
            "review_count": 100,
            "student_count": 500,
            "scraped_at": "2025-11-05T10:00:00",
            "category": "개발",
            "subcategory": "백엔드",
            "difficulty_level": "중급"
        }]

        upsert_courses(courses, batch_size=10)

        # upsert 호출 시 전달된 데이터 검증
        call_args = mock_table.upsert.call_args
        db_records = call_args[0][0]

        assert len(db_records) == 1
        record = db_records[0]

        # 필수 필드 매핑 검증
        assert record["title"] == "테스트 강의"
        assert record["url"] == "https://inflearn.com/course/test"
        assert record["instructor"] == "홍길동"

        # 선택 필드 매핑 검증
        assert record["course_id"] == "test-123"
        assert record["original_price"] == 55000
        assert record["sale_price"] == 33000
        assert record["is_on_sale"] is True
        assert record["rating"] == 4.5
        assert record["review_count"] == 100
        assert record["student_count"] == 500

        # 기본값 검증
        assert record["source"] == "inflearn"
        assert record["is_trending"] is False
        assert "updated_at" in record


class TestGetAllCoursesMock:
    """get_all_courses() Mock 테스트"""

    @mock.patch('db_utils.supabase')
    def test_get_all_courses_success(self, mock_supabase):
        """모든 강의 조회 성공 테스트"""
        from src.db_utils import get_all_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_select = mock.Mock()
        mock_execute = mock.Mock()

        mock_data = [
            {"title": "강의1", "url": "url1", "instructor": "강사1"},
            {"title": "강의2", "url": "url2", "instructor": "강사2"}
        ]
        mock_execute.execute.return_value = mock.Mock(data=mock_data)

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_execute

        result = get_all_courses()

        assert len(result) == 2
        assert result[0]["title"] == "강의1"
        mock_supabase.table.assert_called_once_with("courses")
        mock_table.select.assert_called_once_with("*")

    @mock.patch('db_utils.supabase')
    def test_get_all_courses_exception(self, mock_supabase):
        """조회 실패 예외 처리 테스트"""
        from src.db_utils import get_all_courses

        # Mock 설정 - 예외 발생
        mock_table = mock.Mock()
        mock_select = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.side_effect = Exception("DB 연결 실패")

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_execute

        result = get_all_courses()

        # 예외 발생 시 빈 리스트 반환
        assert result == []


if __name__ == "__main__":
    # 모든 테스트 실행
    pytest.main([__file__, "-v"])
