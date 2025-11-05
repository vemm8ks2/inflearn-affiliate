# scripts/logger_config.py
"""
로깅 설정 모듈
콘솔과 파일 로깅을 동시에 제공
"""

import logging
from datetime import datetime
from pathlib import Path

# logs 디렉토리 생성 (프로젝트 루트 기준)
# scripts/logger_config.py → inflearn-affiliate/scripts/ → inflearn-affiliate/logs/
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# 로그 파일명 (날짜별)
log_filename = logs_dir / f"scraping_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logger(name="inflearn_scraper"):
    """
    로거 설정 함수

    Args:
        name: 로거 이름

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 중복 방지
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 로그 포맷
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 핸들러 (INFO 레벨)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 파일 핸들러 (DEBUG 레벨)
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 기본 로거 인스턴스 생성
logger = setup_logger()


def test_logger_functionality():
    """
    로거 기능 테스트 함수

    이 함수를 분리하여 테스트 코드에서 직접 호출 가능하도록 함
    """
    logger.info("로깅 시스템 테스트")
    logger.warning("경고 메시지 테스트")
    logger.error("에러 메시지 테스트")
    logger.debug("디버그 메시지 테스트 (파일에만 기록됨)")
    print(f"\n[OK] 로그 파일 저장: {log_filename}")


if __name__ == "__main__":
    # 로거 테스트
    test_logger_functionality()
