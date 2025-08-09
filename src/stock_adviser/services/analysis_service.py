import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

from ..agents import MarketSentimentAgent, RiskManagementAgent, InvestmentAdvisorAgent
from ..tools import DataCollector, SentimentAnalyzer
from ..models import StockAnalysisResult, MarketSentiment, RiskMetrics
from ..utils import app_logger, analysis_logger, performance_logger


class StockAnalysisService:
    """주식 분석 서비스"""
    
    def __init__(self):
        # 컴포넌트 초기화
        self.data_collector = DataCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Agent 초기화
        self.market_sentiment_agent = MarketSentimentAgent()
        self.risk_management_agent = RiskManagementAgent()
        self.investment_advisor_agent = InvestmentAdvisorAgent()
        
        app_logger.info("Stock Analysis Service 초기화 완료")
    
    async def analyze_stock(
        self, 
        symbol: str, 
        market: str = "KR", 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Optional[StockAnalysisResult]:
        """종합 주식 분석"""
        try:
            app_logger.info(f"주식 종합 분석 시작: {symbol} ({market})")
            analysis_logger.log_analysis_start(symbol, "comprehensive")
            start_time = datetime.now()
            
            # 1. 기본 데이터 수집
            stock_data = await self.data_collector.get_stock_data(symbol, market)
            if not stock_data:
                app_logger.error(f"주식 데이터 수집 실패: {symbol}")
                return None
            
            company_name = stock_data.info.name
            current_price = stock_data.current_price.close
            
            app_logger.info(f"기본 데이터 수집 완료: {company_name} ({symbol})")
            
            # 2. 병렬로 전문가 분석 실행
            analysis_tasks = [
                self._run_sentiment_analysis(symbol, company_name, market, stock_data.news_data),
                self._run_risk_analysis(symbol, company_name, market, stock_data.price_history),
            ]
            
            sentiment_analysis, risk_analysis = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # 예외 처리
            if isinstance(sentiment_analysis, Exception):
                app_logger.error(f"시장 심리 분석 실패: {str(sentiment_analysis)}")
                sentiment_analysis = None
                
            if isinstance(risk_analysis, Exception):
                app_logger.error(f"리스크 분석 실패: {str(risk_analysis)}")
                risk_analysis = None
            
            # 3. 투자 자문 분석 (다른 분석 결과 통합)
            investment_result = await self._run_investment_analysis(
                symbol, company_name, current_price, market,
                sentiment_analysis, risk_analysis, user_profile
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            performance_logger.log_processing_time("comprehensive_analysis", processing_time, symbol)
            
            app_logger.info(
                f"종합 분석 완료: {symbol}, "
                f"추천: {investment_result.recommendation.value}, "
                f"처리시간: {processing_time:.2f}초"
            )
            
            analysis_logger.log_analysis_complete(symbol, investment_result.to_dict(), processing_time)
            
            return investment_result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            app_logger.error(f"종합 분석 실패: {symbol}, 오류: {str(e)}")
            analysis_logger.log_analysis_error(symbol, e)
            return None
    
    async def _run_sentiment_analysis(
        self, 
        symbol: str, 
        company_name: str, 
        market: str, 
        news_data: Optional[List[Dict]] = None
    ):
        """시장 심리 분석 실행"""
        try:
            # 뉴스 감성 분석
            if news_data:
                news_sentiment = self.sentiment_analyzer.analyze_news_sentiment(news_data)
            else:
                news_sentiment = self.sentiment_analyzer._get_default_sentiment_result()
            
            # 감성 분석 종합
            sentiment_summary = self.sentiment_analyzer.get_sentiment_summary(
                symbol, news_sentiment
            )
            
            # Agent 분석 실행
            sentiment_analysis = self.market_sentiment_agent.analyze_sentiment(
                symbol, company_name, market
            )
            
            # 분석 데이터에 감성 분석 결과 추가
            sentiment_analysis.data.update({
                'sentiment_summary': sentiment_summary,
                'news_sentiment': news_sentiment
            })
            
            return sentiment_analysis
            
        except Exception as e:
            app_logger.error(f"시장 심리 분석 실패: {symbol}, 오류: {str(e)}")
            raise e
    
    async def _run_risk_analysis(
        self, 
        symbol: str, 
        company_name: str, 
        market: str, 
        price_history: Optional[List] = None
    ):
        """리스크 분석 실행"""
        try:
            # 가격 데이터 변환
            price_data = None
            if price_history:
                price_data = [float(price.close) for price in price_history]
            
            # Agent 분석 실행
            risk_analysis = self.risk_management_agent.analyze_risk(
                symbol, company_name, market, price_data
            )
            
            return risk_analysis
            
        except Exception as e:
            app_logger.error(f"리스크 분석 실패: {symbol}, 오류: {str(e)}")
            raise e
    
    async def _run_investment_analysis(
        self,
        symbol: str,
        company_name: str, 
        current_price: Decimal,
        market: str,
        sentiment_analysis,
        risk_analysis,
        user_profile: Optional[Dict] = None
    ) -> StockAnalysisResult:
        """투자 자문 분석 실행"""
        try:
            # Investment Advisor Agent 실행
            investment_result = self.investment_advisor_agent.analyze_investment(
                symbol, company_name, current_price, market,
                sentiment_analysis, risk_analysis, user_profile
            )
            
            return investment_result
            
        except Exception as e:
            app_logger.error(f"투자 자문 분석 실패: {symbol}, 오류: {str(e)}")
            # 기본 결과 반환
            return self.investment_advisor_agent._create_default_analysis_result(
                symbol, company_name, current_price, str(e)
            )
    
    def get_market_sentiment_score(self, symbol: str, market: str) -> MarketSentiment:
        """시장 심리 점수 조회"""
        try:
            return self.market_sentiment_agent.get_market_sentiment_score(symbol, market)
        except Exception as e:
            app_logger.error(f"시장 심리 점수 조회 실패: {symbol}, 오류: {str(e)}")
            return MarketSentiment(
                symbol=symbol,
                sentiment_score=Decimal('0.0'),
                sentiment_category='neutral',
                news_sentiment=Decimal('0.0'),
                confidence=Decimal('0.1')
            )
    
    def calculate_risk_metrics(self, symbol: str, market: str, price_data: Optional[List] = None) -> RiskMetrics:
        """리스크 지표 계산"""
        try:
            return self.risk_management_agent.calculate_risk_metrics(symbol, market, price_data)
        except Exception as e:
            app_logger.error(f"리스크 지표 계산 실패: {symbol}, 오류: {str(e)}")
            return RiskMetrics(symbol=symbol)
    
    async def analyze_portfolio(
        self, 
        holdings: List[Dict[str, Any]], 
        target_allocation: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """포트폴리오 분석 (향후 구현)"""
        try:
            app_logger.info(f"포트폴리오 분석 시작: {len(holdings)}개 종목")
            
            # 개별 종목 분석
            analysis_tasks = []
            for holding in holdings:
                symbol = holding.get('symbol')
                market = holding.get('market', 'KR')
                if symbol:
                    task = self.analyze_stock(symbol, market)
                    analysis_tasks.append(task)
            
            if analysis_tasks:
                results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                
                # 성공한 분석만 필터링
                successful_analyses = [
                    result for result in results 
                    if not isinstance(result, Exception) and result is not None
                ]
                
                app_logger.info(f"포트폴리오 분석 완료: {len(successful_analyses)}/{len(holdings)} 성공")
                
                return {
                    'total_holdings': len(holdings),
                    'analyzed_count': len(successful_analyses),
                    'analyses': [analysis.to_dict() for analysis in successful_analyses],
                    'portfolio_summary': self._calculate_portfolio_summary(successful_analyses),
                    'analysis_timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'total_holdings': 0,
                    'analyzed_count': 0,
                    'analyses': [],
                    'error': 'No valid holdings to analyze'
                }
                
        except Exception as e:
            app_logger.error(f"포트폴리오 분석 실패: {str(e)}")
            return {
                'error': f'Portfolio analysis failed: {str(e)}',
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _calculate_portfolio_summary(self, analyses: List[StockAnalysisResult]) -> Dict[str, Any]:
        """포트폴리오 요약 계산"""
        try:
            if not analyses:
                return {}
            
            # 추천 분포
            recommendations = {}
            total_confidence = 0
            risk_levels = {}
            
            for analysis in analyses:
                # 추천 분포
                rec = analysis.recommendation.value
                recommendations[rec] = recommendations.get(rec, 0) + 1
                
                # 신뢰도 평균
                total_confidence += float(analysis.confidence_level)
                
                # 리스크 분포
                risk = analysis.risk_level.value
                risk_levels[risk] = risk_levels.get(risk, 0) + 1
            
            avg_confidence = total_confidence / len(analyses)
            
            return {
                'total_stocks': len(analyses),
                'recommendation_distribution': recommendations,
                'risk_distribution': risk_levels,
                'average_confidence': round(avg_confidence, 2),
                'summary': f"{len(analyses)}개 종목 분석 완료"
            }
            
        except Exception as e:
            app_logger.error(f"포트폴리오 요약 계산 실패: {str(e)}")
            return {'error': 'Summary calculation failed'}


class DualStockAdviser:
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        self.analysis_service = StockAnalysisService()
        app_logger.info("Dual Stock Adviser 초기화 완료")
    
    async def analyze_stock(
        self, 
        symbol: str, 
        market: str = "KR", 
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Optional[StockAnalysisResult]:
        """주식 분석"""
        return await self.analysis_service.analyze_stock(symbol, market, user_profile)
    
    async def analyze_portfolio(
        self, 
        holdings: List[Dict[str, Any]], 
        target_allocation: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """포트폴리오 분석"""
        return await self.analysis_service.analyze_portfolio(holdings, target_allocation)
    
    def get_market_sentiment(self, symbol: str, market: str = "KR") -> MarketSentiment:
        """시장 심리 조회"""
        return self.analysis_service.get_market_sentiment_score(symbol, market)
    
    def get_risk_metrics(self, symbol: str, market: str = "KR", price_data: Optional[List] = None) -> RiskMetrics:
        """리스크 지표 조회"""
        return self.analysis_service.calculate_risk_metrics(symbol, market, price_data)