import pytest
from decimal import Decimal
from datetime import datetime

from src.stock_adviser.models import (
    StockPrice, StockInfo, FinancialMetrics, TechnicalIndicators,
    StockData, MarketSentiment, RiskMetrics,
    RecommendationType, RiskLevel, AgentAnalysis,
    PriceTarget, StockAnalysisResult
)


class TestStockModels:
    """주식 데이터 모델 테스트"""
    
    def test_stock_price_creation(self):
        """StockPrice 생성 테스트"""
        price = StockPrice(
            open=Decimal('100000'),
            high=Decimal('105000'),
            low=Decimal('98000'),
            close=Decimal('103000'),
            volume=1000000,
            timestamp=datetime.now()
        )
        
        assert price.close == Decimal('103000')
        assert price.volume == 1000000
        
        # to_dict 테스트
        price_dict = price.to_dict()
        assert price_dict['close'] == 103000.0
        assert isinstance(price_dict['timestamp'], str)
    
    def test_stock_info_creation(self):
        """StockInfo 생성 테스트"""
        info = StockInfo(
            symbol='005930',
            name='삼성전자',
            market='KR',
            sector='Technology',
            industry='Consumer Electronics',
            currency='KRW'
        )
        
        assert info.symbol == '005930'
        assert info.name == '삼성전자'
        assert info.market == 'KR'
        
        # to_dict 테스트
        info_dict = info.to_dict()
        assert info_dict['symbol'] == '005930'
        assert info_dict['currency'] == 'KRW'
    
    def test_market_sentiment_creation(self):
        """MarketSentiment 생성 테스트"""
        sentiment = MarketSentiment(
            symbol='005930',
            sentiment_score=Decimal('0.5'),
            sentiment_category='positive',
            news_sentiment=Decimal('0.6'),
            confidence=Decimal('0.8')
        )
        
        assert sentiment.sentiment_score == Decimal('0.5')
        assert sentiment.sentiment_category == 'positive'
        assert sentiment.analysis_date is not None
        
        # to_dict 테스트
        sentiment_dict = sentiment.to_dict()
        assert sentiment_dict['sentiment_score'] == 0.5
        assert sentiment_dict['sentiment_category'] == 'positive'


class TestAnalysisModels:
    """분석 결과 모델 테스트"""
    
    def test_agent_analysis_creation(self):
        """AgentAnalysis 생성 테스트"""
        analysis = AgentAnalysis(
            agent_name="Test Agent",
            analysis_type="test",
            summary="Test analysis",
            key_points=["Point 1", "Point 2"],
            confidence_score=Decimal('0.8')
        )
        
        assert analysis.agent_name == "Test Agent"
        assert len(analysis.key_points) == 2
        assert analysis.confidence_score == Decimal('0.8')
        assert analysis.created_at is not None
    
    def test_price_target_creation(self):
        """PriceTarget 생성 테스트"""
        target = PriceTarget(
            target_price=Decimal('120000'),
            entry_price=Decimal('100000'),
            stop_loss=Decimal('90000'),
            take_profit=Decimal('120000'),
            time_horizon="medium_term"
        )
        
        assert target.target_price == Decimal('120000')
        assert target.time_horizon == "medium_term"
        
        # to_dict 테스트
        target_dict = target.to_dict()
        assert target_dict['target_price'] == 120000.0
    
    def test_stock_analysis_result_creation(self):
        """StockAnalysisResult 생성 테스트"""
        price_target = PriceTarget(
            target_price=Decimal('120000'),
            time_horizon="medium_term"
        )
        
        result = StockAnalysisResult(
            symbol='005930',
            company_name='삼성전자',
            current_price=Decimal('100000'),
            analysis_date=datetime.now(),
            recommendation=RecommendationType.BUY,
            confidence_level=Decimal('0.8'),
            risk_level=RiskLevel.MEDIUM,
            price_targets=price_target
        )
        
        assert result.symbol == '005930'
        assert result.recommendation == RecommendationType.BUY
        assert result.risk_level == RiskLevel.MEDIUM
        assert len(result.agent_analyses) == 0
        
        # 요약 생성 테스트
        summary = result.generate_summary()
        assert '삼성전자' in summary
        assert 'BUY' in summary