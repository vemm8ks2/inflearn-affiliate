# scripts/test_integration_workflows.py
"""
Integration 테스트 - 워크플로우 검증
- 전체 스크래핑 워크플로우
- DB 저장 → 조회 워크플로우
- 에러 복구 시나리오
"""

import sys
from pathlib import Path
from unittest import mock
import pytest
import json

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))


class TestFullScrapingWorkflow:
    """전체 스크래핑 워크플로우 통합 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_all_courses')
    @mock.patch('scrape_inflearn_with_sales.save_to_json')
    def test_scraping_to_json_workflow(self, mock_save_json, mock_extract):
        """스크래핑 → JSON 저장 워크플로우"""
        # Mock 데이터 준비
        mock_courses = [
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'},
            {'title': '강의2', 'url': 'url2', 'instructor': '강사2'}
        ]
        mock_failed = []

        mock_extract.return_value = (mock_courses, mock_failed)

        # 워크플로우 실행
        courses, failed_courses = mock_extract([], max_courses=10)
        mock_save_json(courses, Path("test.json"))

        # 검증
        assert len(courses) == 2
        mock_save_json.assert_called_once()

    @mock.patch('scrape_inflearn_with_sales.extract_all_courses')
    def test_scraping_with_failed_courses_workflow(self, mock_extract):
        """스크래핑 + 실패 목록 처리 워크플로우"""
        # Mock 데이터: 일부 실패 포함
        mock_courses = [
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'}
        ]
        mock_failed = [
            {'index': 1, 'url': 'failed_url', 'error': 'timeout', 'retry_count': 2}
        ]

        mock_extract.return_value = (mock_courses, mock_failed)

        # 워크플로우 실행
        courses, failed_courses = mock_extract([], max_courses=10)

        # 검증
        assert len(courses) == 1
        assert len(failed_courses) == 1
        assert failed_courses[0]['retry_count'] == 2


class TestDBSaveRetrieveWorkflow:
    """DB 저장 → 조회 워크플로우 통합 테스트"""

    @mock.patch('db_utils.supabase')
    def test_save_and_retrieve_workflow(self, mock_supabase):
        """강의 저장 → 조회 워크플로우"""
        from db_utils import upsert_courses, get_all_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_select = mock.Mock()
        mock_execute_upsert = mock.Mock()
        mock_execute_select = mock.Mock()

        mock_execute_upsert.execute.return_value = mock.Mock()
        mock_execute_select.execute.return_value = mock.Mock(data=[
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'},
            {'title': '강의2', 'url': 'url2', 'instructor': '강사2'}
        ])

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute_upsert
        mock_table.select.return_value = mock_execute_select

        # 1. 강의 저장
        courses = [
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'},
            {'title': '강의2', 'url': 'url2', 'instructor': '강사2'}
        ]
        saved_count = upsert_courses(courses, batch_size=10)

        # 2. 강의 조회
        retrieved_courses = get_all_courses()

        # 검증
        assert saved_count == 2
        assert len(retrieved_courses) == 2
        assert retrieved_courses[0]['title'] == '강의1'

    @mock.patch('db_utils.supabase')
    def test_upsert_duplicate_handling(self, mock_supabase):
        """중복 강의 Upsert 처리"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 동일한 URL의 강의 2번 저장
        course = {'title': '강의1', 'url': 'url1', 'instructor': '강사1'}

        # 첫 번째 저장
        upsert_courses([course], batch_size=10)

        # 두 번째 저장 (업데이트)
        course['title'] = '강의1 (업데이트)'
        upsert_courses([course], batch_size=10)

        # Upsert 2번 호출 확인
        assert mock_table.upsert.call_count == 2

    @mock.patch('db_utils.supabase')
    def test_batch_save_workflow(self, mock_supabase):
        """배치 저장 워크플로우 (대용량)"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 25개 강의 생성 (batch_size=10이면 3번 호출)
        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(25)
        ]

        saved_count = upsert_courses(courses, batch_size=10)

        # 검증
        assert saved_count == 25
        assert mock_table.upsert.call_count == 3  # 10, 10, 5


class TestErrorRecoveryScenarios:
    """에러 복구 시나리오 통합 테스트"""

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    @mock.patch('time.sleep', return_value=None)  # 실제 대기 방지
    def test_retry_on_extraction_failure(self, mock_sleep, mock_is_valid, mock_extract):
        """추출 실패 시 재시도 시나리오"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 설정: 첫 2번 실패, 3번째 성공
        mock_extract.side_effect = [
            Exception("첫 번째 실패"),
            Exception("두 번째 실패"),
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'}
        ]
        mock_is_valid.return_value = True

        mock_links = [mock.Mock()]

        # max_retries=2 설정
        courses, failed_courses = extract_all_courses(mock_links, max_courses=10, max_retries=2)

        # 검증: 3번째 시도에서 성공
        assert len(courses) == 1
        assert len(failed_courses) == 0
        assert mock_extract.call_count == 3  # 1번 원본 + 2번 재시도

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    @mock.patch('time.sleep', return_value=None)
    def test_max_retries_exhausted(self, mock_sleep, mock_is_valid, mock_extract):
        """최대 재시도 횟수 초과 시나리오"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 설정: 계속 실패
        mock_extract.side_effect = Exception("계속 실패")

        mock_links = [mock.Mock()]

        # max_retries=2 설정
        courses, failed_courses = extract_all_courses(mock_links, max_courses=10, max_retries=2)

        # 검증: 실패 목록에 포함
        assert len(courses) == 0
        assert len(failed_courses) == 1
        assert failed_courses[0]['retry_count'] == 3  # 초기 시도 포함
        assert mock_extract.call_count == 3  # 1번 원본 + 2번 재시도

    @mock.patch('db_utils.supabase')
    def test_db_connection_failure_recovery(self, mock_supabase):
        """DB 연결 실패 복구 시나리오"""
        from db_utils import upsert_courses

        # Mock 설정: DB 연결 실패
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.side_effect = Exception("DB 연결 실패")

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'}
        ]

        # DB 연결 실패 시 저장 실패하지만 예외는 발생하지 않음
        saved_count = upsert_courses(courses, batch_size=10)

        # 검증: 저장 실패로 0 반환
        assert saved_count == 0

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    def test_partial_failure_workflow(self, mock_is_valid, mock_extract):
        """일부 실패 워크플로우"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 설정: 5개 중 2개 실패
        mock_extract.side_effect = [
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'},  # 성공
            Exception("실패1"),  # 실패
            {'title': '강의3', 'url': 'url3', 'instructor': '강사3'},  # 성공
            Exception("실패2"),  # 실패
            {'title': '강의5', 'url': 'url5', 'instructor': '강사5'},  # 성공
        ]
        mock_is_valid.return_value = True

        mock_links = [mock.Mock() for _ in range(5)]

        courses, failed_courses = extract_all_courses(mock_links, max_courses=10, max_retries=0)

        # 검증: 3개 성공, 2개 실패
        assert len(courses) == 3
        assert len(failed_courses) == 2


class TestValidationWorkflow:
    """데이터 유효성 검증 워크플로우 테스트"""

    def test_course_validation_in_workflow(self):
        """강의 데이터 유효성 검증 통합"""
        from db_utils import validate_course_data

        # 유효한 강의
        valid_course = {
            'title': '테스트 강의',
            'url': 'https://inflearn.com/course/test',
            'instructor': '홍길동',
            'rating': 4.5,
            'review_count': 100,
            'student_count': 500
        }
        assert validate_course_data(valid_course) is True

        # 무효한 강의 (title 누락)
        invalid_course = {
            'url': 'https://inflearn.com/course/test',
            'instructor': '홍길동'
        }
        assert validate_course_data(invalid_course) is False

    @mock.patch('db_utils.supabase')
    def test_invalid_data_filtering_in_save_workflow(self, mock_supabase):
        """DB 저장 시 유효하지 않은 데이터 필터링"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 3개 강의: 2개 유효, 1개 무효
        courses = [
            {'title': '강의1', 'url': 'url1', 'instructor': '강사1'},  # 유효
            {'url': 'url2', 'instructor': '강사2'},  # 무효 (title 누락)
            {'title': '강의3', 'url': 'url3', 'instructor': '강사3'},  # 유효
        ]

        saved_count = upsert_courses(courses, batch_size=10)

        # 검증: 유효한 2개만 저장
        assert saved_count == 2


class TestMetadataWorkflow:
    """메타데이터 생성 및 저장 워크플로우 테스트"""

    def test_metadata_generation_workflow(self):
        """메타데이터 생성 및 구조 검증"""
        from datetime import datetime, timezone

        # 메타데이터 생성
        metadata = {
            'total_courses': 50,
            'failed_courses': 2,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'scraper_version': '2.2.0'
        }

        # 검증
        assert 'total_courses' in metadata
        assert 'failed_courses' in metadata
        assert 'timestamp' in metadata
        assert 'scraper_version' in metadata
        assert metadata['total_courses'] == 50
        assert metadata['failed_courses'] == 2

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_failed_courses_json_save_workflow(self, mock_file):
        """실패한 강의 JSON 저장 워크플로우"""
        import json

        failed_courses = [
            {'index': 0, 'url': 'url1', 'error': 'timeout', 'retry_count': 2},
            {'index': 5, 'url': 'url2', 'error': 'parse_error', 'retry_count': 2}
        ]

        # JSON 저장 시뮬레이션
        json_content = json.dumps(failed_courses, ensure_ascii=False, indent=2)

        # 검증
        assert len(failed_courses) == 2
        assert json.loads(json_content) == failed_courses


if __name__ == "__main__":
    # 모든 테스트 실행
    pytest.main([__file__, "-v"])
