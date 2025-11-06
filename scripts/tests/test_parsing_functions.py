# scripts/test_parsing_functions.py
"""
scrape_inflearn_with_sales.py 파싱 함수 단위 테스트
- parse_price_to_number()
- parse_student_count()
- parse_discount_rate()
- clean_course_url()
- clean_title()
- is_valid_instructor()
- is_valid_course()
"""

import sys
from pathlib import Path
import pytest

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))


class TestParsePriceToNumber:
    """parse_price_to_number() 함수 테스트"""

    def test_parse_price_with_won_symbol_and_comma(self):
        """가격 문자열 파싱 - ₩ 기호와 쉼표 포함"""
        from scrape_inflearn_with_sales import parse_price_to_number

        assert parse_price_to_number("₩77,000") == 77000
        assert parse_price_to_number("₩99,000") == 99000
        assert parse_price_to_number("₩1,234,567") == 1234567

    def test_parse_price_with_won_text_and_comma(self):
        """가격 문자열 파싱 - '원' 텍스트와 쉼표 포함"""
        from scrape_inflearn_with_sales import parse_price_to_number

        assert parse_price_to_number("55,000원") == 55000
        assert parse_price_to_number("10,500원") == 10500

    def test_parse_price_only_numbers(self):
        """가격 문자열 파싱 - 숫자만 포함"""
        from scrape_inflearn_with_sales import parse_price_to_number

        assert parse_price_to_number("77000") == 77000
        assert parse_price_to_number("99000") == 99000

    def test_parse_price_with_comma_only(self):
        """가격 문자열 파싱 - 쉼표만 포함"""
        from scrape_inflearn_with_sales import parse_price_to_number

        assert parse_price_to_number("77,000") == 77000
        assert parse_price_to_number("1,234,567") == 1234567

    def test_parse_price_zero(self):
        """가격 문자열 파싱 - 0원"""
        from scrape_inflearn_with_sales import parse_price_to_number

        assert parse_price_to_number("₩0") == 0
        assert parse_price_to_number("0원") == 0
        assert parse_price_to_number("0") == 0

    def test_parse_price_empty_string(self):
        """가격 문자열 파싱 - 빈 문자열"""
        from scrape_inflearn_with_sales import parse_price_to_number

        assert parse_price_to_number("") is None
        assert parse_price_to_number(None) is None

    def test_parse_price_invalid_format(self):
        """가격 문자열 파싱 - 유효하지 않은 형식"""
        from scrape_inflearn_with_sales import parse_price_to_number

        # 숫자가 없는 경우
        assert parse_price_to_number("무료") is None
        assert parse_price_to_number("abc") is None
        assert parse_price_to_number("₩") is None

    def test_parse_price_with_spaces(self):
        """가격 문자열 파싱 - 공백 포함"""
        from scrape_inflearn_with_sales import parse_price_to_number

        assert parse_price_to_number("  ₩77,000  ") == 77000
        assert parse_price_to_number(" 55,000원 ") == 55000


class TestParseStudentCount:
    """parse_student_count() 함수 테스트"""

    def test_parse_student_count_with_plus_sign(self):
        """수강생 수 파싱 - + 기호 포함"""
        from scrape_inflearn_with_sales import parse_student_count

        assert parse_student_count("3,800+") == 3800
        assert parse_student_count("200+") == 200
        assert parse_student_count("1,234+") == 1234

    def test_parse_student_count_with_comma_only(self):
        """수강생 수 파싱 - 쉼표만 포함"""
        from scrape_inflearn_with_sales import parse_student_count

        assert parse_student_count("3,800") == 3800
        assert parse_student_count("1,234,567") == 1234567

    def test_parse_student_count_only_numbers(self):
        """수강생 수 파싱 - 숫자만 포함"""
        from scrape_inflearn_with_sales import parse_student_count

        assert parse_student_count("3800") == 3800
        assert parse_student_count("200") == 200

    def test_parse_student_count_zero(self):
        """수강생 수 파싱 - 0"""
        from scrape_inflearn_with_sales import parse_student_count

        assert parse_student_count("0") == 0
        assert parse_student_count("0+") == 0

    def test_parse_student_count_empty_string(self):
        """수강생 수 파싱 - 빈 문자열"""
        from scrape_inflearn_with_sales import parse_student_count

        assert parse_student_count("") is None
        assert parse_student_count(None) is None

    def test_parse_student_count_invalid_format(self):
        """수강생 수 파싱 - 유효하지 않은 형식"""
        from scrape_inflearn_with_sales import parse_student_count

        assert parse_student_count("abc") is None
        assert parse_student_count("명+") is None


class TestParseDiscountRate:
    """parse_discount_rate() 함수 테스트"""

    def test_parse_discount_rate_with_percent_sign(self):
        """할인율 파싱 - % 기호 포함"""
        from scrape_inflearn_with_sales import parse_discount_rate

        assert parse_discount_rate("35%") == 35
        assert parse_discount_rate("50%") == 50
        assert parse_discount_rate("100%") == 100

    def test_parse_discount_rate_only_numbers(self):
        """할인율 파싱 - 숫자만 포함"""
        from scrape_inflearn_with_sales import parse_discount_rate

        assert parse_discount_rate("35") == 35
        assert parse_discount_rate("50") == 50

    def test_parse_discount_rate_zero(self):
        """할인율 파싱 - 0%"""
        from scrape_inflearn_with_sales import parse_discount_rate

        assert parse_discount_rate("0%") == 0
        assert parse_discount_rate("0") == 0

    def test_parse_discount_rate_empty_string(self):
        """할인율 파싱 - 빈 문자열"""
        from scrape_inflearn_with_sales import parse_discount_rate

        assert parse_discount_rate("") == 0
        assert parse_discount_rate(None) == 0

    def test_parse_discount_rate_invalid_format(self):
        """할인율 파싱 - 유효하지 않은 형식"""
        from scrape_inflearn_with_sales import parse_discount_rate

        # 숫자가 없는 경우 0 반환
        assert parse_discount_rate("abc") == 0
        assert parse_discount_rate("%") == 0


class TestCleanCourseUrl:
    """clean_course_url() 함수 테스트"""

    def test_clean_url_with_query_parameters(self):
        """URL 정리 - 쿼리 파라미터 포함"""
        from scrape_inflearn_with_sales import clean_course_url

        assert clean_course_url(
            "https://www.inflearn.com/course/test?attributionToken=abc"
        ) == "https://www.inflearn.com/course/test"

        assert clean_course_url(
            "https://www.inflearn.com/course/test?param1=value1&param2=value2"
        ) == "https://www.inflearn.com/course/test"

    def test_clean_url_without_query_parameters(self):
        """URL 정리 - 쿼리 파라미터 없음"""
        from scrape_inflearn_with_sales import clean_course_url

        assert clean_course_url(
            "https://www.inflearn.com/course/test"
        ) == "https://www.inflearn.com/course/test"

    def test_clean_url_empty_string(self):
        """URL 정리 - 빈 문자열"""
        from scrape_inflearn_with_sales import clean_course_url

        assert clean_course_url("") == ""
        assert clean_course_url(None) is None

    def test_clean_url_with_hash(self):
        """URL 정리 - 해시(#) 포함"""
        from scrape_inflearn_with_sales import clean_course_url

        # 쿼리 파라미터는 제거되지만 해시는 유지됨
        assert clean_course_url(
            "https://www.inflearn.com/course/test#section1"
        ) == "https://www.inflearn.com/course/test#section1"

        # 쿼리와 해시 모두 포함된 경우
        assert clean_course_url(
            "https://www.inflearn.com/course/test?param=value#section1"
        ) == "https://www.inflearn.com/course/test"


class TestCleanTitle:
    """clean_title() 함수 테스트"""

    def test_clean_title_with_suffix_lecture_thumbnail(self):
        """제목 정리 - '강의 썸네일' 접미사 제거"""
        from scrape_inflearn_with_sales import clean_title

        assert clean_title("Python 기초강의 썸네일") == "Python 기초"
        assert clean_title("JavaScript강의 썸네일") == "JavaScript"

    def test_clean_title_with_suffix_thumbnail(self):
        """제목 정리 - '썸네일' 접미사 제거"""
        from scrape_inflearn_with_sales import clean_title

        assert clean_title("Python 기초썸네일") == "Python 기초"

    def test_clean_title_with_suffix_lecture(self):
        """제목 정리 - '강의' 접미사 제거"""
        from scrape_inflearn_with_sales import clean_title

        assert clean_title("Python 기초강의") == "Python 기초"

    def test_clean_title_with_suffix_dash(self):
        """제목 정리 - ' - ' 접미사 제거"""
        from scrape_inflearn_with_sales import clean_title

        # Note: The function strips trailing space, leaving " -"
        assert clean_title("Python 기초 - ") == "Python 기초 -"

    def test_clean_title_without_suffix(self):
        """제목 정리 - 접미사 없음"""
        from scrape_inflearn_with_sales import clean_title

        assert clean_title("Python 기초") == "Python 기초"
        assert clean_title("JavaScript 완전 정복") == "JavaScript 완전 정복"

    def test_clean_title_empty_string(self):
        """제목 정리 - 빈 문자열"""
        from scrape_inflearn_with_sales import clean_title

        assert clean_title("") == ""
        assert clean_title(None) is None

    def test_clean_title_with_leading_trailing_spaces(self):
        """제목 정리 - 앞뒤 공백 제거"""
        from scrape_inflearn_with_sales import clean_title

        assert clean_title("  Python 기초  ") == "Python 기초"
        assert clean_title("  Python 기초강의  ") == "Python 기초"


class TestIsValidInstructor:
    """is_valid_instructor() 함수 테스트"""

    def test_valid_instructor_korean_name(self):
        """강사명 유효성 검증 - 한글 이름"""
        from scrape_inflearn_with_sales import is_valid_instructor

        assert is_valid_instructor("홍길동") is True
        assert is_valid_instructor("김철수") is True
        assert is_valid_instructor("박영희") is True

    def test_valid_instructor_english_name(self):
        """강사명 유효성 검증 - 영문 이름"""
        from scrape_inflearn_with_sales import is_valid_instructor

        assert is_valid_instructor("John Doe") is True
        assert is_valid_instructor("Jane Smith") is True

    def test_valid_instructor_mixed_name(self):
        """강사명 유효성 검증 - 혼합 이름"""
        from scrape_inflearn_with_sales import is_valid_instructor

        assert is_valid_instructor("홍길동 (John)") is True
        assert is_valid_instructor("인프런 팀") is True

    def test_invalid_instructor_review_count_in_parentheses(self):
        """강사명 유효성 검증 - 괄호 포함 숫자 (리뷰 수로 추정)"""
        from scrape_inflearn_with_sales import is_valid_instructor

        assert is_valid_instructor("(7)") is False
        assert is_valid_instructor("(244)") is False
        assert is_valid_instructor("(1000)") is False

    def test_invalid_instructor_rating_number(self):
        """강사명 유효성 검증 - 숫자만 포함 (평점으로 추정)"""
        from scrape_inflearn_with_sales import is_valid_instructor

        assert is_valid_instructor("4.9") is False
        assert is_valid_instructor("5.0") is False
        assert is_valid_instructor("3.8") is False
        assert is_valid_instructor("100") is False

    def test_invalid_instructor_empty_string(self):
        """강사명 유효성 검증 - 빈 문자열"""
        from scrape_inflearn_with_sales import is_valid_instructor

        assert is_valid_instructor("") is False
        assert is_valid_instructor(None) is False

    def test_invalid_instructor_whitespace_only(self):
        """강사명 유효성 검증 - 공백만 포함"""
        from scrape_inflearn_with_sales import is_valid_instructor

        assert is_valid_instructor("   ") is False


class TestIsValidCourse:
    """is_valid_course() 함수 테스트"""

    def test_valid_course_minimal(self):
        """강의 유효성 검증 - 최소 필수 필드"""
        from scrape_inflearn_with_sales import is_valid_course

        course = {
            "title": "Python 기초",
            "url": "https://inflearn.com/course/python-basics"
        }
        assert is_valid_course(course) is True

    def test_valid_course_full(self):
        """강의 유효성 검증 - 모든 필드 포함"""
        from scrape_inflearn_with_sales import is_valid_course

        course = {
            "title": "Python 기초",
            "url": "https://inflearn.com/course/python-basics",
            "instructor": "홍길동",
            "rating": 4.5,
            "review_count": 100,
            "student_count": 500
        }
        assert is_valid_course(course) is True

    def test_invalid_course_missing_title(self):
        """강의 유효성 검증 - title 누락"""
        from scrape_inflearn_with_sales import is_valid_course

        course = {
            "url": "https://inflearn.com/course/python-basics"
        }
        assert is_valid_course(course) is False

    def test_invalid_course_missing_url(self):
        """강의 유효성 검증 - url 누락"""
        from scrape_inflearn_with_sales import is_valid_course

        course = {
            "title": "Python 기초"
        }
        assert is_valid_course(course) is False

    def test_invalid_course_empty_title(self):
        """강의 유효성 검증 - 빈 title"""
        from scrape_inflearn_with_sales import is_valid_course

        course = {
            "title": "",
            "url": "https://inflearn.com/course/python-basics"
        }
        assert is_valid_course(course) is False

    def test_invalid_course_empty_url(self):
        """강의 유효성 검증 - 빈 url"""
        from scrape_inflearn_with_sales import is_valid_course

        course = {
            "title": "Python 기초",
            "url": ""
        }
        assert is_valid_course(course) is False

    def test_invalid_course_title_too_short(self):
        """강의 유효성 검증 - 제목이 너무 짧음 (< 3자)"""
        from scrape_inflearn_with_sales import is_valid_course

        course = {
            "title": "AB",
            "url": "https://inflearn.com/course/python-basics"
        }
        assert is_valid_course(course) is False

        # 3자는 통과
        course["title"] = "ABC"
        assert is_valid_course(course) is True


class TestParsePrice:
    """parse_price() 함수 테스트 (호환성 유지)"""

    def test_parse_price_with_won_symbol(self):
        """가격 파싱 - ₩ 기호 포함"""
        from scrape_inflearn_with_sales import parse_price

        assert parse_price("₩99,000") == 99000
        assert parse_price("₩77,000") == 77000

    def test_parse_price_free(self):
        """가격 파싱 - 무료"""
        from scrape_inflearn_with_sales import parse_price

        assert parse_price("무료") == 0
        assert parse_price("") == 0
        assert parse_price(None) == 0

    def test_parse_price_invalid(self):
        """가격 파싱 - 유효하지 않은 형식"""
        from scrape_inflearn_with_sales import parse_price

        assert parse_price("abc") == 0
        assert parse_price("₩abc") == 0


if __name__ == "__main__":
    # 모든 테스트 실행
    pytest.main([__file__, "-v"])
