from crewai import Agent, Task, Crew
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

from ..models import MarketSentiment, AgentAnalysis
from ..utils import app_logger, analysis_logger, settings


class MarketSentimentAgent:
    """시장 심리 분석 전문가"""
    
    def __init__(self, tools: List[Any] = None):
        self.tools = tools or []
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Agent 생성"""
        return Agent(
            role="Market Sentiment Analyst",
            goal="시장 전반의 심리와 투자자 정서를 정확하게 분석하여 투자 결정에 도움이 되는 인사이트를 제공한다.",
            backstory="""
            당신은 15년 경력의 시장 심리 분석 전문가입니다. 
            뉴스, 소셜미디어, 경제지표를 종합적으로 분석하여 시장의 정서를 파악하는데 탁월한 능력을 보유하고 있습니다.
            
            특히 다음 분야에 전문성을 가지고 있습니다:
            - 뉴스 헤드라인 감성 분석
            - 소셜 미디어 트렌드 모니터링  
            - Fear & Greed Index 해석
            - VIX, VKOSPI 등 변동성 지수 분석
            - 한국과 미국 시장의 상호작용 분석
            
            항상 객관적이고 데이터에 기반한 분석을 제공하며, 
            감정적 편향을 배제하고 사실에 근거한 판단을 내립니다.
            """,
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            max_iter=3
        )
    
    def create_sentiment_analysis_task(self, symbol: str, company_name: str, market: str) -> Task:
        """시장 심리 분석 태스크 생성"""
        return Task(
            description=f"""
            {company_name} ({symbol})의 시장 심리를 종합적으로 분석하세요.
            
            분석 범위:
            1. 뉴스 감성 분석
               - 최근 1주일 뉴스 헤드라인 분석
               - 긍정/중립/부정 뉴스 비율
               - 주요 뉴스 이슈와 시장 반응
               
            2. 소셜 미디어 트렌드 (가능한 경우)
               - 투자자 정서 파악
               - 주요 논의 이슈
               - 감정적 편향도 측정
               
            3. 시장 지표 분석
               - Fear & Greed Index 현재 상태
               - VIX (US) / VKOSPI (KR) 분석
               - 시장 변동성 해석
               
            4. 동종업계/섹터 심리
               - 섹터 전반 투자심리
               - 경쟁사 대비 상대적 평가
               
            5. 거시경제 환경
               - 금리 환경과 투자 심리
               - 경제 정책이 해당 종목에 미치는 영향
               
            최종 결과물:
            - 감성 점수 (-1.0 ~ 1.0)
            - 감성 카테고리 (positive/neutral/negative)
            - 신뢰도 점수 (0.0 ~ 1.0)
            - 주요 감성 드라이버 3-5개
            - 향후 1개월 감성 전망
            
            Market: {market}
            분석 기준일: {datetime.now().strftime('%Y-%m-%d')}
            """,
            agent=self.agent,
            expected_output="""
            시장 심리 분석 결과를 다음 JSON 형태로 제공:
            {
                "sentiment_score": -0.5 ~ 1.0,
                "sentiment_category": "positive/neutral/negative", 
                "confidence": 0.0 ~ 1.0,
                "key_drivers": ["드라이버1", "드라이버2", ...],
                "news_sentiment": -1.0 ~ 1.0,
                "social_sentiment": -1.0 ~ 1.0 (선택적),
                "fear_greed_index": 0 ~ 100,
                "volatility_analysis": "분석 내용",
                "outlook": "향후 전망",
                "risk_factors": ["리스크1", "리스크2", ...]
            }
            """
        )
    
    def analyze_sentiment(self, symbol: str, company_name: str, market: str) -> AgentAnalysis:
        """시장 심리 분석 실행"""
        analysis_logger.log_analysis_start(symbol, "market_sentiment")
        start_time = datetime.now()
        
        try:
            # 태스크 생성
            sentiment_task = self.create_sentiment_analysis_task(symbol, company_name, market)
            
            # Crew 생성 및 실행
            crew = Crew(
                agents=[self.agent],
                tasks=[sentiment_task],
                verbose=True
            )
            
            # 분석 실행
            result = crew.kickoff()
            
            # 결과 파싱 (실제로는 더 정교한 파싱 로직 필요)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # AgentAnalysis 객체 생성
            agent_analysis = AgentAnalysis(
                agent_name="Market Sentiment Analyst",
                analysis_type="sentiment",
                summary=f"{company_name}의 시장 심리 분석을 완료했습니다.",
                key_points=[
                    "뉴스 감성 분석 수행",
                    "시장 변동성 지수 검토", 
                    "투자자 정서 파악",
                    "섹터 심리 분석"
                ],
                confidence_score=Decimal('0.8'),
                data={
                    "raw_analysis": str(result),
                    "processing_time": processing_time
                }
            )
            
            analysis_logger.log_analysis_complete(symbol, agent_analysis.to_dict(), processing_time)
            analysis_logger.log_agent_execution("Market Sentiment Analyst", symbol, processing_time, True)
            
            return agent_analysis
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            analysis_logger.log_analysis_error(symbol, e)
            analysis_logger.log_agent_execution("Market Sentiment Analyst", symbol, processing_time, False)
            
            # 에러 시에도 기본 분석 결과 반환
            return AgentAnalysis(
                agent_name="Market Sentiment Analyst",
                analysis_type="sentiment",
                summary=f"시장 심리 분석 중 오류가 발생했습니다: {str(e)}",
                key_points=["분석 실패"],
                confidence_score=Decimal('0.1'),
                data={"error": str(e), "processing_time": processing_time}
            )
    
    def get_market_sentiment_score(self, symbol: str, market: str) -> MarketSentiment:
        """시장 심리 점수 계산"""
        try:
            # 실제 구현에서는 뉴스 데이터, 소셜미디어 데이터 등을 수집하여 계산
            # 현재는 더미 데이터로 구현
            
            # 기본 감성 점수 (더미)
            sentiment_score = Decimal('0.2')  # 약간 긍정적
            news_sentiment = Decimal('0.3')
            
            # 감성 카테고리 결정
            if sentiment_score > 0.2:
                sentiment_category = "positive"
            elif sentiment_score < -0.2:
                sentiment_category = "negative"
            else:
                sentiment_category = "neutral"
            
            return MarketSentiment(
                symbol=symbol,
                sentiment_score=sentiment_score,
                sentiment_category=sentiment_category,
                news_sentiment=news_sentiment,
                confidence=Decimal('0.7')
            )
            
        except Exception as e:
            app_logger.error(f"시장 심리 점수 계산 실패: {symbol}, 오류: {str(e)}")
            
            # 기본값 반환
            return MarketSentiment(
                symbol=symbol,
                sentiment_score=Decimal('0.0'),
                sentiment_category="neutral",
                news_sentiment=Decimal('0.0'),
                confidence=Decimal('0.1')
            )
    
    def update_tools(self, tools: List[Any]):
        """도구 업데이트"""
        self.tools = tools
        self.agent.tools = tools