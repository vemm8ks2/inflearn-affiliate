# scripts/config.py
"""
스크래핑 설정 모듈 (API 버전)
환경 변수 및 상수 관리
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


# .env 파일 로드 시도 (python-dotenv 설치 시)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class ScraperConfig:
    """스크래핑 설정 클래스 (API 버전)"""

    # API 설정
    API_BASE_URL: str = "https://course-api.inflearn.com/client/api/v2"
    API_LANGUAGE: str = "ko"
    API_TIMEOUT: int = 10  # 초

    # 카테고리 설정
    CATEGORY: str = "it-programming"

    # 스크래핑 설정
    MAX_COURSES: int = field(default_factory=lambda: int(os.getenv("MAX_COURSES_PER_RUN", "20")))

    # Phase 7: OpenAI 설정
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    OPENAI_MODEL: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4-turbo"))
    MAX_TOKENS: int = field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "500")))
    TEMPERATURE: float = field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.7")))

    # 파일 경로
    OUTPUT_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / "output")
    JSON_OUTPUT: str = ""

    def __post_init__(self):
        """초기화 후 처리"""
        # 출력 디렉토리 생성
        self.OUTPUT_DIR.mkdir(exist_ok=True)

        # JSON 파일 경로 설정
        self.JSON_OUTPUT = str(self.OUTPUT_DIR / "courses_with_sales.json")


# 전역 설정 인스턴스
config = ScraperConfig()
