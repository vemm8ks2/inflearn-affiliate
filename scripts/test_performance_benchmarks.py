# scripts/test_performance_benchmarks.py
"""
성능 테스트 및 벤치마크
- 대용량 데이터 처리 테스트
- 배치 처리 성능 벤치마크
- 메모리 사용량 모니터링
"""

import sys
from pathlib import Path
from unittest import mock
import pytest
import time
import tracemalloc

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))


class TestLargeDataProcessing:
    """대용량 데이터 처리 테스트"""

    @mock.patch('db_utils.supabase')
    def test_large_batch_processing(self, mock_supabase):
        """대용량 배치 처리 (1000개 강의)"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 1000개 강의 생성
        courses = [
            {
                'title': f'대용량 테스트 강의 {i}',
                'url': f'https://inflearn.com/course/test-{i}',
                'instructor': f'강사 {i % 50}',  # 50명 강사
                'rating': 4.0 + (i % 10) * 0.1,
                'review_count': i * 10,
                'student_count': i * 100
            }
            for i in range(1000)
        ]

        start_time = time.time()
        saved_count = upsert_courses(courses, batch_size=50)
        end_time = time.time()

        # 검증
        assert saved_count == 1000
        assert mock_table.upsert.call_count == 20  # 1000 / 50 = 20 batches

        # 성능 검증: 1000개 처리가 10초 이내
        processing_time = end_time - start_time
        assert processing_time < 10.0, f"처리 시간 초과: {processing_time:.2f}초"

        print(f"\n[성능] 1000개 강의 처리 시간: {processing_time:.3f}초")

    @mock.patch('scrape_inflearn_with_sales.extract_course_data')
    @mock.patch('scrape_inflearn_with_sales.is_valid_course')
    def test_large_extraction_processing(self, mock_is_valid, mock_extract):
        """대용량 추출 처리 (500개 강의)"""
        from scrape_inflearn_with_sales import extract_all_courses

        # Mock 설정
        mock_extract.return_value = {
            'title': '테스트 강의',
            'url': 'https://inflearn.com/course/test',
            'instructor': '강사'
        }
        mock_is_valid.return_value = True

        # 500개 링크
        mock_links = [mock.Mock() for _ in range(500)]

        start_time = time.time()
        courses, failed_courses = extract_all_courses(mock_links, max_courses=500, max_retries=0)
        end_time = time.time()

        # 검증
        assert len(courses) == 500

        # 성능 검증
        processing_time = end_time - start_time
        assert processing_time < 5.0, f"처리 시간 초과: {processing_time:.2f}초"

        print(f"\n[성능] 500개 강의 추출 시간: {processing_time:.3f}초")


class TestBatchProcessingPerformance:
    """배치 처리 성능 벤치마크"""

    @mock.patch('db_utils.supabase')
    def test_batch_size_10_performance(self, mock_supabase):
        """배치 크기 10 성능 벤치마크"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(100)
        ]

        start_time = time.time()
        saved_count = upsert_courses(courses, batch_size=10)
        end_time = time.time()

        # 검증
        assert saved_count == 100
        assert mock_table.upsert.call_count == 10  # 100 / 10 = 10

        processing_time = end_time - start_time
        print(f"\n[벤치마크] batch_size=10: {processing_time:.4f}초, 배치당 {processing_time/10:.4f}초")

    @mock.patch('db_utils.supabase')
    def test_batch_size_50_performance(self, mock_supabase):
        """배치 크기 50 성능 벤치마크"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(100)
        ]

        start_time = time.time()
        saved_count = upsert_courses(courses, batch_size=50)
        end_time = time.time()

        # 검증
        assert saved_count == 100
        assert mock_table.upsert.call_count == 2  # 100 / 50 = 2

        processing_time = end_time - start_time
        print(f"\n[벤치마크] batch_size=50: {processing_time:.4f}초, 배치당 {processing_time/2:.4f}초")

    @mock.patch('db_utils.supabase')
    def test_batch_size_100_performance(self, mock_supabase):
        """배치 크기 100 성능 벤치마크"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(100)
        ]

        start_time = time.time()
        saved_count = upsert_courses(courses, batch_size=100)
        end_time = time.time()

        # 검증
        assert saved_count == 100
        assert mock_table.upsert.call_count == 1  # 100 / 100 = 1

        processing_time = end_time - start_time
        print(f"\n[벤치마크] batch_size=100: {processing_time:.4f}초, 배치당 {processing_time/1:.4f}초")


class TestMemoryUsageMonitoring:
    """메모리 사용량 모니터링 테스트"""

    @mock.patch('db_utils.supabase')
    def test_memory_usage_small_dataset(self, mock_supabase):
        """소규모 데이터셋 메모리 사용량 (100개)"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 메모리 추적 시작
        tracemalloc.start()

        # 100개 강의 생성
        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(100)
        ]

        upsert_courses(courses, batch_size=10)

        # 메모리 사용량 측정
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 검증: 100개 처리에 10MB 미만 사용
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 10.0, f"메모리 사용량 초과: {peak_mb:.2f}MB"

        print(f"\n[메모리] 100개 강의: Peak = {peak_mb:.2f}MB")

    @mock.patch('db_utils.supabase')
    def test_memory_usage_medium_dataset(self, mock_supabase):
        """중규모 데이터셋 메모리 사용량 (1000개)"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 메모리 추적 시작
        tracemalloc.start()

        # 1000개 강의 생성
        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(1000)
        ]

        upsert_courses(courses, batch_size=50)

        # 메모리 사용량 측정
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 검증: 1000개 처리에 50MB 미만 사용
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 50.0, f"메모리 사용량 초과: {peak_mb:.2f}MB"

        print(f"\n[메모리] 1000개 강의: Peak = {peak_mb:.2f}MB")

    @mock.patch('db_utils.supabase')
    def test_memory_usage_large_dataset(self, mock_supabase):
        """대규모 데이터셋 메모리 사용량 (5000개)"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        # 메모리 추적 시작
        tracemalloc.start()

        # 5000개 강의 생성
        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(5000)
        ]

        upsert_courses(courses, batch_size=100)

        # 메모리 사용량 측정
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 검증: 5000개 처리에 200MB 미만 사용
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 200.0, f"메모리 사용량 초과: {peak_mb:.2f}MB"

        print(f"\n[메모리] 5000개 강의: Peak = {peak_mb:.2f}MB")

    def test_memory_leak_detection(self):
        """메모리 누수 감지 테스트"""
        from db_utils import validate_course_data

        tracemalloc.start()

        # 반복적으로 유효성 검증 (메모리 누수 확인)
        course = {
            'title': '테스트 강의',
            'url': 'https://inflearn.com/course/test',
            'instructor': '강사',
            'rating': 4.5,
            'review_count': 100,
            'student_count': 500
        }

        # 첫 번째 실행 후 메모리 측정
        for _ in range(100):
            validate_course_data(course)

        memory_after_100 = tracemalloc.get_traced_memory()[0]

        # 두 번째 실행 후 메모리 측정
        for _ in range(100):
            validate_course_data(course)

        memory_after_200 = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        # 메모리 증가량 계산
        memory_increase = memory_after_200 - memory_after_100
        memory_increase_mb = memory_increase / 1024 / 1024

        # 검증: 메모리 증가량이 1MB 미만 (메모리 누수 없음)
        assert memory_increase_mb < 1.0, f"메모리 누수 의심: {memory_increase_mb:.2f}MB 증가"

        print(f"\n[메모리 누수] 200회 실행 메모리 증가: {memory_increase_mb:.4f}MB")


class TestConcurrentProcessing:
    """동시 처리 성능 테스트"""

    @mock.patch('db_utils.supabase')
    def test_sequential_vs_batch_comparison(self, mock_supabase):
        """순차 처리 vs 배치 처리 성능 비교"""
        from db_utils import upsert_courses

        # Mock 설정
        mock_table = mock.Mock()
        mock_upsert = mock.Mock()
        mock_execute = mock.Mock()
        mock_execute.execute.return_value = mock.Mock()

        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_execute

        courses = [
            {'title': f'강의{i}', 'url': f'url{i}', 'instructor': f'강사{i}'}
            for i in range(100)
        ]

        # 배치 처리 (batch_size=10)
        mock_table.reset_mock()
        start_batch = time.time()
        upsert_courses(courses, batch_size=10)
        time_batch = time.time() - start_batch

        # 배치 처리 (batch_size=1, 유사 순차)
        mock_table.reset_mock()
        start_sequential = time.time()
        upsert_courses(courses, batch_size=1)
        time_sequential = time.time() - start_sequential

        # 성능 개선 비율 계산
        improvement = (time_sequential - time_batch) / time_sequential * 100

        print(f"\n[성능 비교]")
        print(f"  배치 처리 (size=10): {time_batch:.4f}초")
        print(f"  순차 처리 (size=1): {time_sequential:.4f}초")
        print(f"  성능 개선: {improvement:.1f}%")

        # 배치 처리가 더 빠르거나 비슷해야 함
        assert time_batch <= time_sequential * 1.1  # 10% 오차 허용


if __name__ == "__main__":
    # 모든 테스트 실행
    pytest.main([__file__, "-v", "-s"])  # -s 옵션으로 print 출력 표시
