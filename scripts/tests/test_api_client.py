"""
Inflearn API Client 단위 테스트
"""

import pytest
from src.api_client import InflearnAPIClient


class TestInflearnAPIClient:
    """InflearnAPIClient 클래스 테스트"""

    def test_init(self):
        """API 클라이언트 초기화 테스트"""
        client = InflearnAPIClient(language="ko")

        assert client.language == "ko"
        assert client.BASE_URL == "https://course-api.inflearn.com/client/api/v2"
        assert "User-Agent" in client.session.headers
        assert "Accept" in client.session.headers
        assert client.session.headers['Accept-Language'] == "ko-KR,ko;q=0.9"

    def test_get_courses_success(self):
        """강의 목록 가져오기 성공 테스트"""
        client = InflearnAPIClient(language="ko")
        result = client.get_courses(page=1, size=10)

        # API 호출 성공 확인
        assert result is not None
        assert 'items' in result
        assert isinstance(result['items'], list)

        # 페이지 크기 확인 (최대 10개 요청)
        assert len(result['items']) <= 10

        # 필수 필드 확인
        if result['items']:
            item = result['items'][0]
            assert 'course' in item
            assert 'instructor' in item
            assert 'listPrice' in item

    def test_get_courses_with_category(self):
        """카테고리별 강의 목록 가져오기 테스트"""
        client = InflearnAPIClient(language="ko")
        result = client.get_courses(category="it-programming", page=1, size=5)

        assert result is not None
        assert 'items' in result
        assert len(result['items']) <= 5

    def test_normalize_course(self):
        """강의 데이터 정규화 테스트"""
        client = InflearnAPIClient()

        # 샘플 API 응답
        sample_item = {
            'course': {
                'id': 338674,
                'slug': 'test-course',
                'title': '테스트 강의',
                'star': 4.8,
                'reviewCount': 10,
                'studentCount': 795,
                'thumbnailUrl': 'https://example.com/thumb.jpg'
            },
            'instructor': {
                'name': '강사명'
            },
            'listPrice': {
                'regularPrice': 37400,
                'payPrice': 28050,
                'discountRate': 25.0
            }
        }

        normalized = client.normalize_course(sample_item)

        # 필드 존재 확인
        assert 'url' in normalized
        assert 'course_id' in normalized
        assert 'title' in normalized
        assert 'instructor' in normalized
        assert 'original_price' in normalized
        assert 'sale_price' in normalized
        assert 'discount_rate' in normalized
        assert 'rating' in normalized
        assert 'review_count' in normalized
        assert 'student_count' in normalized
        assert 'thumbnail' in normalized

        # 값 확인
        assert normalized['course_id'] == 338674
        assert normalized['title'] == '테스트 강의'
        assert normalized['instructor'] == '강사명'
        assert normalized['original_price'] == 37400
        assert normalized['sale_price'] == 28050
        assert normalized['discount_rate'] == 25.0
        assert normalized['rating'] == 4.8
        assert normalized['review_count'] == 10
        assert normalized['student_count'] == 795
        assert normalized['url'] == 'https://www.inflearn.com/course/test-course'

    def test_normalize_course_without_thumbnail(self):
        """썸네일 없는 강의 정규화 테스트"""
        client = InflearnAPIClient()

        sample_item = {
            'course': {
                'id': 1,
                'slug': 'test',
                'title': 'Test',
                'star': 5.0,
                'reviewCount': 0,
                'studentCount': 0
            },
            'instructor': {
                'name': 'Instructor'
            },
            'listPrice': {
                'regularPrice': 10000,
                'payPrice': 10000,
                'discountRate': 0.0
            }
        }

        normalized = client.normalize_course(sample_item)

        # 썸네일이 없으면 빈 문자열
        assert normalized['thumbnail'] == ''

    def test_get_all_courses(self):
        """여러 페이지 수집 테스트"""
        client = InflearnAPIClient(language="ko")
        courses = client.get_all_courses(max_courses=50)

        # 수집된 강의 확인
        assert isinstance(courses, list)
        assert len(courses) <= 50

        # 모든 강의가 필수 필드를 가지고 있는지 확인
        for course in courses:
            assert 'course_id' in course
            assert 'title' in course
            assert 'instructor' in course
            assert 'original_price' in course
            assert 'sale_price' in course
            assert 'url' in course

    def test_get_all_courses_small_batch(self):
        """소량 수집 테스트 (빠른 테스트)"""
        client = InflearnAPIClient(language="ko")
        courses = client.get_all_courses(max_courses=5)

        assert len(courses) <= 5
        assert all('title' in c for c in courses)

    def test_language_parameter(self):
        """언어 파라미터 테스트"""
        # 한국어 클라이언트
        client_ko = InflearnAPIClient(language="ko")
        assert client_ko.language == "ko"

        # 영어 클라이언트
        client_en = InflearnAPIClient(language="en")
        assert client_en.language == "en"


if __name__ == "__main__":
    # 간단한 수동 테스트
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    print("API Client 테스트 시작...")

    client = InflearnAPIClient(language="ko")
    print(f"[OK] 클라이언트 초기화: {client.language}")

    result = client.get_courses(page=1, size=5)
    if result:
        print(f"[OK] API 호출 성공: {len(result['items'])}개 강의")

    courses = client.get_all_courses(max_courses=10)
    print(f"[OK] 강의 수집 성공: {len(courses)}개")

    if courses:
        print(f"\n첫 번째 강의:")
        print(f"  제목: {courses[0]['title']}")
        print(f"  강사: {courses[0]['instructor']}")
        print(f"  가격: {courses[0]['original_price']:,}원")

    print("\n[OK] 모든 테스트 완료!")
