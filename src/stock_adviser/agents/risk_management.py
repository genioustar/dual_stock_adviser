from crewai import Agent, Task, Crew
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal
import numpy as np

from ..models import RiskMetrics, AgentAnalysis, RiskLevel
from ..utils import app_logger, analysis_logger


class RiskManagementAgent:
    """리스크 관리 전문가"""
    
    def __init__(self, tools: List[Any] = None):
        self.tools = tools or []
        self.agent = self._create_agent()
        
    def _create_agent(self) -> Agent:
        """Agent 생성"""
        return Agent(
            role="Risk Management Specialist",
            goal="포트폴리오와 개별 종목의 리스크를 정확히 평가하고, 효과적인 리스크 관리 전략을 제공한다.",
            backstory="""
            당신은 20년 경력의 리스크 관리 전문가입니다.
            퀀트 분석과 리스크 모델링에 깊은 전문성을 가지고 있으며,
            기관투자자들의 포트폴리오 리스크 관리를 담당해왔습니다.
            
            전문 분야:
            - Value at Risk (VaR) 모델링
            - 베타 계수 및 상관관계 분석
            - 변동성 예측 및 관리
            - 섹터별 리스크 노출도 평가
            - 지정학적/규제 리스크 모니터링
            - 스트레스 테스트 및 시나리오 분석
            
            항상 보수적이고 신중한 관점에서 리스크를 평가하며,
            최악의 시나리오까지 고려한 포괄적인 리스크 분석을 제공합니다.
            
            한국과 미국 시장의 상관관계와 각 시장의 고유 리스크 특성을
            깊이 이해하고 있습니다.
            """,
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            max_iter=3
        )
    
    def create_risk_analysis_task(self, symbol: str, company_name: str, market: str) -> Task:
        """리스크 분석 태스크 생성"""
        return Task(
            description=f"""
            {company_name} ({symbol})에 대한 종합적인 리스크 분석을 수행하세요.
            
            분석 항목:
            1. 시장 리스크 (Market Risk)
               - 베타 계수 계산 및 분석
               - 시장 지수와의 상관관계
               - 시장 변동성에 대한 민감도
               
            2. 개별 리스크 (Idiosyncratic Risk)  
               - 기업 고유 변동성
               - 업종별 리스크 특성
               - 기업 펀더멘털 리스크
               
            3. 변동성 분석
               - 역사적 변동성 패턴
               - 현재 변동성 수준
               - 변동성 예측 모델
               
            4. Value at Risk (VaR) 계산
               - 95% 신뢰구간 VaR
               - 99% 신뢰구간 VaR
               - Expected Shortfall (ES)
               
            5. 유동성 리스크
               - 평균 거래량 분석
               - 거래 비용 추정
               - 유동성 위기 시나리오
               
            6. 지정학적/규제 리스크
               - 정책 변화 리스크
               - 규제 환경 변화
               - 무역 분쟁 영향
               
            7. ESG 리스크
               - 환경 리스크
               - 사회적 리스크
               - 지배구조 리스크
               
            Market: {market}
            분석 기준일: {datetime.now().strftime('%Y-%m-%d')}
            """,
            agent=self.agent,
            expected_output="""
            리스크 분석 결과를 다음 JSON 형태로 제공:
            {
                "overall_risk_level": "low/medium/high/very_high",
                "risk_score": 0.0 ~ 1.0,
                "var_95": VaR 값 (95% 신뢰구간),
                "var_99": VaR 값 (99% 신뢰구간),
                "beta": 베타 계수,
                "volatility": 연환산 변동성,
                "correlation_analysis": {
                    "market_correlation": 시장 상관관계,
                    "sector_correlation": 섹터 상관관계
                },
                "liquidity_metrics": {
                    "avg_volume": 평균 거래량,
                    "bid_ask_spread": 호가 스프레드,
                    "liquidity_risk": "low/medium/high"
                },
                "fundamental_risks": ["리스크1", "리스크2", ...],
                "regulatory_risks": ["규제 리스크1", "규제 리스크2", ...],
                "esg_risks": ["ESG 리스크1", "ESG 리스크2", ...],
                "risk_mitigation": ["완화 방안1", "완화 방안2", ...],
                "stress_scenarios": {
                    "market_crash": "시장 급락 시나리오 영향",
                    "sector_crisis": "섹터 위기 시나리오 영향",
                    "company_crisis": "기업 위기 시나리오 영향"
                }
            }
            """
        )
    
    def analyze_risk(self, symbol: str, company_name: str, market: str, price_data: Optional[List] = None) -> AgentAnalysis:
        """리스크 분석 실행"""
        analysis_logger.log_analysis_start(symbol, "risk_management")
        start_time = datetime.now()
        
        try:
            # 리스크 메트릭스 계산
            risk_metrics = self.calculate_risk_metrics(symbol, market, price_data)
            
            # 태스크 생성
            risk_task = self.create_risk_analysis_task(symbol, company_name, market)
            
            # Crew 생성 및 실행
            crew = Crew(
                agents=[self.agent],
                tasks=[risk_task],
                verbose=True
            )
            
            # 분석 실행
            result = crew.kickoff()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 리스크 레벨 결정
            risk_level = self._determine_risk_level(risk_metrics)
            
            # AgentAnalysis 객체 생성
            agent_analysis = AgentAnalysis(
                agent_name="Risk Management Specialist",
                analysis_type="risk",
                summary=f"{company_name}의 리스크 분석을 완료했습니다. 위험도: {risk_level.value}",
                key_points=[
                    f"VaR(95%): {float(risk_metrics.var_95):.2%}" if risk_metrics.var_95 else "VaR 계산 불가",
                    f"베타 계수: {float(risk_metrics.beta):.2f}" if risk_metrics.beta else "베타 계산 불가",
                    f"변동성: {float(risk_metrics.volatility):.2%}" if risk_metrics.volatility else "변동성 계산 불가",
                    f"리스크 레벨: {risk_level.value}"
                ],
                confidence_score=Decimal('0.85'),
                data={
                    "raw_analysis": str(result),
                    "risk_metrics": risk_metrics.to_dict(),
                    "risk_level": risk_level.value,
                    "processing_time": processing_time
                }
            )
            
            analysis_logger.log_analysis_complete(symbol, agent_analysis.to_dict(), processing_time)
            analysis_logger.log_agent_execution("Risk Management Specialist", symbol, processing_time, True)
            
            return agent_analysis
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            analysis_logger.log_analysis_error(symbol, e)
            analysis_logger.log_agent_execution("Risk Management Specialist", symbol, processing_time, False)
            
            # 에러 시에도 기본 분석 결과 반환
            return AgentAnalysis(
                agent_name="Risk Management Specialist",
                analysis_type="risk",
                summary=f"리스크 분석 중 오류가 발생했습니다: {str(e)}",
                key_points=["분석 실패"],
                confidence_score=Decimal('0.1'),
                data={"error": str(e), "processing_time": processing_time}
            )
    
    def calculate_risk_metrics(self, symbol: str, market: str, price_data: Optional[List] = None) -> RiskMetrics:
        """리스크 메트릭스 계산"""
        try:
            # 실제 구현에서는 가격 데이터를 사용하여 계산
            # 현재는 더미 데이터로 구현
            
            if price_data and len(price_data) > 1:
                # 수익률 계산
                returns = []
                for i in range(1, len(price_data)):
                    if price_data[i-1] != 0:
                        ret = (price_data[i] - price_data[i-1]) / price_data[i-1]
                        returns.append(ret)
                
                if returns:
                    returns_array = np.array(returns)
                    
                    # 변동성 계산 (연환산)
                    volatility = np.std(returns_array) * np.sqrt(252)
                    
                    # VaR 계산 (정규분포 가정)
                    var_95 = -np.percentile(returns_array, 5)
                    var_99 = -np.percentile(returns_array, 1)
                    
                    # 베타 계산 (더미 - 실제로는 시장 지수 데이터 필요)
                    beta = 1.2 if market == 'US' else 0.9
                    
                else:
                    # 기본값
                    volatility = 0.3
                    var_95 = 0.05
                    var_99 = 0.08
                    beta = 1.0
            else:
                # 기본값 (더미 데이터)
                volatility = 0.25 if market == 'KR' else 0.30
                var_95 = 0.04 if market == 'KR' else 0.05
                var_99 = 0.07 if market == 'KR' else 0.08
                beta = 0.9 if market == 'KR' else 1.1
            
            return RiskMetrics(
                symbol=symbol,
                var_95=Decimal(str(var_95)),
                var_99=Decimal(str(var_99)),
                beta=Decimal(str(beta)),
                volatility=Decimal(str(volatility)),
                sharpe_ratio=Decimal('0.8'),  # 더미
                max_drawdown=Decimal('0.15'),  # 더미
                correlation_spy=Decimal('0.6') if market == 'US' else Decimal('0.3'),
                correlation_kospi=Decimal('0.7') if market == 'KR' else Decimal('0.2')
            )
            
        except Exception as e:
            app_logger.error(f"리스크 메트릭스 계산 실패: {symbol}, 오류: {str(e)}")
            
            # 기본값 반환
            return RiskMetrics(
                symbol=symbol,
                var_95=Decimal('0.05'),
                var_99=Decimal('0.08'),
                beta=Decimal('1.0'),
                volatility=Decimal('0.25'),
                correlation_spy=Decimal('0.5'),
                correlation_kospi=Decimal('0.5')
            )
    
    def _determine_risk_level(self, risk_metrics: RiskMetrics) -> RiskLevel:
        """리스크 레벨 결정"""
        try:
            # VaR과 변동성을 기준으로 리스크 레벨 결정
            var_95 = float(risk_metrics.var_95) if risk_metrics.var_95 else 0.05
            volatility = float(risk_metrics.volatility) if risk_metrics.volatility else 0.25
            
            # 리스크 점수 계산 (0~1)
            risk_score = (var_95 * 0.6) + (volatility * 0.4)
            
            if risk_score < 0.15:
                return RiskLevel.LOW
            elif risk_score < 0.25:
                return RiskLevel.MEDIUM  
            elif risk_score < 0.40:
                return RiskLevel.HIGH
            else:
                return RiskLevel.VERY_HIGH
                
        except Exception as e:
            app_logger.error(f"리스크 레벨 결정 실패: {str(e)}")
            return RiskLevel.MEDIUM
    
    def calculate_portfolio_risk(self, holdings: List[Dict], correlations: Dict) -> Dict[str, float]:
        """포트폴리오 리스크 계산"""
        try:
            # 실제 구현에서는 Modern Portfolio Theory 사용
            # 현재는 단순화된 계산
            
            total_risk = 0.0
            total_weight = sum(holding.get('weight', 0) for holding in holdings)
            
            for holding in holdings:
                weight = holding.get('weight', 0) / total_weight if total_weight > 0 else 0
                individual_risk = holding.get('volatility', 0.25)
                total_risk += (weight ** 2) * (individual_risk ** 2)
            
            # 분산 효과 고려 (단순화)
            diversification_benefit = 0.1  # 10% 리스크 감소
            portfolio_volatility = np.sqrt(total_risk) * (1 - diversification_benefit)
            
            return {
                'portfolio_volatility': portfolio_volatility,
                'var_95': portfolio_volatility * 1.65,  # 95% VaR 근사
                'var_99': portfolio_volatility * 2.33,  # 99% VaR 근사
                'diversification_ratio': diversification_benefit
            }
            
        except Exception as e:
            app_logger.error(f"포트폴리오 리스크 계산 실패: {str(e)}")
            return {
                'portfolio_volatility': 0.20,
                'var_95': 0.033,
                'var_99': 0.047,
                'diversification_ratio': 0.1
            }
    
    def update_tools(self, tools: List[Any]):
        """도구 업데이트"""
        self.tools = tools
        self.agent.tools = tools