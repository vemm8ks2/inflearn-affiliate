# scripts/test_scraping_extraction_mock.py
"""
scrape_inflearn_with_sales.py 추출 함수 Mock 테스트
- extract_course_data() 단위 테스트
- extract_price_info() Mock 테스트
- extract_rating(), extract_review_count(), extract_student_count() 테스트
"""

import sys
from pathlib import Path
from unittest import mock
import pytest
from datetime import datetime, timezone

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))


class TestExtractRating:
    """extract_rating() 함수 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_rating_valid(self, mock_extract_text):
        """유효한 평점 추출"""
        from scrape_inflearn_with_sales import extract_rating

        mock_extract_text.return_value = "4.5"
        mock_locator = mock.Mock()

        result = extract_rating(mock_locator)
        assert result == 4.5

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_rating_min_max_boundary(self, mock_extract_text):
        """평점 경계값 테스트 (0-5)"""
        from scrape_inflearn_with_sales import extract_rating

        # 최소값
        mock_extract_text.return_value = "0.0"
        mock_locator = mock.Mock()
        assert extract_rating(mock_locator) == 0.0

        # 최대값
        mock_extract_text.return_value = "5.0"
        assert extract_rating(mock_locator) == 5.0

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_rating_out_of_range(self, mock_extract_text):
        """평점 범위 초과 테스트"""
        from scrape_inflearn_with_sales import extract_rating

        mock_locator = mock.Mock()

        # 범위 초과 (> 5)
        mock_extract_text.return_value = "5.5"
        assert extract_rating(mock_locator) is None

        # 음수
        mock_extract_text.return_value = "-1.0"
        assert extract_rating(mock_locator) is None

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_rating_invalid_format(self, mock_extract_text):
        """유효하지 않은 평점 형식"""
        from scrape_inflearn_with_sales import extract_rating

        mock_extract_text.return_value = "invalid"
        mock_locator = mock.Mock()

        assert extract_rating(mock_locator) is None

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_rating_not_found(self, mock_extract_text):
        """평점 요소를 찾을 수 없음"""
        from scrape_inflearn_with_sales import extract_rating

        mock_extract_text.return_value = None
        mock_locator = mock.Mock()

        assert extract_rating(mock_locator) is None


class TestExtractReviewCount:
    """extract_review_count() 함수 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_review_count_with_parentheses(self, mock_extract_text):
        """괄호 포함 리뷰 수 추출"""
        from scrape_inflearn_with_sales import extract_review_count

        mock_extract_text.return_value = "(1,234)"
        mock_locator = mock.Mock()

        result = extract_review_count(mock_locator)
        assert result == 1234

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_review_count_without_parentheses(self, mock_extract_text):
        """괄호 없는 리뷰 수 추출"""
        from scrape_inflearn_with_sales import extract_review_count

        mock_extract_text.return_value = "500"
        mock_locator = mock.Mock()

        result = extract_review_count(mock_locator)
        assert result == 500

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_review_count_zero(self, mock_extract_text):
        """리뷰 수 0"""
        from scrape_inflearn_with_sales import extract_review_count

        mock_extract_text.return_value = "(0)"
        mock_locator = mock.Mock()

        result = extract_review_count(mock_locator)
        assert result == 0

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_review_count_invalid(self, mock_extract_text):
        """유효하지 않은 리뷰 수"""
        from scrape_inflearn_with_sales import extract_review_count

        mock_extract_text.return_value = "(invalid)"
        mock_locator = mock.Mock()

        result = extract_review_count(mock_locator)
        assert result is None


class TestExtractStudentCount:
    """extract_student_count() 함수 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_student_count_with_plus(self, mock_extract_text):
        """+ 기호 포함 수강생 수 추출"""
        from scrape_inflearn_with_sales import extract_student_count

        mock_extract_text.return_value = "3,800+"
        mock_locator = mock.Mock()

        result = extract_student_count(mock_locator)
        assert result == 3800

    @mock.patch('scrape_inflearn_with_sales.extract_text_by_selector')
    def test_extract_student_count_without_plus(self, mock_extract_text):
        """+ 기호 없는 수강생 수 추출"""
        from scrape_inflearn_with_sales import extract_student_count

        mock_extract_text.return_value = "1,234"
        mock_locator = mock.Mock()

        result = extract_student_count(mock_locator)
        assert result == 1234


class TestExtractPriceInfo:
    """extract_price_info() 함수 Mock 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_single_price_element')
    def test_extract_price_info_on_sale(self, mock_extract_single):
        """할인 중인 강의 가격 정보"""
        from scrape_inflearn_with_sales import extract_price_info

        # Mock 설정: first_price 존재 (할인 중)
        mock_extract_single.side_effect = [
            "₩77,000",  # first_price (정가)
            "₩55,000",  # sale_price (할인가)
            "28%"       # discount_rate
        ]

        mock_locator = mock.Mock()
        result = extract_price_info(mock_locator)

        assert result['original_price'] == 77000
        assert result['sale_price'] == 55000
        assert result['discount_rate'] == 28
        assert result['is_on_sale'] is True

    @mock.patch('scrape_inflearn_with_sales.extract_single_price_element')
    def test_extract_price_info_not_on_sale(self, mock_extract_single):
        """할인 없는 강의 가격 정보"""
        from scrape_inflearn_with_sales import extract_price_info

        # Mock 설정: first_price 없음 (할인 없음)
        mock_extract_single.side_effect = [
            None,       # first_price (없음)
            "₩55,000",  # second_price (정가)
        ]

        mock_locator = mock.Mock()
        result = extract_price_info(mock_locator)

        assert result['original_price'] == 55000
        assert result['sale_price'] == 55000
        assert result['discount_rate'] == 0
        assert result['is_on_sale'] is False

    @mock.patch('scrape_inflearn_with_sales.extract_single_price_element')
    def test_extract_price_info_exception_handling(self, mock_extract_single):
        """가격 정보 추출 중 예외 처리"""
        from scrape_inflearn_with_sales import extract_price_info

        # Mock 설정: 예외 발생
        mock_extract_single.side_effect = Exception("추출 실패")

        mock_locator = mock.Mock()
        result = extract_price_info(mock_locator)

        # 예외 발생 시 기본 구조 반환
        assert result['original_price'] is None
        assert result['sale_price'] is None
        assert result['discount_rate'] == 0
        assert result['is_on_sale'] is False


class TestExtractCourseData:
    """extract_course_data() 함수 Mock 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_title')
    @mock.patch('scrape_inflearn_with_sales.extract_instructor')
    @mock.patch('scrape_inflearn_with_sales.extract_thumbnail')
    @mock.patch('scrape_inflearn_with_sales.extract_price_info')
    @mock.patch('scrape_inflearn_with_sales.extract_rating')
    @mock.patch('scrape_inflearn_with_sales.extract_review_count')
    @mock.patch('scrape_inflearn_with_sales.extract_student_count')
    def test_extract_course_data_complete(
        self, mock_student, mock_review, mock_rating, mock_price,
        mock_thumbnail, mock_instructor, mock_title
    ):
        """완전한 강의 데이터 추출"""
        from scrape_inflearn_with_sales import extract_course_data

        # Mock 설정
        mock_link = mock.Mock()
        mock_link.get_attribute.return_value = "https://www.inflearn.com/course/test-course?token=abc"
        mock_link.locator.return_value = mock.Mock()

        mock_title.return_value = "테스트 강의"
        mock_instructor.return_value = "홍길동"
        mock_thumbnail.return_value = "https://example.com/thumb.jpg"
        mock_price.return_value = {
            'original_price': 77000,
            'sale_price': 55000,
            'discount_rate': 28,
            'is_on_sale': True
        }
        mock_rating.return_value = 4.5
        mock_review.return_value = 1234
        mock_student.return_value = 5000

        result = extract_course_data(mock_link, 0)

        assert result['url'] == "https://www.inflearn.com/course/test-course"
        assert result['course_id'] == "test-course"
        assert result['title'] == "테스트 강의"
        assert result['instructor'] == "홍길동"
        assert result['thumbnail_url'] == "https://example.com/thumb.jpg"
        assert result['original_price'] == 77000
        assert result['sale_price'] == 55000
        assert result['discount_rate'] == 28
        assert result['is_on_sale'] is True
        assert result['rating'] == 4.5
        assert result['review_count'] == 1234
        assert result['student_count'] == 5000
        assert result['source'] == 'inflearn'
        assert 'scraped_at' in result

    @mock.patch('scrape_inflearn_with_sales.extract_title')
    def test_extract_course_data_exception(self, mock_title):
        """강의 데이터 추출 중 예외 처리"""
        from scrape_inflearn_with_sales import extract_course_data

        # Mock 설정: 예외 발생
        mock_link = mock.Mock()
        mock_link.get_attribute.side_effect = Exception("추출 실패")

        result = extract_course_data(mock_link, 0)

        # 예외 발생 시 빈 딕셔너리 반환
        assert result == {}


class TestExtractAllCourses:
    """extract_all_courses() 함수 Mock 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    def test_extract_all_courses_success(self, mock_is_valid, mock_extract):
        """강의 목록 추출 성공"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 강의 링크
        mock_links = [mock.Mock() for _ in range(3)]

        # Mock extract_course_data 반환값
        mock_extract.side_effect = [
            {'title': '강의1', 'url': 'url1'},
            {'title': '강의2', 'url': 'url2'},
            {'title': '강의3', 'url': 'url3'}
        ]

        # Mock is_valid_course 반환값 (모두 유효)
        mock_is_valid.return_value = True

        courses, failed_courses = extract_all_courses(mock_links, max_courses=10, max_retries=2)

        assert len(courses) == 3
        assert len(failed_courses) == 0
        assert courses[0]['title'] == '강의1'
        assert courses[1]['title'] == '강의2'
        assert courses[2]['title'] == '강의3'

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    @mock.patch('pathlib.Path.exists', return_value=True)
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('json.dump')
    def test_extract_all_courses_with_failures(self, mock_json_dump, mock_file, mock_exists, mock_is_valid, mock_extract):
        """일부 강의 추출 실패"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 강의 링크
        mock_links = [mock.Mock() for _ in range(3)]

        # Mock extract_course_data 반환값 (2번째 실패)
        mock_extract.side_effect = [
            {'title': '강의1', 'url': 'url1'},
            Exception("추출 실패"),  # 2번째 강의 실패
            {'title': '강의3', 'url': 'url3'}
        ]

        # Mock is_valid_course 반환값
        mock_is_valid.side_effect = [True, True]

        courses, failed_courses = extract_all_courses(mock_links, max_courses=10, max_retries=0)

        assert len(courses) == 2  # 성공한 강의만
        assert len(failed_courses) == 1  # 실패한 강의
        assert failed_courses[0]['index'] == 2  # 2번째 강의 (0-based index 1)

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    def test_extract_all_courses_max_limit(self, mock_is_valid, mock_extract):
        """최대 강의 수 제한"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 강의 링크 (10개)
        mock_links = [mock.Mock() for _ in range(10)]

        # Mock extract_course_data 반환값
        mock_extract.return_value = {'title': '강의', 'url': 'url'}
        mock_is_valid.return_value = True

        courses, failed_courses = extract_all_courses(mock_links, max_courses=5, max_retries=2)

        # 최대 5개만 추출
        assert len(courses) == 5

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    def test_extract_all_courses_invalid_courses(self, mock_is_valid, mock_extract):
        """유효하지 않은 강의 필터링"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 강의 링크
        mock_links = [mock.Mock() for _ in range(3)]

        # Mock extract_course_data 반환값
        mock_extract.return_value = {'title': '강의', 'url': 'url'}

        # Mock is_valid_course 반환값 (2번째만 무효)
        mock_is_valid.side_effect = [True, False, True]

        courses, failed_courses = extract_all_courses(mock_links, max_courses=10, max_retries=2)

        # 유효한 강의만 포함
        assert len(courses) == 2
        # 유효성 검증 실패도 실패 목록에 포함
        assert len(failed_courses) == 1


if __name__ == "__main__":
    # 모든 테스트 실행
    pytest.main([__file__, "-v"])
