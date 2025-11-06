"""인프런 스크래퍼 테스트 패키지

이 패키지는 스크래핑 시스템의 각 컴포넌트를 테스트합니다.

테스트 모듈:
    - test_db_utils_*.py: 데이터베이스 유틸리티 테스트
    - test_logger_config.py: 로깅 시스템 테스트
    - test_parsing_functions.py: 파싱 로직 테스트
    - test_scraping_extraction_mock.py: 스크래핑 추출 테스트
    - test_integration_workflows.py: 통합 워크플로우 테스트
    - test_performance_benchmarks.py: 성능 벤치마크 테스트

테스트 실행:
    pytest scripts/tests/
    pytest scripts/tests/test_db_utils_improvements.py -v
"""

__version__ = "0.1.0"
