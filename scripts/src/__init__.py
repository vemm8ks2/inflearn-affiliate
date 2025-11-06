"""인프런 강의 스크래핑 패키지

이 패키지는 인프런 웹사이트에서 강의 데이터를 수집하고
Supabase 데이터베이스에 저장하는 기능을 제공합니다.

주요 모듈:
    - config: 스크래핑 설정 및 환경 변수 관리
    - db_utils: Supabase 데이터베이스 유틸리티
    - logger_config: 로깅 시스템 설정
    - scraper: 메인 스크래핑 로직

사용 예시:
    >>> from src.config import config
    >>> from src.db_utils import upsert_courses
    >>> from src.logger_config import logger
    >>>
    >>> logger.info(f"스크래핑 시작: {config.BASE_URL}")
"""

from .config import config
from .logger_config import logger

# db_utils는 supabase 의존성이 필요하므로 선택적 import
try:
    from .db_utils import upsert_courses, validate_course_data
    __all__ = [
        "config",
        "upsert_courses",
        "validate_course_data",
        "logger",
    ]
except ImportError:
    # supabase가 설치되지 않은 경우
    __all__ = [
        "config",
        "logger",
    ]

__version__ = "0.1.0"
__author__ = "Inflearn Affiliate Team"
