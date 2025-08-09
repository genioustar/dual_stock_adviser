from crewai import Agent, Task, Crew, Process
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

from ..models import (
    RecommendationType, RiskLevel, AgentAnalysis, PriceTarget, 
    InvestmentRationale, PerformanceMetrics, StockAnalysisResult
)
from ..utils import app_logger, analysis_logger


class InvestmentAdvisorAgent:
    """투자 자문가 (Manager Role)"""
    
    def __init__(self, tools: List[Any] = None):
        self.tools = tools or []
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Manager Agent 생성"""
        return Agent(
            role="Senior Investment Advisor",
            goal="다양한 분석 결과를 종합하여 최적의 투자 의사결정과 전략을 제공한다.",
            backstory="""
            당신은 25년 경력의 시니어 투자 자문가로, 국내외 주요 자산운용사에서
            포트폴리오 매니저와 투자 전략 책임자를 역임했습니다.
            
            CFA(Chartered Financial Analyst) 자격을 보유하고 있으며,
            한국과 미국 시장에서 일관되게 우수한 성과를 거두어왔습니다.
            
            전문 분야:
            - 멀티 팩터 투자 전략
            - 글로벌 자산 배분
            - 리스크 조정 수익률 최적화
            - 행동 금융학 기반 투자 심리 분석
            - ESG 투자 전략
            
            투자 철학:
            - 장기적 가치 창출 중시
            - 리스크 대비 수익률 최적화
            - 분산 투자의 중요성 인식
            - 시장 효율성과 비효율성의 균형적 이해
            - 투자자 개인의 목표와 성향 존중
            
            항상 객관적이고 균형잡힌 시각으로 투자 의견을 제시하며,
            다른 전문가들의 의견을 종합하여 최종 판단을 내립니다.
            """,
            verbose=True,
            allow_delegation=True,  # Manager 역할이므로 delegation 허용
            tools=self.tools,
            max_iter=5
        )
    
    def create_investment_analysis_task(
        self, 
        symbol: str, 
        company_name: str, 
        market: str,
        sentiment_analysis: Optional[AgentAnalysis] = None,
        risk_analysis: Optional[AgentAnalysis] = None,
        user_profile: Optional[Dict] = None
    ) -> Task:
        """투자 분석 통합 태스크 생성"""
        
        user_context = ""
        if user_profile:
            risk_tolerance = user_profile.get('risk_tolerance', 'medium')
            investment_horizon = user_profile.get('investment_horizon', 'medium_term')
            investment_style = user_profile.get('investment_style', 'moderate')
            
            user_context = f"""
            투자자 프로필:
            - 위험 허용도: {risk_tolerance}
            - 투자 기간: {investment_horizon}  
            - 투자 스타일: {investment_style}
            """
        
        sentiment_context = ""
        if sentiment_analysis:
            sentiment_context = f"""
            시장 심리 분석 결과:
            - 전문가: {sentiment_analysis.agent_name}
            - 요약: {sentiment_analysis.summary}
            - 주요 포인트: {', '.join(sentiment_analysis.key_points)}
            - 신뢰도: {float(sentiment_analysis.confidence_score):.1%}
            """
            
        risk_context = ""
        if risk_analysis:
            risk_context = f"""
            리스크 분석 결과:
            - 전문가: {risk_analysis.agent_name}
            - 요약: {risk_analysis.summary}
            - 주요 포인트: {', '.join(risk_analysis.key_points)}
            - 신뢰도: {float(risk_analysis.confidence_score):.1%}
            """
        
        return Task(
            description=f"""
            {company_name} ({symbol})에 대한 종합적인 투자 분석을 수행하고 
            최종 투자 추천을 제시하세요.
            
            {user_context}
            
            분석 통합 과정:
            1. 기존 분석 결과 검토
            {sentiment_context}
            
            {risk_context}
            
            2. 추가 분석 수행
               - 기술적 분석 (차트 패턴, 기술 지표)
               - 기본적 분석 (재무제표, 밸류에이션)
               - 동종업계 비교 분석
               - 거시경제 환경 분석
               
            3. 종합 투자 의견 도출
               - 매수/매도/중립 추천
               - 목표가 설정 (진입가, 목표가, 손절가)
               - 투자 기간별 전략
               - 포지션 사이징 권고
               
            4. 시나리오 분석
               - 베이스 케이스 (확률 60%)
               - 불 케이스 (확률 20%)  
               - 베어 케이스 (확률 20%)
               
            5. 투자자별 맞춤 조언
               - 보수적 투자자를 위한 조언
               - 공격적 투자자를 위한 조언
               - 리스크 관리 방안
               
            Market: {market}
            분석 기준일: {datetime.now().strftime('%Y-%m-%d')}
            """,
            agent=self.agent,
            expected_output="""
            투자 분석 결과를 다음 JSON 형태로 제공:
            {
                "recommendation": "strong_buy/buy/hold/sell/strong_sell",
                "confidence_level": 0.0 ~ 1.0,
                "price_targets": {
                    "target_price": 목표가,
                    "entry_price": 적정 진입가,
                    "stop_loss": 손절가,
                    "time_horizon": "short_term/medium_term/long_term"
                },
                "rationale": {
                    "positive_factors": ["긍정 요인1", "긍정 요인2", ...],
                    "negative_factors": ["부정 요인1", "부정 요인2", ...],
                    "risk_factors": ["리스크 요인1", "리스크 요인2", ...],
                    "catalysts": ["성장 동력1", "성장 동력2", ...]
                },
                "performance_metrics": {
                    "expected_return": 예상 수익률,
                    "expected_volatility": 예상 변동성,
                    "win_probability": 수익 확률,
                    "risk_reward_ratio": 위험 대비 수익률
                },
                "scenario_analysis": {
                    "base_case": {"probability": 0.6, "return": "수익률", "description": "설명"},
                    "bull_case": {"probability": 0.2, "return": "수익률", "description": "설명"},  
                    "bear_case": {"probability": 0.2, "return": "수익률", "description": "설명"}
                },
                "portfolio_advice": {
                    "position_size": "권고 비중",
                    "diversification": "분산 투자 조언",
                    "rebalancing": "리밸런싱 시점"
                },
                "risk_management": {
                    "stop_loss_strategy": "손절 전략",
                    "hedging_options": "헤지 옵션",
                    "monitoring_points": ["모니터링 포인트1", ...]
                }
            }
            """
        )
    
    def analyze_investment(
        self, 
        symbol: str, 
        company_name: str, 
        current_price: Decimal,
        market: str,
        sentiment_analysis: Optional[AgentAnalysis] = None,
        risk_analysis: Optional[AgentAnalysis] = None,
        user_profile: Optional[Dict] = None
    ) -> StockAnalysisResult:
        """종합 투자 분석 실행"""
        analysis_logger.log_analysis_start(symbol, "investment_advisor")
        start_time = datetime.now()
        
        try:
            # 태스크 생성
            investment_task = self.create_investment_analysis_task(
                symbol, company_name, market, sentiment_analysis, risk_analysis, user_profile
            )
            
            # Crew 생성 및 실행 (hierarchical process로 매니저 역할 수행)
            crew = Crew(
                agents=[self.agent],
                tasks=[investment_task],
                process=Process.hierarchical,
                manager_llm="gpt-4",  # 매니저용 LLM
                verbose=True
            )
            
            # 분석 실행
            result = crew.kickoff()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 결과 파싱 및 StockAnalysisResult 생성
            analysis_result = self._create_analysis_result(
                symbol, company_name, current_price, result, 
                sentiment_analysis, risk_analysis, processing_time
            )
            
            analysis_logger.log_analysis_complete(symbol, analysis_result.to_dict(), processing_time)
            analysis_logger.log_agent_execution("Investment Advisor", symbol, processing_time, True)
            
            return analysis_result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            analysis_logger.log_analysis_error(symbol, e)
            analysis_logger.log_agent_execution("Investment Advisor", symbol, processing_time, False)
            
            # 에러 시 기본 결과 반환
            return self._create_default_analysis_result(symbol, company_name, current_price, str(e))
    
    def _create_analysis_result(
        self,
        symbol: str,
        company_name: str, 
        current_price: Decimal,
        raw_result: str,
        sentiment_analysis: Optional[AgentAnalysis],
        risk_analysis: Optional[AgentAnalysis],
        processing_time: float
    ) -> StockAnalysisResult:
        """분석 결과 객체 생성"""
        
        # 실제로는 raw_result를 파싱하여 구조화된 데이터 추출
        # 현재는 더미 데이터로 구현
        
        # 추천 결정 (더미 로직)
        recommendation = RecommendationType.BUY  # 기본값
        confidence_level = Decimal('0.75')
        risk_level = RiskLevel.MEDIUM
        
        # 가격 타겟 설정
        target_price_factor = Decimal('1.15')  # 15% 상승 목표
        price_targets = PriceTarget(
            target_price=current_price * target_price_factor,
            entry_price=current_price * Decimal('0.98'),  # 2% 하락 시 진입
            stop_loss=current_price * Decimal('0.90'),    # 10% 손절
            take_profit=current_price * target_price_factor,
            time_horizon="medium_term"
        )
        
        # 투자 근거
        rationale = InvestmentRationale(
            positive_factors=["시장 심리 개선", "펀더멘털 양호", "기술적 강세"],
            negative_factors=["거시경제 불확실성", "업종 경쟁 심화"],
            risk_factors=["시장 변동성", "규제 변화 가능성"],
            catalysts=["신제품 출시", "실적 개선 기대", "시장 확대"]
        )
        
        # 성과 지표
        performance_metrics = PerformanceMetrics(
            expected_return=Decimal('0.15'),  # 15% 기대수익률
            expected_volatility=Decimal('0.25'),  # 25% 변동성
            sharpe_ratio_expected=Decimal('0.60'),
            max_loss_probability=Decimal('0.20'),  # 20% 손실 확률
            win_probability=Decimal('0.65')  # 65% 수익 확률
        )
        
        # StockAnalysisResult 생성
        analysis_result = StockAnalysisResult(
            symbol=symbol,
            company_name=company_name,
            current_price=current_price,
            analysis_date=datetime.now(),
            recommendation=recommendation,
            confidence_level=confidence_level,
            risk_level=risk_level,
            price_targets=price_targets,
            rationale=rationale,
            performance_metrics=performance_metrics,
            processing_time=processing_time
        )
        
        # Agent 분석 결과들 추가
        if sentiment_analysis:
            analysis_result.add_agent_analysis(sentiment_analysis)
        if risk_analysis:
            analysis_result.add_agent_analysis(risk_analysis)
            
        # 자체 분석 결과 추가
        advisor_analysis = AgentAnalysis(
            agent_name="Investment Advisor",
            analysis_type="investment",
            summary=f"{company_name} 투자 분석 완료. 추천: {recommendation.value}",
            key_points=[
                f"목표가: {float(price_targets.target_price):,.0f}원",
                f"기대수익률: {float(performance_metrics.expected_return)*100:.1f}%",
                f"리스크 레벨: {risk_level.value}",
                f"신뢰도: {float(confidence_level)*100:.0f}%"
            ],
            confidence_score=confidence_level,
            data={
                "raw_analysis": raw_result,
                "processing_time": processing_time
            }
        )
        analysis_result.add_agent_analysis(advisor_analysis)
        
        return analysis_result
    
    def _create_default_analysis_result(self, symbol: str, company_name: str, current_price: Decimal, error_msg: str) -> StockAnalysisResult:
        """에러 시 기본 분석 결과 생성"""
        return StockAnalysisResult(
            symbol=symbol,
            company_name=company_name,
            current_price=current_price,
            analysis_date=datetime.now(),
            recommendation=RecommendationType.HOLD,
            confidence_level=Decimal('0.1'),
            risk_level=RiskLevel.HIGH,
            price_targets=PriceTarget(
                target_price=current_price,
                entry_price=current_price,
                stop_loss=current_price * Decimal('0.95'),
                time_horizon="medium_term"
            ),
            rationale=InvestmentRationale(
                negative_factors=[f"분석 오류: {error_msg}"],
                risk_factors=["분석 불가로 인한 높은 불확실성"]
            ),
            performance_metrics=PerformanceMetrics(),
            processing_time=0.0
        )
    
    def create_portfolio_optimization_task(self, holdings: List[Dict], target_allocation: Dict) -> Task:
        """포트폴리오 최적화 태스크 생성"""
        return Task(
            description=f"""
            현재 포트폴리오를 분석하고 최적화 방안을 제시하세요.
            
            현재 보유 종목: {holdings}
            목표 자산 배분: {target_allocation}
            
            분석 항목:
            1. 현재 포트폴리오 평가
               - 섹터별/지역별 분산도
               - 리스크-수익률 프로필
               - 상관관계 분석
               
            2. 최적화 방안
               - 리밸런싱 권고
               - 신규 종목 추가/제거 권고
               - 비중 조정 제안
               
            3. 리스크 관리
               - 포트폴리오 VaR 계산
               - 스트레스 테스트
               - 헤지 전략
            """,
            agent=self.agent,
            expected_output="포트폴리오 최적화 권고안"
        )
    
    def update_tools(self, tools: List[Any]):
        """도구 업데이트"""
        self.tools = tools
        self.agent.tools = tools