# scripts/test_logger_config.py
"""
logger_config.py 테스트
"""

import subprocess
import sys
from pathlib import Path


def test_logger_setup():
    """로거 설정 함수 테스트"""
    from src.logger_config import setup_logger, log_filename

    # 로거 생성
    logger = setup_logger("test_logger")

    # 로거 속성 검증
    assert logger.name == "test_logger"
    assert len(logger.handlers) == 2  # console + file

    # 핸들러 타입 검증
    handler_types = [type(h).__name__ for h in logger.handlers]
    assert "StreamHandler" in handler_types
    assert "FileHandler" in handler_types

    # 로그 레벨 검증
    assert logger.level == 10  # DEBUG

    # 로그 파일 존재 확인
    assert log_filename.exists() or log_filename.parent.exists()

    print("✅ 로거 설정 함수 테스트 통과")


def test_logger_duplicate_handler_prevention():
    """중복 핸들러 방지 테스트"""
    from src.logger_config import setup_logger

    # 같은 이름으로 여러 번 호출
    logger1 = setup_logger("duplicate_test")
    logger2 = setup_logger("duplicate_test")

    # 같은 객체 반환 확인
    assert logger1 is logger2

    # 핸들러가 중복되지 않음 확인
    assert len(logger1.handlers) == 2

    print("✅ 중복 핸들러 방지 테스트 통과")


def test_logger_main_execution():
    """logger_config.py 직접 실행 테스트 (__main__ 블록)"""
    # logger_config.py 파일 경로
    logger_config_path = Path(__file__).parent / "logger_config.py"

    # Python으로 직접 실행
    result = subprocess.run(
        [sys.executable, str(logger_config_path)],
        capture_output=True,
        text=True,
        timeout=10
    )

    # 실행 성공 확인
    assert result.returncode == 0, f"실행 실패: {result.stderr}"

    # 출력 내용 검증 (stderr 또는 stdout 모두 확인)
    output = result.stdout + result.stderr
    assert "로깅 시스템 테스트" in output, "INFO 메시지 누락"
    assert "경고 메시지 테스트" in output, "WARNING 메시지 누락"
    assert "에러 메시지 테스트" in output, "ERROR 메시지 누락"
    assert "로그 파일 저장:" in output or "[OK]" in output, "로그 파일 경로 출력 누락"

    # DEBUG 메시지는 콘솔에 출력되지 않음 (파일에만 기록)
    assert "디버그 메시지 테스트" not in result.stdout, "DEBUG 메시지가 stdout에 출력됨 (오류)"

    print("✅ __main__ 블록 실행 테스트 통과")


def test_logger_file_creation():
    """로그 파일 생성 확인"""
    from src.logger_config import log_filename, logger

    # 테스트 로그 작성
    logger.info("테스트 로그 메시지")

    # 로그 파일 존재 확인
    assert log_filename.exists(), f"로그 파일 미생성: {log_filename}"

    # 로그 파일 내용 확인
    with open(log_filename, "r", encoding="utf-8") as f:
        content = f.read()
        assert "테스트 로그 메시지" in content, "로그 내용 미기록"

    print("✅ 로그 파일 생성 테스트 통과")


def test_logger_log_levels():
    """로그 레벨별 기록 테스트"""
    from src.logger_config import setup_logger, log_filename
    import logging

    # 새 로거 생성
    test_logger = setup_logger("level_test")

    # 각 레벨 로그 기록
    test_logger.debug("DEBUG 테스트")
    test_logger.info("INFO 테스트")
    test_logger.warning("WARNING 테스트")
    test_logger.error("ERROR 테스트")

    # 로그 파일 내용 확인 (모든 레벨 기록됨)
    with open(log_filename, "r", encoding="utf-8") as f:
        content = f.read()
        assert "DEBUG 테스트" in content, "DEBUG 미기록"
        assert "INFO 테스트" in content, "INFO 미기록"
        assert "WARNING 테스트" in content, "WARNING 미기록"
        assert "ERROR 테스트" in content, "ERROR 미기록"

    print("✅ 로그 레벨별 기록 테스트 통과")


def test_logger_functionality_function():
    """test_logger_functionality() 함수 직접 호출 테스트"""
    from src.logger_config import test_logger_functionality, log_filename
    from io import StringIO
    import sys

    # stdout 캡처
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        # 함수 직접 호출
        test_logger_functionality()

        # stdout 복원
        sys.stdout = sys.__stdout__

        # 출력 내용 검증
        output = captured_output.getvalue()
        assert "[OK]" in output or "로그 파일 저장:" in output, "출력 메시지 누락"

        # 로그 파일 내용 검증
        with open(log_filename, "r", encoding="utf-8") as f:
            content = f.read()
            assert "로깅 시스템 테스트" in content, "INFO 미기록"
            assert "경고 메시지 테스트" in content, "WARNING 미기록"
            assert "에러 메시지 테스트" in content, "ERROR 미기록"

        print("[OK] test_logger_functionality() 함수 테스트 통과")

    finally:
        # stdout 복원 (예외 발생 시에도 복원)
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    # 모든 테스트 실행
    test_logger_setup()
    test_logger_duplicate_handler_prevention()
    test_logger_main_execution()
    test_logger_file_creation()
    test_logger_log_levels()
    test_logger_functionality_function()

    print("\n" + "="*60)
    print("[OK] 모든 logger_config.py 테스트 통과!")
    print("="*60)
