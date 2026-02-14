# 재고마스터 (Inventory Master)

소상공인을 위한 간편한 재고관리 시스템

## 기능

- 🔐 사용자 인증 (Supabase Auth)
- 📦 상품 관리 (등록/조회/수정/삭제)
- 📥 입고 관리
- 📤 출고 관리
- 📊 재고 현황 대시보드
- 📈 통계 및 리포트

## 기술 스택

- **Frontend/Backend**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Deployment**: Render
- **Version Control**: GitHub

## 설치 및 실행

### 1. 저장소 클론

```bash
git clone <your-repo-url>
cd Inventory_Control
```

### 2. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env.example` 파일을 `.env`로 복사하고 Supabase 정보를 입력하세요.

```bash
cp .env.example .env
```

`.env` 파일 내용:
```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
```

### 5. 앱 실행

```bash
streamlit run app/main.py
```

브라우저에서 `http://localhost:8501` 접속

## 프로젝트 구조

```
Inventory_Control/
├── app/
│   ├── main.py              # 메인 앱
│   ├── pages/               # 멀티페이지
│   │   ├── 1_상품관리.py
│   │   ├── 2_입출고관리.py
│   │   └── 3_대시보드.py
│   └── utils/               # 유틸리티
│       ├── database.py      # DB 연결
│       ├── auth.py          # 인증
│       └── helpers.py       # 헬퍼 함수
├── .env                     # 환경변수 (git 제외)
├── .env.example             # 환경변수 템플릿
├── .gitignore
├── requirements.txt
└── README.md
```

## Supabase 데이터베이스 스키마

### products (상품)
- id: uuid (PK)
- user_id: uuid (FK)
- name: text
- sku: text (상품코드)
- category: text
- unit: text (단위)
- unit_price: numeric
- current_stock: integer
- min_stock: integer (최소재고)
- created_at: timestamp
- updated_at: timestamp

### transactions (입출고)
- id: uuid (PK)
- user_id: uuid (FK)
- product_id: uuid (FK)
- type: text (입고/출고)
- quantity: integer
- unit_price: numeric
- total_price: numeric
- memo: text
- transaction_date: timestamp
- created_at: timestamp

## 배포 (Render)

1. Render 계정 생성
2. New Web Service 선택
3. GitHub 저장소 연결
4. 환경변수 설정
5. 배포

## 라이선스

MIT License

## 문의

Issues 탭에서 문의해주세요.
