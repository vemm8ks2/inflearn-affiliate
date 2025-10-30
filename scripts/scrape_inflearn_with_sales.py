# scripts/scrape_inflearn_with_sales.py
"""
인프런 강의 스크래핑 스크립트 (개선 버전)
- 안정적인 선택자 사용
- 로깅 시스템 적용
- 함수 분리 및 모듈화
- 설정 관리 개선
"""

from playwright.sync_api import sync_playwright, Locator
import json
import time
import re
from datetime import datetime
from typing import Dict, Optional, List, Any

# 로컬 모듈 import
from logger_config import logger
from config import config


# ============================================================================
# 데이터 추출 헬퍼 함수들
# ============================================================================

def extract_with_fallback(link: Locator, selectors: List[str], validator=None) -> Optional[str]:
    """
    여러 선택자를 순차적으로 시도하여 텍스트 추출

    Args:
        link: Playwright Locator 객체
        selectors: 시도할 선택자 리스트
        validator: 추출한 텍스트 검증 함수 (optional)

    Returns:
        추출된 텍스트 또는 None
    """
    for selector in selectors:
        try:
            elem = link.locator(selector).first
            if elem:
                text = elem.text_content(timeout=config.ELEMENT_TIMEOUT)
                if text and text.strip():
                    text = text.strip()
                    if validator is None or validator(text):
                        return text
        except Exception as e:
            logger.debug(f"선택자 실패 ({selector}): {e}")
            continue
    return None


def extract_title(entry_elem: Locator) -> Optional[str]:
    """
    강의 제목 추출

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        제목 문자열 또는 None
    """

    try:
        title_elem = entry_elem.locator('div:nth-child(2) > div:nth-child(1) > p:nth-child(1)').first
        title = title_elem.text_content(timeout=config.ELEMENT_TIMEOUT) 

        return title
    except Exception as e:
        logger.debug(f"제목 추출 실패: {e}")

    return None


def clean_title(title: str) -> str:
    """
    제목 정제 (불필요한 접미사 제거)

    ✅ Phase 1.1: "강의 썸네일" 등 불필요한 접미사 제거

    Args:
        title: 원본 제목 문자열

    Returns:
        정제된 제목 문자열
    """
    if not title:
        return title

    # 제거할 접미사 목록
    suffixes = ["강의 썸네일", "썸네일", "강의", " - "]

    cleaned = title.strip()
    for suffix in suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()

    return cleaned


def is_valid_instructor(instructor: str) -> bool:
    """
    강사명 유효성 검증

    Args:
        instructor: 검증할 강사명 문자열

    Returns:
        유효한 강사명이면 True, 아니면 False
    """
    if not instructor:
        return False

    # ✅ Phase 1.1: 검증 강화 - 괄호 포함 숫자 거부 (리뷰 수: "(7)", "(244)")
    if re.match(r'^\(\d+\)$', instructor):
        logger.debug(f"강사명 검증 실패: 괄호 포함 숫자 (리뷰 수로 추정) - '{instructor}'")
        return False

    # 숫자만 있으면 거부 (평점 오인: "4.9", "5.0" 등)
    if re.match(r'^\d+(\.\d+)?$', instructor):
        logger.debug(f"강사명 검증 실패: 숫자만 포함 (평점으로 추정) - '{instructor}'")
        return False

    # 퍼센트 포함 거부 (할인율 오인: "35%", "25%" 등)
    if '%' in instructor:
        logger.debug(f"강사명 검증 실패: 퍼센트 포함 (할인율로 추정) - '{instructor}'")
        return False

    # ✅ Phase 1.2: 검증 강화 - 원화 심볼 거부 (가격: "₩165,000", "₩31,460")
    if '₩' in instructor:
        logger.debug(f"강사명 검증 실패: 원화 심볼 포함 (가격으로 추정) - '{instructor}'")
        return False

    # ✅ Phase 1.1: 검증 강화 - "일만" 패턴 거부 (할인 기간: "8일만", "6일만")
    if re.search(r'\d+일만', instructor):
        logger.debug(f"강사명 검증 실패: 할인 기간 패턴 - '{instructor}'")
        return False

    # ✅ Phase 1.1: 검증 강화 - 단일 기술 이름 거부 (카테고리: "C++", "Java")
    if not re.search(r'[가-힣]', instructor) and len(instructor) <= 5:
        logger.debug(f"강사명 검증 실패: 기술 이름으로 추정 - '{instructor}'")
        return False

    # 최소 2자, 최대 50자 (한글 이름 2-10자, 영문 이름 더 긴 경우 고려)
    if not (2 <= len(instructor) <= 50):
        logger.debug(f"강사명 검증 실패: 길이 부적절 ({len(instructor)}자) - '{instructor}'")
        return False

    return True


def extract_instructor(entry_elem: Locator) -> Optional[str]:
    """
    강사명 추출

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        강사명 또는 None
    """
    
    try:
        instructor_elem = entry_elem.locator('div:nth-child(2) > div:nth-child(1) > p:nth-child(2)').first
        instructor = instructor_elem.text_content(timeout=config.ELEMENT_TIMEOUT)

        return instructor
    except Exception as e:
        logger.debug(f"강사명 추출 실패: {e}")

    return None


def extract_thumbnail(entry_elem: Locator) -> Optional[str]:
    """
    썸네일 이미지 URL 추출

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        이미지 URL 또는 None
    """
    try:
        img_elem = entry_elem.locator('picture img').first
        if img_elem:
            img_src = img_elem.get_attribute('src')
            if img_src:
                return img_src
    except Exception as e:
        logger.debug(f"썸네일 추출 실패: {e}")

    return None


def parse_price(price_text: str) -> int:
    """
    가격 문자열을 정수로 변환

    Args:
        price_text: "₩99,000" 형식의 문자열

    Returns:
        정수 가격 (무료는 0)
    """
    if not price_text or price_text == '무료':
        return 0
    try:
        return int(price_text.replace('₩', '').replace(',', '').strip())
    except ValueError:
        return 0


def extract_price_info(entry_elem: Locator) -> Dict[str, Optional[Any]]:
    """
    가격 정보 추출 (정가, 할인가, 할인율)

    Args:
        link: 강의 링크 Locator

    Returns:
        가격 정보 딕셔너리
    """
    result = {
        'original_price': None,
        'sale_price': None,
        'discount_rate': None,
    }

    try:
        first_price = None
        first_price_elem = entry_elem.locator('div:nth-child(2) > div:nth-child(2) > div > div:nth-child(1) > p').first

        has_first_price = first_price_elem.count() > 0

        if has_first_price:
            first_price = first_price_elem.text_content(timeout=config.ELEMENT_TIMEOUT) # first_price는 존재하거나 존재하지 않으며, 만약 존재한다면 그것은 할인 전 가격이다.

        second_price_selector = 'div:nth-child(2) > div:nth-child(2) > div > div:nth-child(2) > p'
        discount_rate_selector = None

        if first_price: # 만약 first_price_selector가 존재하면 할인 중인 강의
            discount_rate_selector = 'div:nth-child(2) > div:nth-child(2) > div > div:nth-child(2) > p:nth-child(2)'
            second_price_selector = 'div:nth-child(2) > div:nth-child(2) > div > div:nth-child(2) > p:nth-child(3)'

        second_price_elem = entry_elem.locator(second_price_selector).first
        second_price = second_price_elem.text_content(timeout=config.ELEMENT_TIMEOUT) # second_price는 항상 존재하며 만약 first_price가 있다면 할인 후 가격이고, 없다면 할인 전 가격이다.

        if discount_rate_selector:
            discount_rate_elem = entry_elem.locator(discount_rate_selector).first
            discount_rate = discount_rate_elem.text_content(timeout=config.ELEMENT_TIMEOUT) 

        if first_price:
            result['original_price'] = first_price
            result['sale_price'] = second_price
            result['discount_rate'] = discount_rate
        else:
            result['original_price'] = second_price
            result['sale_price'] = None
            result['discount_rate'] = None

        return result
    except Exception as e:
        logger.debug(f"가격 정보 추출 실패: {e}")

    # None 대신 기본 구조 반환 (dict unpacking TypeError 방지)
    return {
        'original_price': None,
        'sale_price': None,
        'discount_rate': None,
    }


def extract_rating(entry_elem: Locator) -> Optional[float]:
    """
    평점 추출

    Args:
        link: 강의 링크 Locator

    Returns:
        평점 (0-5) 또는 None
    """
    try:
        rating_elem = entry_elem.locator('div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(1) > div > p').first
        rating = rating_elem.text_content(timeout=config.ELEMENT_TIMEOUT)

        return rating
    except Exception as e:
        logger.debug(f"평점 추출 실패: {e}")

    return None


def extract_review_count(entry_elem: Locator) -> Optional[int]:
    """
    리뷰 수 추출

    Args:
        link: 강의 링크 Locator

    Returns:
        리뷰 수 또는 None
    """
    try:
        review_count_elem = entry_elem.locator('div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(1) > p').first
        review_count = review_count_elem.text_content(timeout=config.ELEMENT_TIMEOUT)

        return review_count
    except Exception as e:
        logger.debug(f"리뷰 수 추출 실패: {e}")

    return None


def extract_student_count(entry_elem: Locator) -> Optional[str]:
    """
    수강생 수 추출

    Args:
        link: 강의 링크 Locator

    Returns:
        수강생 수 문자열 또는 None
    """
    try:
        student_count_elem = entry_elem.locator('div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(2) > span').first
        student_count = student_count_elem.text_content(timeout=config.ELEMENT_TIMEOUT)

        return student_count
    except Exception as e:
        logger.debug(f"수강생 수 추출 실패: {e}")

    return None


def extract_course_data(link: Locator, idx: int) -> Dict[str, Any]:
    """
    강의 하나의 모든 데이터 추출

    Args:
        link: 강의 링크 Locator
        idx: 강의 인덱스

    Returns:
        강의 데이터 딕셔너리
    """
    try:
        # URL 및 course_id
        url = link.get_attribute('href')
        course_id = None

        if url:
            course_id = url.split('/course/')[-1].split('?')[0]

        entry_elem = link.locator('div > div:nth-child(2) > div > article')

        # 모든 필드 추출
        course = {
            'url': url,
            'course_id': course_id,
            'title': extract_title(entry_elem),
            'instructor': extract_instructor(entry_elem),
            'thumbnail_url': extract_thumbnail(entry_elem),
            **extract_price_info(entry_elem),
            'rating': extract_rating(entry_elem),
            'review_count': extract_review_count(entry_elem),
            'student_count': extract_student_count(entry_elem),
            'scraped_at': datetime.now().isoformat(),
            'source': 'inflearn',
        }

        return course

    except Exception as e:
        logger.error(f"강의 {idx+1} 데이터 추출 실패", exc_info=True)
        return {}


def is_valid_course(course: Dict[str, Any]) -> bool:
    """
    강의 데이터 유효성 검증

    Args:
        course: 강의 데이터 딕셔너리

    Returns:
        유효 여부
    """
    if not course.get('title') or not course.get('url'):
        return False

    # 제목 길이 검증
    if len(course.get('title', '')) < 3:
        logger.warning(f"제목이 너무 짧음: {course.get('title')}")
        return False

    return True


def log_course_info(course: Dict[str, Any], idx: int):
    """
    수집한 강의 정보 로깅

    Args:
        course: 강의 데이터
        idx: 인덱스
    """
    logger.info(f"  [{idx+1}] {course.get('title', 'N/A')[:40]}...")
    logger.info(f"       강사: {course.get('instructor', 'N/A')}")

    # 가격 정보 출력
    if course.get('sale_price'):
        logger.info(f"       정가: {course.get('original_price', 'N/A')}, "
                   f"할인가: {course.get('sale_price')}, "
                   f"할인율: {course.get('discount_rate', 'N/A')}%")
    else:
        logger.info(f"       가격: {course.get('original_price', 'N/A')}")

    logger.info(f"       평점: {course.get('rating', 'N/A')}, "
               f"리뷰: {course.get('review_count', 'N/A')}, "
               f"수강생: {course.get('student_count', 'N/A')}")


# ============================================================================
# 메인 스크래핑 함수
# ============================================================================

def scrape_inflearn_courses(max_courses: Optional[int] = None, headless: Optional[bool] = None) -> List[Dict]:
    """
    인프런 강의 목록 스크래핑 (리팩토링 버전)

    Args:
        max_courses: 수집할 최대 강의 수 (기본값: config.MAX_COURSES)
        headless: 브라우저 숨김 모드 (기본값: config.HEADLESS)

    Returns:
        강의 정보 딕셔너리 리스트
    """
    # 기본값 설정
    max_courses = max_courses if max_courses is not None else config.MAX_COURSES
    headless = headless if headless is not None else config.HEADLESS

    logger.info("=" * 60)
    logger.info("🚀 인프런 강의 스크래핑 시작")
    logger.info(f"설정: max_courses={max_courses}, headless={headless}")
    logger.info("=" * 60)

    courses = []

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            # 페이지 이동
            url = f"{config.BASE_URL}/{config.CATEGORY}"
            logger.info(f"🌐 페이지 접속 중: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=config.PAGE_LOAD_TIMEOUT)
            time.sleep(2)

            # 스크롤하여 콘텐츠 로드
            logger.info("📜 페이지 스크롤 중...")
            for i in range(3):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(config.SCROLL_DELAY)
                logger.debug(f"스크롤 {i+1}/3 완료")

            # 강의 링크 수집
            logger.info("🔍 강의 링크 수집 중...")
            course_links = page.locator('li > a[href*="/course/"]').all()
            logger.info(f"✅ {len(course_links)}개의 강의 발견")

            # 데이터 추출
            logger.info(f"📊 데이터 추출 중 (최대 {max_courses}개)...")
            for idx, link in enumerate(course_links[:max_courses]):
                try:
                    course_data = extract_course_data(link, idx)

                    if is_valid_course(course_data):
                        courses.append(course_data)
                        log_course_info(course_data, idx)
                    else:
                        logger.warning(f"강의 {idx+1} 검증 실패")

                except Exception as e:
                    logger.error(f"강의 {idx+1} 처리 중 오류: {e}", exc_info=True)
                    continue

            # 디버그 파일 저장
            logger.info("💾 디버그 파일 저장 중...")
            page.screenshot(path=config.SCREENSHOT_PATH)
            logger.info(f"스크린샷 저장: {config.SCREENSHOT_PATH}")

            html_content = page.content()
            with open(config.HTML_SOURCE_PATH, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML 소스 저장: {config.HTML_SOURCE_PATH}")

        except Exception as e:
            logger.error(f"스크래핑 중 치명적 오류 발생: {e}", exc_info=True)

        finally:
            browser.close()
            logger.debug("브라우저 종료")

    logger.info(f"\n✅ 총 {len(courses)}개 강의 수집 완료")
    return courses


def save_to_json(courses: List[Dict], filename: Optional[str] = None):
    """
    수집한 강의 데이터를 JSON 파일로 저장

    Args:
        courses: 강의 데이터 리스트
        filename: 저장할 파일 경로 (기본값: config.JSON_OUTPUT)
    """
    filename = filename or config.JSON_OUTPUT

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(courses, f, ensure_ascii=False, indent=2)
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
        # 스크래핑 실행
        courses = scrape_inflearn_courses()

        if courses:
            # JSON 저장
            save_to_json(courses)

            # 결과 요약
            print_summary(courses)
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
