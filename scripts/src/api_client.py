"""
Inflearn API Client
API 직접 호출을 통한 강의 데이터 수집
"""

import requests
from typing import List, Dict, Optional
import time
import logging

logger = logging.getLogger(__name__)


class InflearnAPIClient:
    """Inflearn API 클라이언트"""

    BASE_URL = "https://course-api.inflearn.com/client/api/v2"

    def __init__(self, language: str = "ko"):
        """
        API 클라이언트 초기화

        Args:
            language: 응답 언어 (ko/en)
        """
        self.language = language
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': f'{language}-KR,{language};q=0.9',
            'Referer': 'https://www.inflearn.com/'
        })

    def get_courses(
        self,
        category: str = "it-programming",
        page: int = 1,
        size: int = 40
    ) -> Optional[Dict]:
        """
        강의 목록 가져오기

        Args:
            category: 카테고리 (it-programming, ai, design 등)
            page: 페이지 번호 (1부터 시작)
            size: 페이지 크기 (최대 40)

        Returns:
            API 응답 데이터 (data 필드) 또는 None (실패 시)
        """
        url = f"{self.BASE_URL}/courses/search"
        params = {
            'categories': category,
            'pageNumber': page,
            'pageSize': size,
            'sort': 'RECOMMEND',
            'types': 'ONLINE,OFFLINE',
            'lang': self.language,  # 핵심! 언어 제어
            'isBot': 'false',
            'isDiscounted': 'false',
            'isEarlybirdDiscounted': 'false',
            'keyword': ''
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # API 상태 코드 확인
            if data.get('statusCode') != 'OK':
                logger.error(f"❌ API 에러: {data.get('message', 'Unknown error')}")
                return None

            logger.info(f"✅ Page {page}: {len(data['data']['items'])}개 강의 수집")
            return data['data']

        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout: API 응답 시간 초과 (page={page})")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error {e.response.status_code}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API 호출 실패: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            return None

    def normalize_course(self, item: Dict) -> Dict:
        """
        API 응답을 현재 데이터 구조로 변환

        Args:
            item: API 응답의 items 배열 요소

        Returns:
            정규화된 강의 데이터
        """
        course = item['course']
        instructor = item['instructor']
        price = item['listPrice']

        return {
            'url': f"https://www.inflearn.com/course/{course['slug']}",
            'course_id': course['id'],
            'title': course['title'],
            'instructor': instructor['name'],
            'original_price': price['regularPrice'],
            'sale_price': price['payPrice'],
            'discount_rate': price['discountRate'],
            'rating': course['star'],
            'review_count': course['reviewCount'],
            'student_count': course['studentCount'],
            'thumbnail': course.get('thumbnailUrl', ''),
        }

    def get_all_courses(
        self,
        max_courses: int = 200,
        category: str = "it-programming"
    ) -> List[Dict]:
        """
        여러 페이지의 강의 목록 수집

        Args:
            max_courses: 수집할 최대 강의 수
            category: 카테고리

        Returns:
            정규화된 강의 데이터 리스트
        """
        all_courses = []
        page = 1

        logger.info(f"🔍 강의 수집 시작 (목표: {max_courses}개)")

        while len(all_courses) < max_courses:
            result = self.get_courses(category=category, page=page, size=40)

            # API 호출 실패 시 중단
            if not result or not result.get('items'):
                logger.warning(f"⚠️ Page {page}에서 데이터 없음, 수집 종료")
                break

            # 강의 정규화 및 추가
            for item in result['items']:
                try:
                    normalized = self.normalize_course(item)
                    all_courses.append(normalized)

                    if len(all_courses) >= max_courses:
                        break

                except (KeyError, TypeError) as e:
                    logger.error(f"❌ 강의 정규화 실패: {e}")
                    continue

            logger.info(f"📊 진행: {len(all_courses)}/{max_courses} 수집 완료")

            # 다음 페이지로
            page += 1

            # Rate limit 예방 (초당 2회로 제한)
            time.sleep(0.5)

        logger.info(f"✅ 수집 완료: 총 {len(all_courses)}개 강의")
        return all_courses[:max_courses]
