# scripts/config.py
"""
스크래핑 설정 모듈
환경 변수 및 상수 관리
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


# .env 파일 로드 시도 (python-dotenv 설치 시)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv가 없으면 os.getenv만 사용
    pass


@dataclass
class ScraperConfig:
    """스크래핑 설정 클래스"""

    # 기본 URL 설정
    BASE_URL: str = "https://www.inflearn.com/courses"
    CATEGORY: str = "it-programming"

    # 스크래핑 설정
    MAX_COURSES: int = field(default_factory=lambda: int(os.getenv("MAX_COURSES_PER_RUN", "20")))
    HEADLESS: bool = field(default_factory=lambda: os.getenv("HEADLESS_MODE", "false").lower() == "true")

    # 타임아웃 설정 (밀리초)
    PAGE_LOAD_TIMEOUT: int = 30000
    ELEMENT_TIMEOUT: int = 2000
    SCROLL_DELAY: int = 1

    # 파일 경로 (프로젝트 루트 기준)
    OUTPUT_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "output")
    SCREENSHOT_PATH: str = ""
    HTML_SOURCE_PATH: str = ""
    JSON_OUTPUT: str = ""

    # 선택자 전략
    SELECTORS: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self):
        """초기화 후 처리"""
        # 출력 디렉토리 생성
        self.OUTPUT_DIR.mkdir(exist_ok=True)

        # 파일 경로 설정
        self.SCREENSHOT_PATH = str(self.OUTPUT_DIR / "inflearn_screenshot.png")
        self.HTML_SOURCE_PATH = str(self.OUTPUT_DIR / "page_source.html")
        self.JSON_OUTPUT = str(self.OUTPUT_DIR / "courses_with_sales.json")

        # 선택자 딕셔너리 (Phase 1: 상수화)
        # 주의: nth-child 셀렉터는 DOM 구조 변경에 취약함
        self.SELECTORS = {
            # 기본 정보
            'course_link': 'li > a[href*="/course/"]',
            'entry_container': 'div > div:nth-child(2) > div > article',

            # 강의 상세 정보
            'title': 'div:nth-child(2) > div:nth-child(1) > p:nth-child(1)',
            'instructor': 'div:nth-child(2) > div:nth-child(1) > p:nth-child(2)',
            'thumbnail': 'picture img',

            # 가격 정보
            'first_price': 'div:nth-child(2) > div:nth-child(2) > div > div:nth-child(1) > p',
            'second_price': 'div:nth-child(2) > div:nth-child(2) > div > div:nth-child(2) > p',
            'discount_rate': 'div:nth-child(2) > div:nth-child(2) > div > div:nth-child(2) > p:nth-child(2)',
            'sale_price': 'div:nth-child(2) > div:nth-child(2) > div > div:nth-child(2) > p:nth-child(3)',

            # 평가 정보
            'rating': 'div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(1) > div > p',
            'review_count': 'div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(1) > p',
            'student_count': 'div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(2) > span',
        }


# 전역 설정 인스턴스
config = ScraperConfig()
