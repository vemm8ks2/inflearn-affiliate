# 인프런 강의 추천 자동화 시스템

인프런 강의 데이터를 자동 수집하고, AI로 리뷰를 생성하는 풀스택 자동화 프로젝트

## Tech Stack

- **Frontend**: Next.js 14 (App Router), Tailwind CSS
- **Backend**: Supabase (PostgreSQL), n8n
- **Scraping**: Playwright (Chromium)
- **AI**: OpenAI GPT-4
- **DevOps**: GitHub Actions, Vercel

## 프로젝트 구조

```
inflearn-affiliate/
├── scripts/                 # 스크래핑 스크립트
│   └── src/
│       ├── scraper.py      # 메인 스크래퍼
│       ├── config.py       # 설정 관리
│       ├── db_utils.py     # Supabase 연동
│       └── logger_config.py # 로깅 설정
├── venv/                   # Python 가상환경
├── run_scraper.bat         # Windows 실행 스크립트
└── run_scraper.sh          # Linux/Mac 실행 스크립트
```

## Getting Started

### 1. 프론트엔드 설정

```bash
npm install
npm run dev
```

### 2. 스크래핑 설정

#### 사전 요구사항

1. **Python 가상환경 활성화**
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

2. **Playwright 브라우저 설치 (최초 1회만)**
   ```bash
   # Windows
   venv\Scripts\python.exe -m playwright install chromium

   # Linux/Mac
   venv/bin/python -m playwright install chromium
   ```

3. **환경 변수 설정**

   `scripts/.env` 파일 생성:
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

#### 스크래핑 실행 방법

**방법 1: 편의 스크립트 사용 (권장)**

```bash
# Windows
run_scraper.bat

# Linux/Mac
./run_scraper.sh
```

**방법 2: 직접 실행**

```bash
cd scripts
python -m src.scraper
```

#### 스크래핑 설정 커스터마이징

`scripts/src/config.py`에서 다음 설정 가능:
- `MAX_COURSES`: 수집할 최대 강의 수 (기본값: 20)
- `HEADLESS`: 브라우저 숨김 모드 (기본값: False)
- `CATEGORY`: 수집할 카테고리 (기본값: "it-programming")

## Environment Variables

### 프론트엔드 (`.env.local`)

```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### 스크래핑 (`scripts/.env`)

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 스크래핑 결과 확인

스크래핑 실행 후 다음 파일이 생성됩니다:

- `scripts/output/courses_with_sales.json` - 수집된 강의 데이터
- `scripts/output/inflearn_screenshot.png` - 페이지 스크린샷
- `scripts/output/page_source.html` - HTML 소스
- `scripts/logs/scraper_YYYYMMDD.log` - 실행 로그

## 수집 데이터 구조

```json
{
  "metadata": {
    "version": "1.0.0",
    "total_courses": 20,
    "scraped_at": "2025-11-07T...",
    "scraping_duration_seconds": 49.64
  },
  "courses": [
    {
      "title": "강의 제목",
      "instructor": "강사명",
      "url": "https://www.inflearn.com/course/...",
      "original_price": 37400,
      "sale_price": 28050,
      "discount_rate": 25,
      "rating": 4.9,
      "review_count": 9,
      "student_count": 700
    }
  ]
}
```
