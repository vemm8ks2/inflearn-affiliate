# scripts/logger_config.py
"""
로깅 설정 모듈
콘솔과 파일 로깅을 동시에 제공
"""

import logging
import os
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
