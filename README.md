# 한미 주식 투자 자문 AI 시스템 개발 요구사항

[![Build Status](https://github.com/your-username/dual_stock_adviser/workflows/CI/badge.svg)](https://github.com/your-username/dual_stock_adviser/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Coverage](https://codecov.io/gh/your-username/dual_stock_adviser/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/dual_stock_adviser)
[![Documentation](https://readthedocs.org/projects/dual-stock-adviser/badge/?version=latest)](https://dual-stock-adviser.readthedocs.io/)
[![CrewAI](https://img.shields.io/badge/CrewAI-latest-purple.svg)](https://github.com/joaomdmoura/crewAI)

## 📋 프로젝트 개요

CrewAI 프레임워크를 활용하여 한국과 미국 주식 시장의 종목을 분석하고, 매수/매도 의견을 제공하는 지능형 투자 자문 시스템을 구축합니다.

## 🚀 설치 및 설정

### 시스템 요구사항

- Python 3.8 이상
- 최소 4GB RAM
- 안정적인 인터넷 연결 (실시간 데이터 수집용)

### 설치 방법

1. **저장소 클론**
```bash
git clone https://github.com/your-username/dual_stock_adviser.git
cd dual_stock_adviser
```

2. **가상환경 생성 및 활성화**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경변수 설정**
```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일에 필요한 API 키 입력:
```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
NEWS_API_KEY=your_news_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Database
DATABASE_URL=sqlite:///stock_adviser.db

# Configuration
LOG_LEVEL=INFO
CACHE_TTL=300
```

## 🔧 빠른 시작

### 기본 사용법

```python
from stock_adviser import DualStockAdviser

# 시스템 초기화
adviser = DualStockAdviser()

# 종목 분석 (예: 삼성전자)
result = adviser.analyze_stock("005930.KS")
print(result.recommendation)

# 미국 종목 분석 (예: Apple)
result = adviser.analyze_stock("AAPL")
print(result.recommendation)
```

### 명령행 인터페이스

```bash
# 단일 종목 분석
python -m stock_adviser analyze --symbol "005930.KS" --market "KR"

# 여러 종목 비교 분석
python -m stock_adviser compare --symbols "AAPL,MSFT,GOOGL"

# 포트폴리오 분석
python -m stock_adviser portfolio --config "portfolio.yaml"
```

## 📁 프로젝트 구조

```
dual_stock_adviser/
├── src/
│   ├── stock_adviser/
│   │   ├── __init__.py
│   │   ├── main.py                 # 메인 애플리케이션
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── market_sentiment.py # 시장 심리 분석가
│   │   │   ├── risk_management.py  # 리스크 관리 전문가
│   │   │   └── investment_advisor.py # 투자 자문가
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── data_collector.py   # 데이터 수집 도구
│   │   │   ├── technical_analysis.py # 기술적 분석 도구
│   │   │   └── sentiment_analyzer.py # 감성 분석 도구
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── stock_data.py       # 주식 데이터 모델
│   │   │   └── analysis_result.py  # 분석 결과 모델
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_service.py     # 데이터 서비스
│   │   │   └── analysis_service.py # 분석 서비스
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── config.py           # 설정 관리
│   │       └── logger.py           # 로깅 설정
├── tests/
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_tools/
│   └── test_services/
├── docs/
│   ├── api.md                      # API 문서
│   ├── architecture.md             # 아키텍처 가이드
│   └── user_guide.md               # 사용자 가이드
├── config/
│   ├── agents.yaml                 # Agent 설정
│   ├── tasks.yaml                  # Task 설정
│   └── portfolio_example.yaml      # 포트폴리오 예제
├── requirements.txt                # 의존성 목록
├── requirements-dev.txt            # 개발 의존성
├── .env.example                    # 환경변수 예제
├── .gitignore
├── setup.py
└── README.md
```

## 🎯 목표

- 한국(KOSPI, KOSDAQ)과 미국(NYSE, NASDAQ) 주식 시장 동시 분석
- 데이터 기반의 객관적인 투자 의사결정 지원
- 다각도 분석을 통한 리스크 관리 및 수익 최적화

## 🏗️ 시스템 아키텍처

### Agent 구성 (Hierarchical Process)

시스템은 계층적 구조로 구성되며, Investment Advisor가 매니저 역할을 수행합니다.

#### 1. **Market Sentiment Analyst** (시장 심리 분석가)

- **역할**: 시장 전반의 심리와 투자자 정서 분석
- **주요 기능**:
  - 뉴스 헤드라인 감성 분석
  - 소셜 미디어 트렌드 모니터링
  - Fear & Greed Index 분석
  - 시장 변동성 지수(VIX, VKOSPI) 해석
- **출력**: 시장 심리 점수 및 투자 심리 보고서

#### 2. **Risk Management Specialist** (리스크 관리 전문가)

- **역할**: 포트폴리오 리스크 평가 및 관리
- **주요 기능**:
  - VaR(Value at Risk) 계산
  - 베타 계수 및 상관관계 분석
  - 섹터별 리스크 노출도 평가
  - 지정학적/규제 리스크 모니터링
- **출력**: 리스크 평가 보고서 및 헤지 전략

#### 3. **Investment Advisor** (투자 자문가) - Manager Role

- **역할**: 전체 분석 조율 및 최종 투자 의견 제시
- **주요 기능**:
  - 다른 agent들의 분석 결과 종합
  - 투자자 프로필에 맞는 전략 수립
  - 포트폴리오 배분 최적화
  - 매수/매도 타이밍 결정
- **출력**: 최종 투자 추천 보고서

## 🛠️ 기술 스택 및 도구

### 필수 라이브러리

```python
crewai>=0.1.0
yfinance  # 실시간 주식 데이터
pandas_ta  # 기술적 분석
nltk  # 자연어 처리
textblob  # 감성 분석
ta-lib  # 기술 지표 계산
numpy
pandas
```

### API 통합

1. **실시간 데이터**

   - Yahoo Finance API (무료)
   - Alpha Vantage API (기본 무료)
   - Polygon.io API (유료, 선택사항)

2. **뉴스 및 감성 분석**

   - Serper API (웹 검색)
   - News API (뉴스 수집)
   - Financial Modeling Prep (재무 데이터)

3. **한국 시장 전용**
   - KRX 정보데이터시스템
   - 네이버 금융 크롤링 (선택사항)

## 🛠️ 개발 환경 설정

### 개발 도구 설치

```bash
# 개발 의존성 설치
pip install -r requirements-dev.txt

# Pre-commit 훅 설정 (코드 품질 관리)
pre-commit install
```

### 코드 품질 도구

```bash
# 코드 포맷팅
black src/ tests/

# 린트 검사
flake8 src/ tests/

# 타입 체크
mypy src/

# 보안 취약점 검사
bandit -r src/
```

### 데이터베이스 설정

```bash
# SQLite 데이터베이스 초기화
python -m stock_adviser.utils.init_db

# 마이그레이션 실행 (필요시)
alembic upgrade head
```

### 개발 서버 실행

```bash
# 개발 모드 실행
python -m stock_adviser.main --dev

# API 서버 실행 (FastAPI)
uvicorn stock_adviser.api:app --reload --host 0.0.0.0 --port 8000
```

### 환경별 설정

| 환경 | 설정 파일 | 설명 |
|------|-----------|------|
| 개발 | `.env.development` | 로컬 개발 환경 |
| 테스트 | `.env.test` | 테스트 환경 |
| 운영 | `.env.production` | 운영 환경 |

## 📊 주요 기능 요구사항

### 1. 데이터 수집 및 처리

- 실시간 가격 데이터 수집 (5분/15분/일별)
- 재무제표 자동 수집 및 파싱
- 뉴스 기사 실시간 크롤링
- 기술적 지표 자동 계산 (MA, RSI, MACD, Bollinger Bands 등)

### 2. 분석 기능

- **기본 분석**: P/E, P/B, ROE, 부채비율 등
- **기술적 분석**: 차트 패턴 인식, 지지/저항선 식별
- **감성 분석**: 뉴스/소셜 미디어 긍정/부정 점수
- **상관관계 분석**: 섹터별, 국가별 상관관계

### 3. 의사결정 프로세스

```
1. 사용자 입력 (종목명 또는 조건)
   ↓
2. Market Sentiment Analyst: 시장 분위기 파악
   ↓
3. Risk Management Specialist: 리스크 요소 평가
   ↓
4. Investment Advisor: 종합 분석 및 의견 제시
   ↓
5. 최종 보고서 생성 (매수/매도/관망 + 근거)
```

### 4. 메모리 시스템

- **단기 메모리**:
  - 현재 세션의 분석 데이터 캐싱
  - 최근 조회한 종목 정보 저장
- **장기 메모리**:
  - 과거 추천 이력 및 성과 추적
  - 시장 패턴 학습 데이터 축적
  - 사용자별 투자 성향 프로파일

### 5. 사용자 맞춤화

- **투자 성향 설정**:

  - Conservative (보수적): 안정적 대형주 중심
  - Moderate (중도적): 균형잡힌 포트폴리오
  - Aggressive (공격적): 성장주/소형주 포함

- **투자 기간**:

  - 단기 (1주-1개월)
  - 중기 (1-6개월)
  - 장기 (6개월 이상)

- **리스크 허용도**:
  - Low: 최대 손실 -10%
  - Medium: 최대 손실 -20%
  - High: 최대 손실 -30% 이상

## 📝 출력 형식

### 최종 보고서 구조

```
=== 투자 분석 보고서 ===
[종목명] (티커: XXX)
분석 일시: YYYY-MM-DD HH:MM

📊 종합 평가: [매수/매도/관망]
신뢰도: XX%

📈 주요 지표
- 현재가: $XXX
- 목표가: $XXX
- 예상 수익률: ±XX%

🔍 세부 분석
1. 시장 심리: [긍정/중립/부정]
   - 뉴스 감성 점수: X.X/10
   - 투자자 심리 지수: XX

2. 리스크 평가: [낮음/중간/높음]
   - VaR (95%): -XX%
   - 베타: X.XX

3. 투자 의견
   - 진입 가격: $XXX
   - 손절 가격: $XXX
   - 목표 가격: $XXX

📌 핵심 근거
- [근거 1]
- [근거 2]
- [근거 3]

⚠️ 주의사항
- [리스크 요인 1]
- [리스크 요인 2]
```

## 🚀 구현 우선순위

### Phase 1 (MVP)

1. CrewAI 기본 구조 설정
2. Yahoo Finance 연동
3. 기본적인 3개 Agent 구현
4. 간단한 매수/매도 판단 로직

### Phase 2 (개선)

1. 뉴스 API 통합
2. 감성 분석 기능 추가
3. 기술적 분석 지표 확장
4. 한국 시장 데이터 통합

### Phase 3 (고도화)

1. 머신러닝 모델 통합
2. 백테스팅 기능
3. 포트폴리오 최적화
4. 실시간 알림 시스템

## 📖 API 문서

### RESTful API 엔드포인트

#### 주식 분석

```http
POST /api/v1/analyze
Content-Type: application/json

{
  "symbol": "005930.KS",
  "market": "KR",
  "analysis_type": "comprehensive",
  "user_profile": {
    "risk_tolerance": "medium",
    "investment_horizon": "long_term",
    "investment_style": "moderate"
  }
}
```

**응답 예시:**
```json
{
  "status": "success",
  "timestamp": "2024-01-01T10:00:00Z",
  "data": {
    "symbol": "005930.KS",
    "company_name": "삼성전자",
    "recommendation": "buy",
    "confidence": 0.85,
    "target_price": 75000,
    "current_price": 70000,
    "expected_return": 7.14,
    "risk_score": 0.65,
    "analysis": {
      "sentiment": {
        "score": 0.72,
        "category": "positive"
      },
      "technical": {
        "trend": "bullish",
        "indicators": {
          "rsi": 58.5,
          "macd": 1.23
        }
      },
      "fundamental": {
        "pe_ratio": 12.5,
        "pb_ratio": 1.1
      }
    }
  }
}
```

#### 포트폴리오 분석

```http
POST /api/v1/portfolio/analyze
Content-Type: application/json

{
  "holdings": [
    {"symbol": "005930.KS", "quantity": 100, "avg_cost": 68000},
    {"symbol": "AAPL", "quantity": 50, "avg_cost": 150.00}
  ],
  "cash": 1000000
}
```

#### 실시간 데이터

```http
GET /api/v1/market/data/{symbol}
```

```http
WebSocket: ws://localhost:8000/ws/market/{symbol}
```

### Python SDK

```python
from stock_adviser import StockAdviserClient

client = StockAdviserClient(api_key="your_api_key")

# 단일 종목 분석
result = client.analyze_stock("005930.KS")

# 포트폴리오 분석
portfolio = client.analyze_portfolio(holdings)

# 실시간 스트림
for update in client.stream_market_data("AAPL"):
    print(f"Price update: {update.price}")
```

## 🧪 테스트

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/test_agents/

# 커버리지 보고서 생성
pytest --cov=stock_adviser --cov-report=html

# 통합 테스트 실행
pytest tests/integration/

# API 테스트
pytest tests/api/
```

### 테스트 구조

- **Unit Tests**: 개별 컴포넌트 테스트
- **Integration Tests**: 시스템 통합 테스트  
- **API Tests**: REST API 엔드포인트 테스트
- **End-to-End Tests**: 전체 워크플로우 테스트

### 성능 테스트

```bash
# 부하 테스트 (Locust 사용)
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 메모리 프로파일링
python -m memory_profiler tests/performance/memory_test.py
```

## 💡 추가 고려사항

### 성능 최적화

- API 호출 횟수 제한 관리
- 데이터 캐싱 전략
- 비동기 처리로 응답 속도 개선

### 안정성

- 에러 핸들링 및 재시도 로직
- API 장애 시 대체 데이터 소스 활용
- 로깅 및 모니터링 시스템

## 🚨 문제 해결 가이드

### 일반적인 문제 및 해결책

#### 1. API 키 관련 오류

**문제**: `API key not found` 또는 `Unauthorized` 오류
```
APIError: Invalid API key for service: alpha_vantage
```

**해결책**:
```bash
# .env 파일 확인
cat .env | grep API_KEY

# 환경변수 확인
echo $OPENAI_API_KEY

# 새로운 API 키 설정
export OPENAI_API_KEY="your_new_api_key"
```

#### 2. 데이터 수집 실패

**문제**: 주식 데이터를 가져올 수 없음
```
DataCollectionError: Failed to fetch data for symbol: 005930.KS
```

**해결책**:
```python
# 디버그 모드로 실행
python -m stock_adviser analyze --symbol "005930.KS" --debug

# 대체 데이터 소스 사용
python -m stock_adviser analyze --symbol "005930.KS" --fallback
```

#### 3. 메모리 부족

**문제**: 대량 데이터 처리 시 메모리 부족
```
MemoryError: Unable to allocate array
```

**해결책**:
```python
# 배치 크기 축소
config.update({
    "batch_size": 50,
    "max_concurrent_requests": 2
})

# 캐시 정리
python -m stock_adviser utils clear-cache
```

#### 4. 네트워크 연결 오류

**문제**: API 서버와 연결 실패
```
ConnectionError: Unable to connect to API server
```

**해결책**:
```bash
# 네트워크 연결 확인
ping api.example.com

# 프록시 설정 (필요시)
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### 디버깅 도구

#### 로그 레벨 설정

```bash
# 디버그 로그 활성화
export LOG_LEVEL=DEBUG

# 특정 모듈 로그만 활성화
export LOG_MODULES="agents,tools"
```

#### 성능 모니터링

```bash
# 메모리 사용량 모니터링
python -m memory_profiler stock_adviser/main.py

# CPU 사용량 프로파일링
python -m cProfile -o profile.stats stock_adviser/main.py
```

#### 데이터 검증

```bash
# 데이터 무결성 확인
python -m stock_adviser utils validate-data --symbol "005930.KS"

# 캐시 상태 확인
python -m stock_adviser utils cache-status
```

### 로그 파일 위치

- **애플리케이션 로그**: `logs/app.log`
- **에러 로그**: `logs/error.log`
- **API 요청 로그**: `logs/api.log`
- **성능 로그**: `logs/performance.log`

### 지원 요청

문제가 해결되지 않는 경우:

1. **이슈 템플릿 사용**: GitHub Issues에서 버그 리포트 템플릿 사용
2. **로그 첨부**: 관련 로그 파일과 에러 메시지 포함
3. **환경 정보 제공**: Python 버전, OS, 의존성 버전
4. **재현 단계**: 문제 재현을 위한 단계별 설명

## ⚙️ 상세 설정 가이드

### 환경변수 상세 설정

```bash
# Core Settings
ENVIRONMENT=development                    # development, test, production
LOG_LEVEL=INFO                            # DEBUG, INFO, WARNING, ERROR
DEBUG=true                                # Enable debug mode

# API Configuration
API_RATE_LIMIT=100                        # Requests per minute
API_TIMEOUT=30                            # Request timeout in seconds
API_RETRY_ATTEMPTS=3                      # Number of retry attempts
API_BACKOFF_FACTOR=2                      # Backoff multiplier

# Data Sources
DATA_PROVIDER_PRIMARY=yfinance            # Primary data provider
DATA_PROVIDER_FALLBACK=alpha_vantage      # Fallback data provider
CACHE_ENABLED=true                        # Enable response caching
CACHE_TTL=300                             # Cache time-to-live in seconds

# Analysis Settings
SENTIMENT_THRESHOLD=0.6                   # Sentiment analysis threshold
RISK_CALCULATION_METHOD=var               # VaR calculation method
CONFIDENCE_INTERVAL=0.95                  # Statistical confidence level

# Database
DATABASE_POOL_SIZE=10                     # Connection pool size
DATABASE_POOL_RECYCLE=3600               # Pool recycle time
DATABASE_ECHO=false                       # Echo SQL queries

# Security
JWT_SECRET_KEY=your_jwt_secret_key        # JWT signing key
SESSION_TIMEOUT=3600                      # Session timeout in seconds
ENABLE_RATE_LIMITING=true                # Enable API rate limiting
```

### Agent 설정 커스터마이징

`config/agents.yaml` 파일을 통해 Agent 동작을 세부 조정할 수 있습니다:

```yaml
agents:
  market_sentiment:
    max_iterations: 3
    temperature: 0.3
    tools: ["sentiment_analyzer", "news_scraper"]
    memory_enabled: true
    
  risk_management:
    max_iterations: 2
    temperature: 0.1
    tools: ["var_calculator", "correlation_analyzer"]
    confidence_threshold: 0.8
    
  investment_advisor:
    max_iterations: 5
    temperature: 0.5
    tools: ["all"]
    delegation_enabled: true
```

## 📚 참고 자료

- [CrewAI Documentation](https://docs.crewai.com/)
- [Yahoo Finance API Guide](https://pypi.org/project/yfinance/)
- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)

## 🤝 기여하기 (Contributing)

이 프로젝트에 기여해주셔서 감사합니다! 다음 가이드라인을 따라주세요.

### 개발 워크플로우

1. **Fork & Clone**
```bash
# 저장소 Fork 후 클론
git clone https://github.com/your-username/dual_stock_adviser.git
cd dual_stock_adviser

# 업스트림 저장소 추가
git remote add upstream https://github.com/original-username/dual_stock_adviser.git
```

2. **브랜치 생성**
```bash
# feature 브랜치 생성
git checkout -b feature/your-feature-name

# bugfix 브랜치 생성  
git checkout -b bugfix/issue-number
```

3. **개발 환경 설정**
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 개발 의존성 설치
pip install -r requirements-dev.txt
pip install -e .

# pre-commit 훅 설정
pre-commit install
```

### 코드 스타일 가이드

- **Python**: PEP 8 준수, Black 포맷터 사용
- **Docstrings**: Google 스타일 docstring 사용
- **Type Hints**: 모든 함수와 메서드에 타입 힌트 추가
- **테스트**: 새로운 기능에 대한 테스트 코드 필수

### 커밋 메시지 컨벤션

```
<type>(<scope>): <subject>

<body>

<footer>
```

**타입**:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 스타일 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 기타 작업

**예시**:
```
feat(agents): add sentiment analysis for Korean news

- Implement Korean text preprocessing
- Add Naver news API integration
- Update sentiment scoring algorithm

Closes #123
```

### Pull Request 가이드라인

1. **PR 전 체크리스트**
   - [ ] 모든 테스트 통과
   - [ ] 코드 스타일 검사 통과
   - [ ] 문서 업데이트 완료
   - [ ] CHANGELOG 업데이트

2. **PR 템플릿**
```markdown
## 변경 사항 요약
- 

## 테스트
- [ ] 단위 테스트 추가/수정
- [ ] 통합 테스트 확인
- [ ] 수동 테스트 완료

## 체크리스트
- [ ] 코드 리뷰 준비 완료
- [ ] 문서 업데이트 완료
- [ ] 브레이킹 체인지 여부 확인
```

### 이슈 리포팅

버그 리포트나 기능 요청 시 다음 템플릿을 사용해주세요:

**버그 리포트**:
```markdown
## 버그 설명
간단한 버그 설명

## 재현 단계
1. 
2. 
3. 

## 예상 동작
예상했던 동작 설명

## 실제 동작
실제로 발생한 동작 설명

## 환경 정보
- OS: 
- Python 버전: 
- 프로젝트 버전: 

## 추가 정보
스크린샷, 로그 파일 등
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

```
MIT License

Copyright (c) 2024 Dual Stock Adviser Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 감사의 말

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent AI framework
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance market data
- [TA-Lib](https://github.com/mrjbq7/ta-lib) - Technical analysis library
- 모든 기여자들과 오픈소스 커뮤니티

---

**면책 조항**: 이 시스템은 교육 및 연구 목적으로 제작되었습니다. 투자 결정은 본인의 책임하에 이루어져야 하며, 시스템의 분석 결과로 인한 손실에 대해 개발자는 책임지지 않습니다.
