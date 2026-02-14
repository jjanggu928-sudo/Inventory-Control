# 재고마스터 설치 및 설정 가이드

## 📋 목차
1. [로컬 개발 환경 설정](#로컬-개발-환경-설정)
2. [Supabase 설정](#supabase-설정)
3. [GitHub 연동](#github-연동)
4. [Render 배포](#render-배포)
5. [문제 해결](#문제-해결)

---

## 🏠 로컬 개발 환경 설정

### 1. 저장소 클론
```bash
git clone <your-repository-url>
cd Inventory_Control
```

### 2. Python 가상환경 생성 (Windows)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. Python 가상환경 생성 (Mac/Linux)
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# .env.example을 .env로 복사
copy .env.example .env  # Windows
# 또는
cp .env.example .env    # Mac/Linux
```

`.env` 파일을 열고 Supabase 정보 입력:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
```

### 5. 앱 실행
```bash
streamlit run app/main.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 🗄️ Supabase 설정

### 1. Supabase 프로젝트 생성
1. https://supabase.com 접속
2. "New Project" 클릭
3. 프로젝트 이름, 비밀번호, 리전 설정
4. 프로젝트 생성 대기 (약 2분)

### 2. 데이터베이스 스키마 생성
1. Supabase 대시보드에서 "SQL Editor" 선택
2. "New Query" 클릭
3. `database_schema.sql` 파일의 내용을 복사하여 붙여넣기
4. "Run" 버튼 클릭하여 실행

### 3. API 키 확인
1. Supabase 대시보드에서 "Settings" → "API" 선택
2. **Project URL** 복사
3. **anon public** 키 복사
4. `.env` 파일에 입력

### 4. 이메일 인증 설정 (선택사항)
1. "Authentication" → "Email Templates" 선택
2. 이메일 템플릿 커스터마이징 가능
3. "Authentication" → "Providers" 에서 이메일 인증 활성화 확인

---

## 🔗 GitHub 연동

### 1. 로컬 Git 초기화
```bash
cd C:\개발관련\Inventory_Control

# Git 초기화 (이미 클론한 경우 생략)
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: 재고마스터 프로젝트"
```

### 2. GitHub 저장소 연결
```bash
# 원격 저장소 추가
git remote add origin <your-github-repo-url>

# 푸시
git push -u origin main
```

### 3. .gitignore 확인
`.env` 파일이 Git에 포함되지 않도록 `.gitignore`에 이미 추가되어 있는지 확인하세요.

---

## 🚀 Render 배포

### 1. Render 계정 생성
1. https://render.com 접속
2. GitHub 계정으로 로그인

### 2. Web Service 생성
1. Dashboard에서 "New +" → "Web Service" 선택
2. GitHub 저장소 연결
3. 저장소 선택: `Inventory_Control`

### 3. 배포 설정
**Settings 입력:**
- **Name**: `inventory-master` (또는 원하는 이름)
- **Region**: Singapore (한국과 가까움)
- **Branch**: `main`
- **Root Directory**: (비워둠)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0`

### 4. 환경변수 설정
"Environment" 섹션에서 "Add Environment Variable" 클릭:

```
SUPABASE_URL = https://your-project-id.supabase.co
SUPABASE_KEY = your-anon-public-key
```

### 5. 배포
"Create Web Service" 클릭하여 배포 시작

배포 완료 후 제공되는 URL로 접속:
```
https://inventory-master-xxxx.onrender.com
```

### 6. 무료 티어 주의사항
- 15분간 요청이 없으면 슬립 모드
- 다음 접속 시 약 30초 로딩 시간
- 월 750시간 무료 (1개 서비스 상시 운영 가능)

---

## 🛠️ 문제 해결

### Q1: ModuleNotFoundError 발생
```bash
# 가상환경이 활성화되었는지 확인
# 프롬프트 앞에 (venv) 표시가 있어야 함

# 패키지 재설치
pip install -r requirements.txt
```

### Q2: Supabase 연결 오류
```
ValueError: SUPABASE_URL과 SUPABASE_KEY를 .env 파일에 설정해주세요.
```
**해결:**
1. `.env` 파일이 존재하는지 확인
2. URL과 KEY가 정확한지 확인 (공백 없이)
3. 파일이 프로젝트 루트에 있는지 확인

### Q3: 로그인이 안됨
**해결:**
1. Supabase에서 이메일 인증이 활성화되었는지 확인
2. 회원가입 후 이메일 확인
3. Supabase Dashboard → Authentication → Users 에서 사용자 확인

### Q4: 데이터베이스 테이블이 없음
**해결:**
1. `database_schema.sql` 파일을 Supabase SQL Editor에서 실행했는지 확인
2. Supabase Dashboard → Table Editor에서 테이블 확인

### Q5: Render 배포 실패
**해결:**
1. 빌드 로그 확인
2. `requirements.txt` 파일이 있는지 확인
3. Start Command 재확인:
   ```
   streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0
   ```

### Q6: 포트 충돌 (로컬)
```
OSError: [Errno 48] Address already in use
```
**해결:**
```bash
# 다른 포트로 실행
streamlit run app/main.py --server.port=8502
```

---

## 📞 추가 도움

문제가 해결되지 않으면:
1. GitHub Issues에 문의
2. Supabase 공식 문서: https://supabase.com/docs
3. Streamlit 공식 문서: https://docs.streamlit.io
4. Render 공식 문서: https://render.com/docs

---

## 🎯 다음 단계

로컬 개발이 완료되었다면:
1. ✅ 기능 테스트
2. ✅ 실제 데이터로 사용해보기
3. ✅ 피드백 수집
4. ✅ 기능 개선
5. ✅ 프로덕션 배포

Good luck! 🚀
