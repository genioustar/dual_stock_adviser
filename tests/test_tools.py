import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from decimal import Decimal

from src.stock_adviser.tools import SentimentAnalyzer, DataCollector


class TestSentimentAnalyzer:
    """감성 분석 도구 테스트"""
    
    def setup_method(self):
        """테스트 준비"""
        self.analyzer = SentimentAnalyzer()
    
    def test_sentiment_analyzer_creation(self):
        """감성 분석기 생성 테스트"""
        assert self.analyzer is not None
    
    def test_analyze_text_sentiment(self):
        """텍스트 감성 분석 테스트"""
        # 긍정적 텍스트
        positive_text = "주가가 상승하고 수익이 증가했습니다"
        positive_score = self.analyzer._analyze_text_sentiment(positive_text)
        assert isinstance(positive_score, float)
        assert -1.0 <= positive_score <= 1.0
        
        # 부정적 텍스트  
        negative_text = "주가가 하락하고 손실이 발생했습니다"
        negative_score = self.analyzer._analyze_text_sentiment(negative_text)
        assert isinstance(negative_score, float)
        assert -1.0 <= negative_score <= 1.0
    
    def test_preprocess_text(self):
        """텍스트 전처리 테스트"""
        raw_text = "<p>주가가   상승했습니다!</p>"
        processed = self.analyzer._preprocess_text(raw_text)
        
        assert '<p>' not in processed
        assert '</p>' not in processed
        assert '  ' not in processed  # 다중 공백 제거
    
    def test_financial_keywords_weight(self):
        """금융 키워드 가중치 테스트"""
        base_sentiment = 0.0
        
        # 긍정 키워드가 많은 텍스트
        positive_text = "성장 수익 증가 호조"
        weighted_positive = self.analyzer._apply_financial_keywords_weight(
            positive_text, base_sentiment
        )
        assert weighted_positive >= base_sentiment
        
        # 부정 키워드가 많은 텍스트
        negative_text = "하락 손실 위험 급락"
        weighted_negative = self.analyzer._apply_financial_keywords_weight(
            negative_text, base_sentiment  
        )
        assert weighted_negative <= base_sentiment
    
    def test_analyze_news_sentiment_empty(self):
        """빈 뉴스 데이터 감성 분석 테스트"""
        result = self.analyzer.analyze_news_sentiment([])
        
        assert result['overall_sentiment'] == 0.0
        assert result['overall_category'] == 'neutral'
        assert result['confidence'] == 0.1
        assert result['news_count'] == 0
    
    def test_analyze_news_sentiment_with_data(self):
        """뉴스 데이터 감성 분석 테스트"""
        news_data = [
            {
                'title': '삼성전자 실적 호조',
                'description': '수익이 크게 증가했습니다',
                'url': 'http://example.com/1'
            },
            {
                'title': '주가 하락 우려',
                'description': '시장 상황이 좋지 않습니다', 
                'url': 'http://example.com/2'
            }
        ]
        
        result = self.analyzer.analyze_news_sentiment(news_data)
        
        assert 'overall_sentiment' in result
        assert 'overall_category' in result
        assert 'confidence' in result
        assert result['news_count'] == 2
        assert len(result['analyzed_news']) == 2
        
        # 분포 확인
        distribution = result['sentiment_distribution']
        assert 'positive' in distribution
        assert 'negative' in distribution
        assert 'neutral' in distribution
    
    def test_get_sentiment_summary(self):
        """감성 분석 요약 테스트"""
        news_sentiment = {
            'overall_sentiment': 0.3,
            'overall_category': 'positive',
            'confidence': 0.7
        }
        
        summary = self.analyzer.get_sentiment_summary('TEST', news_sentiment)
        
        assert summary['symbol'] == 'TEST'
        assert isinstance(summary['sentiment_score'], Decimal)
        assert summary['sentiment_category'] == 'positive'
        assert isinstance(summary['confidence'], Decimal)


class TestDataCollector:
    """데이터 수집 도구 테스트"""
    
    def setup_method(self):
        """테스트 준비"""
        self.collector = DataCollector()
    
    def test_data_collector_creation(self):
        """데이터 수집기 생성 테스트"""
        assert self.collector is not None
        assert hasattr(self.collector, 'session')
    
    def test_rsi_calculation(self):
        """RSI 계산 테스트"""
        # 테스트 가격 데이터
        prices = [100, 102, 101, 103, 102, 104, 103, 105, 104, 106, 105, 107, 106, 108, 107]
        
        rsi = self.collector._calculate_rsi(prices, 14)
        
        assert rsi is not None
        assert 0 <= rsi <= 100
    
    def test_rsi_calculation_insufficient_data(self):
        """RSI 계산 - 데이터 부족 테스트"""
        prices = [100, 102, 101]  # 14개 미만
        
        rsi = self.collector._calculate_rsi(prices, 14)
        
        assert rsi is None
    
    def test_bollinger_bands_calculation(self):
        """볼린저 밴드 계산 테스트"""
        prices = [100, 102, 101, 103, 102, 104, 103, 105, 104, 106, 
                 105, 107, 106, 108, 107, 109, 108, 110, 109, 111]
        
        upper, middle, lower = self.collector._calculate_bollinger_bands(prices, 20, 2)
        
        assert upper is not None
        assert middle is not None  
        assert lower is not None
        assert upper > middle > lower
    
    def test_macd_calculation(self):
        """MACD 계산 테스트"""
        prices = list(range(100, 130))  # 30개 가격 데이터
        
        macd, signal, histogram = self.collector._calculate_macd(prices, 12, 26, 9)
        
        assert macd is not None
        assert signal is not None
        assert histogram is not None
    
    @pytest.mark.asyncio
    async def test_get_company_info_mock(self):
        """기업 정보 수집 테스트 (Mock)"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock 데이터 설정
            mock_info = {
                'longName': '삼성전자',
                'sector': 'Technology',
                'industry': 'Consumer Electronics'
            }
            mock_ticker.return_value.info = mock_info
            
            result = await self.collector.get_company_info('005930', 'KR')
            
            assert result is not None
            assert result.name == '삼성전자'
            assert result.sector == 'Technology'
            assert result.market == 'KR'
    
    @pytest.mark.asyncio  
    async def test_get_financial_metrics_mock(self):
        """재무 지표 수집 테스트 (Mock)"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_info = {
                'trailingPE': 15.5,
                'priceToBook': 1.2,
                'returnOnEquity': 0.15,
                'marketCap': 1000000000
            }
            mock_ticker.return_value.info = mock_info
            
            result = await self.collector.get_financial_metrics('005930', 'KR')
            
            assert result is not None
            assert result.pe_ratio == Decimal('15.5')
            assert result.pb_ratio == Decimal('1.2')
            assert result.roe == Decimal('0.15')
    
    def test_calculate_technical_indicators_insufficient_data(self):
        """기술적 지표 계산 - 데이터 부족 테스트"""
        from src.stock_adviser.models import StockPrice
        from datetime import datetime
        
        # 10개만 제공 (20개 미만)
        price_data = []
        for i in range(10):
            price = StockPrice(
                open=Decimal('100'), high=Decimal('105'), 
                low=Decimal('95'), close=Decimal(str(100 + i)),
                volume=1000, timestamp=datetime.now()
            )
            price_data.append(price)
        
        indicators = self.collector.calculate_technical_indicators(price_data)
        
        # 데이터 부족으로 대부분 None이어야 함
        assert indicators.rsi is None
        assert indicators.sma_20 is None


if __name__ == '__main__':
    pytest.main([__file__])