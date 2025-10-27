# 인프런 강의 추천 자동화 시스템

인프런 강의 데이터를 자동 수집하고, AI로 리뷰를 생성하는 풀스택 자동화 프로젝트

## Tech Stack

- **Frontend**: Next.js 14 (App Router), Tailwind CSS
- **Backend**: Supabase (PostgreSQL), n8n
- **AI**: OpenAI GPT-4
- **DevOps**: GitHub Actions, Vercel

## Getting Started

```bash
npm install
npm run dev
```

## Environment Variables

`.env.local` 파일 생성 후:

```bash
NEXT_PUBLIC_SUPABASE_URL=your_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key
```
