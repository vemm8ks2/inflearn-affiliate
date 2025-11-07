# scripts/src/scraper.py
"""
인프런 강의 스크래핑 스크립트 (개선 버전)
- 안정적인 선택자 사용
- 로깅 시스템 적용
- 함수 분리 및 모듈화
- 설정 관리 개선
"""

from playwright.sync_api import sync_playwright, Locator, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import json
import time
import re
from datetime import datetime, timezone
from typing import Dict, Optional, List, Any

# 로컬 모듈 import
from src.logger_config import logger
from src.config import config
from src.db_utils import upsert_courses


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


def extract_text_by_selector(
    entry_elem: Locator,
    selector: str,
    field_name: str,
    timeout: int = None
) -> Optional[str]:
    """
    셀렉터로 텍스트 추출하는 공통 함수 (타임아웃 재시도 포함)

    Args:
        entry_elem: 강의 요소 Locator
        selector: CSS 셀렉터
        field_name: 필드명 (로깅용)
        timeout: 타임아웃 (기본값: config.ELEMENT_TIMEOUT)

    Returns:
        추출된 텍스트 또는 None
    """
    timeout = timeout or config.ELEMENT_TIMEOUT

    # 재시도 로직: 타임아웃 시 최대 MAX_RETRIES번 재시도
    for attempt in range(config.MAX_RETRIES + 1):
        try:
            elem = entry_elem.locator(selector).first
            if elem:
                value = elem.text_content(timeout=timeout)
                return value.strip() if value else None
        except PlaywrightTimeoutError:
            if attempt < config.MAX_RETRIES:
                logger.debug(f"{field_name} 추출 타임아웃 - 재시도 {attempt + 1}/{config.MAX_RETRIES}")
                time.sleep(config.RETRY_DELAY)
                continue
            else:
                logger.debug(f"{field_name} 추출 타임아웃 (재시도 {config.MAX_RETRIES}회 실패)")
        except AttributeError:
            logger.debug(f"{field_name} 요소 없음 (페이지 구조 변경 가능)")
            break  # 재시도 불필요
        except PlaywrightError as e:
            logger.warning(f"{field_name} 추출 실패 (Playwright 오류): {e}")
            break  # 재시도 불필요
        except Exception as e:
            logger.error(f"{field_name} 추출 중 예상치 못한 오류: {e}", exc_info=True)
            break  # 재시도 불필요

    return None


def extract_title(entry_elem: Locator) -> Optional[str]:
    """
    강의 제목 추출

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        제목 문자열 또는 None
    """
    return extract_text_by_selector(entry_elem, config.SELECTORS['title'], "제목")


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
    return extract_text_by_selector(entry_elem, config.SELECTORS['instructor'], "강사명")


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
    except PlaywrightTimeoutError:
        logger.debug("썸네일 추출 타임아웃 (요소 로드 지연)")
    except AttributeError:
        logger.debug("썸네일 요소 없음 (페이지 구조 변경 가능)")
    except PlaywrightError as e:
        logger.warning(f"썸네일 추출 실패 (Playwright 오류): {e}")
    except Exception as e:
        logger.error(f"썸네일 추출 중 예상치 못한 오류: {e}", exc_info=True)

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


def parse_price_to_number(price_text: str) -> Optional[int]:
    """
    가격 문자열을 숫자로 변환

    Args:
        price_text: 가격 문자열 (예: "₩77,000", "77000원")

    Returns:
        변환된 가격 (숫자) 또는 None

    Examples:
        >>> parse_price_to_number("₩77,000")
        77000
        >>> parse_price_to_number("55,000원")
        55000
    """
    if not price_text:
        return None

    try:
        # 숫자가 아닌 모든 문자 제거 (₩, 원, 쉼표 등)
        clean_text = ''.join(char for char in price_text if char.isdigit())
        if clean_text:
            return int(clean_text)
    except (ValueError, AttributeError) as e:
        logger.debug(f"가격 변환 실패 ('{price_text}'): {e}")

    return None


def parse_student_count(count_text: str) -> Optional[int]:
    """
    수강생 수 문자열을 숫자로 변환

    Args:
        count_text: 수강생 수 문자열 (예: "3,800+", "200+")

    Returns:
        변환된 수강생 수 (숫자) 또는 None

    Examples:
        >>> parse_student_count("3,800+")
        3800
        >>> parse_student_count("200+")
        200
    """
    if not count_text:
        return None

    try:
        # 숫자와 쉼표만 추출 후 쉼표 제거 ('+' 제거)
        clean_text = ''.join(char for char in count_text if char.isdigit() or char == ',')
        clean_text = clean_text.replace(',', '')
        if clean_text:
            return int(clean_text)
    except (ValueError, AttributeError) as e:
        logger.debug(f"수강생 수 변환 실패 ('{count_text}'): {e}")

    return None


def parse_discount_rate(discount_text: str) -> int:
    """
    할인율 문자열을 숫자로 변환

    Args:
        discount_text: 할인율 문자열 (예: "35%", "50%")

    Returns:
        변환된 할인율 (숫자, 0-100) 또는 0

    Examples:
        >>> parse_discount_rate("35%")
        35
        >>> parse_discount_rate("50%")
        50
        >>> parse_discount_rate(None)
        0
    """
    if not discount_text:
        return 0

    try:
        # % 기호 제거 후 숫자만 추출
        clean_text = ''.join(char for char in discount_text if char.isdigit())
        if clean_text:
            return int(clean_text)
    except (ValueError, AttributeError) as e:
        logger.debug(f"할인율 변환 실패 ('{discount_text}'): {e}")

    return 0


def clean_course_url(url: str) -> str:
    """
    URL에서 쿼리 파라미터 제거 (추적 파라미터 정규화)

    Args:
        url: 원본 URL (쿼리 파라미터 포함 가능)

    Returns:
        정규화된 URL (쿼리 파라미터 제거됨)

    Examples:
        >>> clean_course_url("https://www.inflearn.com/course/test?attributionToken=abc")
        "https://www.inflearn.com/course/test"
        >>> clean_course_url("https://www.inflearn.com/course/test")
        "https://www.inflearn.com/course/test"
    """
    if not url:
        return url

    # '?' 기준으로 분리하여 쿼리 파라미터 제거
    return url.split('?')[0]


def extract_single_price_element(entry_elem: Locator, selector: str, field_name: str) -> Optional[str]:
    """
    단일 가격 요소를 안전하게 추출

    Args:
        entry_elem: 강의 요소 Locator
        selector: CSS 셀렉터
        field_name: 필드명 (로깅용)

    Returns:
        추출된 가격 텍스트 또는 None
    """
    try:
        elem = entry_elem.locator(selector).first
        if elem and elem.count() > 0:
            text = elem.text_content(timeout=config.ELEMENT_TIMEOUT)
            return text.strip() if text else None
    except PlaywrightTimeoutError:
        logger.debug(f"{field_name} 추출 타임아웃")
    except Exception as e:
        logger.debug(f"{field_name} 추출 실패: {e}")
    return None


def extract_price_info(entry_elem: Locator) -> Dict[str, Optional[Any]]:
    """
    가격 정보 추출 (개선 버전 - 숫자 변환 및 is_on_sale 플래그 포함)

    페이지 구조:
    - 할인 없음: second_price만 존재 (정가)
    - 할인 중: first_price (정가) + second_price (할인가) + discount_rate 존재

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        가격 정보 딕셔너리
        {
            'original_price': int,
            'sale_price': int,
            'discount_rate': int,
            'is_on_sale': bool
        }
    """
    try:
        # Step 1: first_price 추출 시도 (할인 전 가격)
        first_price_text = extract_single_price_element(
            entry_elem,
            config.SELECTORS['first_price'],
            "정가(할인전)"
        )

        # Step 2: first_price 존재 여부에 따라 분기
        if first_price_text:
            # 할인 중: first_price=정가, second_price=할인가, discount_rate 추출
            sale_price_text = extract_single_price_element(
                entry_elem,
                config.SELECTORS['sale_price'],
                "할인가"
            )
            discount_rate_text = extract_single_price_element(
                entry_elem,
                config.SELECTORS['discount_rate'],
                "할인율"
            )

            original_price = parse_price_to_number(first_price_text)
            sale_price = parse_price_to_number(sale_price_text)

            return {
                'original_price': original_price,
                'sale_price': sale_price,
                'discount_rate': parse_discount_rate(discount_rate_text),
                'is_on_sale': True,
            }
        else:
            # 할인 없음: second_price=정가
            regular_price_text = extract_single_price_element(
                entry_elem,
                config.SELECTORS['second_price'],
                "정가"
            )

            regular_price = parse_price_to_number(regular_price_text)

            return {
                'original_price': regular_price,
                'sale_price': regular_price,  # 할인 없으면 정가와 동일
                'discount_rate': 0,
                'is_on_sale': False,
            }

    except Exception as e:
        logger.error(f"가격 정보 추출 중 예상치 못한 오류: {e}", exc_info=True)

    # 예외 발생 시 기본 구조 반환 (dict unpacking TypeError 방지)
    return {
        'original_price': None,
        'sale_price': None,
        'discount_rate': 0,
        'is_on_sale': False,
    }


def extract_rating(entry_elem: Locator) -> Optional[float]:
    """
    평점 추출 및 float 변환

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        평점 (0-5) 또는 None
    """
    rating_text = extract_text_by_selector(entry_elem, config.SELECTORS['rating'], "평점")
    if rating_text:
        try:
            rating = float(rating_text.strip())
            # 범위 검증 (0-5)
            if 0 <= rating <= 5:
                return rating
            else:
                logger.warning(f"평점 범위 초과: {rating}")
        except ValueError as e:
            logger.debug(f"평점 변환 실패 ('{rating_text}'): {e}")
    return None


def extract_review_count(entry_elem: Locator) -> Optional[int]:
    """
    리뷰 수 추출 및 int 변환

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        리뷰 수 또는 None
    """
    count_text = extract_text_by_selector(entry_elem, config.SELECTORS['review_count'], "리뷰 수")
    if count_text:
        try:
            # 괄호 및 쉼표 제거: "(1,234)" → "1234"
            clean_text = count_text.strip().strip('()').replace(',', '')
            return int(clean_text)
        except ValueError as e:
            logger.debug(f"리뷰 수 변환 실패 ('{count_text}'): {e}")
    return None


def extract_student_count(entry_elem: Locator) -> Optional[int]:
    """
    수강생 수 추출 및 int 변환

    Args:
        entry_elem: 강의 요소 Locator

    Returns:
        수강생 수 (숫자) 또는 None

    Examples:
        "3,800+" → 3800
        "200+" → 200
    """
    count_text = extract_text_by_selector(entry_elem, config.SELECTORS['student_count'], "수강생 수")
    return parse_student_count(count_text)


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
        raw_url = link.get_attribute('href')
        url = clean_course_url(raw_url)  # 추적 파라미터 제거
        course_id = None

        if url:
            course_id = url.split('/course/')[-1]

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
            'scraped_at': datetime.now(timezone.utc).isoformat(),
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

def load_course_list(page, url: str) -> List[Locator]:
    """
    페이지 로드 및 강의 링크 수집 (최적화된 대기 전략)

    Args:
        page: Playwright Page 객체
        url: 접속할 URL

    Returns:
        강의 링크 Locator 리스트
    """
    logger.info(f"🌐 페이지 접속 중: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=config.PAGE_LOAD_TIMEOUT)

    # 네트워크가 idle 상태가 될 때까지 대기 (증가된 타임아웃)
    try:
        page.wait_for_load_state('networkidle', timeout=10000)
        logger.debug("네트워크 idle 도달")
    except PlaywrightTimeoutError:
        logger.debug("페이지 로드 대기 타임아웃 (계속 진행)")

    # 스크롤하여 콘텐츠 로드 (증가된 횟수와 안정적인 대기)
    logger.info("📜 페이지 스크롤 중...")
    for i in range(5):
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        time.sleep(1)  # 각 스크롤 후 1초 대기 (안정적인 렌더링 보장)
        logger.debug(f"스크롤 {i+1}/5 완료")

    # 강의 링크 수집
    logger.info("🔍 강의 링크 수집 중...")
    course_links = page.locator(config.SELECTORS['course_link']).all()
    logger.info(f"✅ {len(course_links)}개의 강의 발견")

    return course_links


def extract_all_courses(course_links: List[Locator], max_courses: int, max_retries: int = 2) -> tuple[List[Dict], List[Dict]]:
    """
    모든 강의 데이터 추출 (메트릭 수집 및 실패 추적 포함)

    Args:
        course_links: 강의 링크 Locator 리스트
        max_courses: 수집할 최대 강의 수
        max_retries: 강의별 최대 재시도 횟수 (기본값: 2)

    Returns:
        tuple: (강의 정보 딕셔너리 리스트, 실패한 강의 리스트)
    """
    courses = []
    failed_courses = []
    metrics = {
        'total': 0,
        'success': 0,
        'validation_failed': 0,
        'extraction_failed': 0,
        'retried': 0
    }

    logger.info(f"📊 데이터 추출 중 (최대 {max_courses}개)...")
    start_time = time.time()

    for idx, link in enumerate(course_links[:max_courses]):
        metrics['total'] += 1
        retry_count = 0
        success = False
        last_error = None

        # 강의별 재시도 로직
        while retry_count <= max_retries and not success:
            try:
                course_data = extract_course_data(link, idx)

                if is_valid_course(course_data):
                    courses.append(course_data)
                    log_course_info(course_data, idx)
                    metrics['success'] += 1
                    success = True
                else:
                    last_error = "Validation failed"
                    metrics['validation_failed'] += 1
                    break  # 검증 실패는 재시도 불필요

            except Exception as e:
                last_error = str(e)
                retry_count += 1

                if retry_count <= max_retries:
                    logger.warning(f"  [{idx+1}] ⚠️  시도 {retry_count}/{max_retries} 실패: {e}")
                    metrics['retried'] += 1
                    time.sleep(config.RETRY_DELAY * retry_count)  # 지수 백오프
                else:
                    logger.error(f"  [{idx+1}] ❌ 최종 실패 (재시도 {max_retries}회 초과)", exc_info=True)
                    metrics['extraction_failed'] += 1

        # 실패한 강의 기록
        if not success:
            failed_info = {
                "index": idx + 1,
                "error": last_error,
                "retry_count": retry_count,
                "url": None
            }

            # URL 추출 시도
            try:
                raw_url = link.get_attribute('href')
                if raw_url:
                    failed_info["url"] = clean_course_url(raw_url)
            except:
                pass

            failed_courses.append(failed_info)

    # 실패 목록 저장
    if failed_courses:
        from pathlib import Path
        failed_path = Path(__file__).parent.parent / "output" / "failed_courses.json"
        try:
            with open(failed_path, "w", encoding="utf-8") as f:
                json.dump(failed_courses, f, ensure_ascii=False, indent=2)
            logger.warning(f"⚠️  실패 목록 저장: {len(failed_courses)}개 - {failed_path}")
        except Exception as e:
            logger.error(f"실패 목록 저장 중 오류: {e}", exc_info=True)

    # 메트릭 요약 출력
    elapsed = time.time() - start_time
    success_rate = (metrics['success'] / metrics['total'] * 100) if metrics['total'] > 0 else 0
    logger.info(f"\n{'='*60}")
    logger.info(f"📈 수집 통계:")
    logger.info(f"  • 전체: {metrics['total']}개")
    logger.info(f"  • 성공: {metrics['success']}개 ({success_rate:.1f}%)")
    logger.info(f"  • 검증 실패: {metrics['validation_failed']}개")
    logger.info(f"  • 추출 실패: {metrics['extraction_failed']}개")
    logger.info(f"  • 재시도: {metrics['retried']}회")
    logger.info(f"  • 소요 시간: {elapsed:.1f}초")
    logger.info(f"  • 평균 처리 시간: {elapsed/metrics['total']:.2f}초/강의" if metrics['total'] > 0 else "  • 평균 처리 시간: N/A")
    logger.info(f"{'='*60}\n")

    return courses, failed_courses


def save_debug_files(page):
    """
    디버그용 파일 저장

    Args:
        page: Playwright Page 객체
    """
    logger.info("💾 디버그 파일 저장 중...")

    # 스크린샷 저장
    page.screenshot(path=config.SCREENSHOT_PATH)
    logger.info(f"스크린샷 저장: {config.SCREENSHOT_PATH}")

    # HTML 소스 저장
    html_content = page.content()
    with open(config.HTML_SOURCE_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"HTML 소스 저장: {config.HTML_SOURCE_PATH}")


def scrape_inflearn_courses(max_courses: Optional[int] = None, headless: Optional[bool] = None) -> tuple[List[Dict], Dict]:
    """
    인프런 강의 목록 스크래핑 (리팩토링 버전 - 메타데이터 포함)

    Args:
        max_courses: 수집할 최대 강의 수 (기본값: config.MAX_COURSES)
        headless: 브라우저 숨김 모드 (기본값: config.HEADLESS)

    Returns:
        tuple: (강의 정보 딕셔너리 리스트, 메타데이터 딕셔너리)
    """
    # 기본값 설정
    max_courses = max_courses if max_courses is not None else config.MAX_COURSES
    headless = headless if headless is not None else config.HEADLESS

    # 스크래핑 시작 시간 기록
    start_time = time.time()
    start_datetime = datetime.now(timezone.utc)

    logger.info("=" * 60)
    logger.info("🚀 인프런 강의 스크래핑 시작")
    logger.info(f"설정: max_courses={max_courses}, headless={headless}")
    logger.info("=" * 60)

    with sync_playwright() as p:
        # 브라우저 실행 (봇 탐지 우회 설정 추가)
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR',
            extra_http_headers={
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            }
        )
        page = context.new_page()

        # 페이지 레벨에서도 Accept-Language 헤더 명시적 설정
        page.set_extra_http_headers({
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })

        try:
            # 페이지 로드 및 강의 링크 수집
            url = f"{config.BASE_URL}/{config.CATEGORY}"
            course_links = load_course_list(page, url)

            # 모든 강의 데이터 추출 (실패 추적 포함)
            courses, failed_courses = extract_all_courses(course_links, max_courses)

            # 디버그 파일 저장
            save_debug_files(page)

            # 스크래핑 종료 시간 계산
            end_time = time.time()
            duration = round(end_time - start_time, 2)

            # 메타데이터 생성
            metadata = {
                "version": "1.0.0",
                "scraper_version": "2.2.0",  # 실패 추적 및 재시도 로직 추가
                "total_courses": len(courses),
                "failed_courses": len(failed_courses),
                "scraped_at": start_datetime.isoformat(),
                "scraping_duration_seconds": duration,
                "config": {
                    "max_courses": max_courses,
                    "category": config.CATEGORY,
                    "headless": headless,
                    "base_url": config.BASE_URL
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
                "scraper_version": "2.1.0",
                "total_courses": 0,
                "scraped_at": start_datetime.isoformat(),
                "scraping_duration_seconds": duration,
                "config": {
                    "max_courses": max_courses,
                    "category": config.CATEGORY,
                    "headless": headless,
                    "base_url": config.BASE_URL
                },
                "error": str(e)
            }
            return [], metadata

        finally:
            context.close()
            browser.close()
            logger.debug("브라우저 종료")


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
        # 스크래핑 실행 (메타데이터 포함)
        courses, metadata = scrape_inflearn_courses()

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
