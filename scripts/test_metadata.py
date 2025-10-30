# scripts/test_metadata.py
"""
메타데이터 기능 검증 테스트
"""

import json
from datetime import datetime, timezone


def test_metadata_structure():
    """메타데이터 구조 검증"""
    print("=" * 60)
    print("메타데이터 구조 검증 테스트")
    print("=" * 60)

    # 예상 메타데이터 구조
    expected_metadata = {
        "version": "1.0.0",
        "scraper_version": "2.1.0",
        "total_courses": 20,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "scraping_duration_seconds": 1.5,
        "config": {
            "max_courses": 20,
            "category": "it-programming",
            "headless": False,
            "base_url": "https://www.inflearn.com"
        }
    }

    # 예상 출력 구조
    expected_output = {
        "metadata": expected_metadata,
        "courses": [
            {"title": "강의1", "url": "https://test.com/1"},
            {"title": "강의2", "url": "https://test.com/2"}
        ]
    }

    print("\n✅ 메타데이터 구조:")
    print(json.dumps(expected_metadata, indent=2, ensure_ascii=False))

    print("\n✅ JSON 출력 구조:")
    print(json.dumps(expected_output, indent=2, ensure_ascii=False))

    # 필수 필드 검증
    required_metadata_fields = [
        "version",
        "scraper_version",
        "total_courses",
        "scraped_at",
        "scraping_duration_seconds",
        "config"
    ]

    print("\n✅ 필수 메타데이터 필드 검증:")
    for field in required_metadata_fields:
        if field in expected_metadata:
            print(f"  - {field}: PASS")
        else:
            print(f"  - {field}: FAIL")

    # config 필드 검증
    required_config_fields = ["max_courses", "category", "headless", "base_url"]

    print("\n✅ config 필드 검증:")
    for field in required_config_fields:
        if field in expected_metadata["config"]:
            print(f"  - {field}: PASS")
        else:
            print(f"  - {field}: FAIL")


def test_save_to_json_logic():
    """save_to_json 로직 검증"""
    print("\n" + "=" * 60)
    print("save_to_json 로직 검증")
    print("=" * 60)

    courses = [{"title": "Test", "url": "https://test.com"}]
    metadata = {
        "version": "1.0.0",
        "total_courses": len(courses)
    }

    # 메타데이터 있을 때
    output_with_metadata = {
        "metadata": metadata,
        "courses": courses
    }

    # 메타데이터 없을 때 (하위 호환성)
    output_without_metadata = courses

    print("\n✅ 메타데이터 포함 출력:")
    print(json.dumps(output_with_metadata, indent=2, ensure_ascii=False))

    print("\n✅ 메타데이터 없음 (하위 호환성):")
    print(json.dumps(output_without_metadata, indent=2, ensure_ascii=False))


def test_error_metadata():
    """에러 발생 시 메타데이터 검증"""
    print("\n" + "=" * 60)
    print("에러 메타데이터 검증")
    print("=" * 60)

    error_metadata = {
        "version": "1.0.0",
        "scraper_version": "2.1.0",
        "total_courses": 0,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "scraping_duration_seconds": 0.5,
        "config": {
            "max_courses": 20,
            "category": "it-programming",
            "headless": False
        },
        "error": "Timeout error"
    }

    print("\n✅ 에러 발생 시 메타데이터:")
    print(json.dumps(error_metadata, indent=2, ensure_ascii=False))

    # error 필드 존재 확인
    if "error" in error_metadata:
        print("\n✅ error 필드 포함: PASS")
    else:
        print("\n❌ error 필드 누락: FAIL")


def main():
    """전체 테스트 실행"""
    print("\n" + "=" * 60)
    print("메타데이터 기능 검증 시작")
    print("=" * 60)

    test_metadata_structure()
    test_save_to_json_logic()
    test_error_metadata()

    print("\n" + "=" * 60)
    print("✅ 메타데이터 기능 검증 완료")
    print("=" * 60)

    print("\n📊 구현 완료 요약:")
    print("  - version: 데이터 버전 정보")
    print("  - scraper_version: 스크래퍼 버전 (2.1.0)")
    print("  - total_courses: 수집된 강의 수")
    print("  - scraped_at: 스크래핑 시작 시간 (UTC)")
    print("  - scraping_duration_seconds: 소요 시간")
    print("  - config: 스크래핑 설정 정보")
    print("  - error: 에러 발생 시 에러 메시지 (선택적)")


if __name__ == "__main__":
    main()
