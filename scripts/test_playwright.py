# scripts/test_playwright.py
from playwright.sync_api import sync_playwright

def test_basic_scraping():
    """Playwright 기본 동작 테스트"""
    with sync_playwright() as p:
        # 브라우저 실행 (headless=False로 브라우저 창 표시)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 인프런 홈페이지 접속
        print("🌐 인프런 접속 중...")
        page.goto("https://www.inflearn.com", wait_until="domcontentloaded")

        # 페이지 타이틀 확인
        title = page.title()
        print(f"✅ 페이지 타이틀: {title}")

        # 스크린샷 저장 (선택적)
        page.screenshot(path="inflearn_homepage.png")
        print("📸 스크린샷 저장: inflearn_homepage.png")

        # 브라우저 종료
        browser.close()
        print("✅ 테스트 완료!")

if __name__ == "__main__":
    test_basic_scraping()