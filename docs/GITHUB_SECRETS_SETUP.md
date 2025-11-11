# GitHub Secrets 설정 가이드

## 개요

GitHub Actions 워크플로우가 정상적으로 동작하기 위해서는 다음 Secrets를 설정해야 합니다.

## 필수 Secrets

### 1. SUPABASE_URL (기존)

**설명**: Supabase 프로젝트 URL

**확인 방법**:
1. Supabase 대시보드 접속: https://supabase.com/dashboard
2. 프로젝트 선택
3. Settings → API → Project URL 복사

**형식 예시**: `https://xxxxxxxxxxxxx.supabase.co`

---

### 2. SUPABASE_SERVICE_ROLE_KEY (기존)

**설명**: Supabase Service Role Key (관리자 권한)

**확인 방법**:
1. Supabase 대시보드 접속
2. 프로젝트 선택
3. Settings → API → service_role (secret) 키 복사

**주의사항**:
- ⚠️ **절대 공개 저장소에 노출하지 마세요**
- anon public 키가 아닌 service_role 키를 사용해야 합니다

---

### 3. OPENAI_API_KEY (신규 추가 - Phase 7)

**설명**: OpenAI API 키 (GPT-4 사용)

**발급 방법**:
1. OpenAI 플랫폼 접속: https://platform.openai.com/
2. 로그인 후 API Keys 메뉴 선택
3. "Create new secret key" 클릭
4. 키 이름 입력 (예: "inflearn-affiliate-prod")
5. 생성된 키 복사 (⚠️ **한 번만 표시됩니다**)

**형식 예시**: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**비용 정보**:
- GPT-4 Turbo 가격: Input $0.01/1K tokens, Output $0.03/1K tokens
- 예상 월간 비용: ~$6.60 (일 20개 리뷰 기준)
- 월 예산 설정 권장: https://platform.openai.com/account/billing/limits

**주의사항**:
- ⚠️ **절대 공개하지 마세요**
- OpenAI 계정에 결제 수단이 등록되어 있어야 합니다
- API 사용량 모니터링: https://platform.openai.com/usage

---

### 4. SLACK_WEBHOOK_URL (선택사항)

**설명**: Slack 알림용 웹훅 URL

**발급 방법**:
1. Slack 워크스페이스에서 Incoming Webhooks 앱 설치
2. 알림을 받을 채널 선택
3. Webhook URL 복사

**형식 예시**: `https://hooks.slack.com/services/YOUR_WORKSPACE_ID/YOUR_CHANNEL_ID/YOUR_WEBHOOK_TOKEN`

**주의사항**:
- 선택사항이므로 없어도 워크플로우는 정상 동작합니다
- 실패 시 `continue-on-error: true`로 설정되어 있습니다

---

## GitHub Secrets 등록 방법

### 단계별 가이드

1. **GitHub 저장소 접속**
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPOSITORY
   ```

2. **Settings 메뉴 클릭**
   - 저장소 상단 탭에서 "Settings" 선택

3. **Secrets and variables 메뉴 이동**
   - 왼쪽 사이드바에서 "Secrets and variables" → "Actions" 클릭

4. **New repository secret 클릭**
   - "New repository secret" 버튼 클릭

5. **Secret 정보 입력**
   - **Name**: Secret 이름 (예: `OPENAI_API_KEY`)
   - **Secret**: 실제 값 입력
   - "Add secret" 버튼 클릭

6. **모든 필수 Secrets 반복 등록**
   - SUPABASE_URL
   - SUPABASE_SERVICE_ROLE_KEY
   - OPENAI_API_KEY
   - SLACK_WEBHOOK_URL (선택)

---

## 등록 확인

### 방법 1: Workflow 수동 실행

1. Actions 탭 이동
2. "Daily Scraping and AI Review Generation" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. 실행 로그에서 "✅ Verify Environment Variables" 단계 확인

### 방법 2: 로컬에서 환경 변수 테스트

```bash
# .env 파일 생성
cat > .env << EOF
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
EOF

# 환경 변수 로드 및 테스트
source .env
python -c "import os; print('✅ SUPABASE_URL:', os.getenv('SUPABASE_URL')[:20] + '...')"
python -c "import os; print('✅ SUPABASE_SERVICE_ROLE_KEY:', os.getenv('SUPABASE_SERVICE_ROLE_KEY')[:20] + '...')"
python -c "import os; print('✅ OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY')[:20] + '...')"
```

---

## 보안 권장사항

### 1. Secret 로테이션

- OpenAI API 키: 3-6개월마다 교체
- Supabase 키: 필요 시 재발급
- 이전 키는 즉시 삭제

### 2. 접근 권한 관리

- GitHub 저장소 접근 권한을 최소화
- Organization의 경우 Secret 접근 권한 별도 관리

### 3. 모니터링

- OpenAI 사용량 주간 확인
- 이상 패턴 감지 시 즉시 키 삭제 및 재발급

### 4. 로그 보안

- GitHub Actions 로그에 Secret이 노출되지 않도록 주의
- 디버깅 시 환경 변수 직접 출력 금지

---

## 문제 해결

### Error: OPENAI_API_KEY not set

**원인**: GitHub Secrets에 OPENAI_API_KEY가 등록되지 않음

**해결방법**:
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. Name: `OPENAI_API_KEY`
4. Secret: OpenAI API 키 입력

### Error: Invalid API Key

**원인**: 잘못된 API 키 또는 만료된 키

**해결방법**:
1. OpenAI 대시보드에서 키 유효성 확인
2. 새 키 발급 후 GitHub Secrets 업데이트

### Error: Insufficient quota

**원인**: OpenAI 계정 크레딧 부족

**해결방법**:
1. OpenAI 계정에 결제 수단 등록
2. 사용 한도 설정: https://platform.openai.com/account/billing/limits

---

## 환경 변수 목록 요약

| Secret Name | 설명 | 필수 여부 | Phase |
|-------------|------|-----------|-------|
| SUPABASE_URL | Supabase 프로젝트 URL | ✅ 필수 | Phase 6 |
| SUPABASE_SERVICE_ROLE_KEY | Supabase 관리자 키 | ✅ 필수 | Phase 6 |
| OPENAI_API_KEY | OpenAI API 키 | ✅ 필수 | Phase 7 |
| SLACK_WEBHOOK_URL | Slack 알림 웹훅 | ⚪ 선택 | Phase 6 |

---

## 추가 리소스

- [GitHub Encrypted Secrets 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OpenAI API Keys 관리](https://platform.openai.com/api-keys)
- [Supabase API 문서](https://supabase.com/docs/guides/api)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
