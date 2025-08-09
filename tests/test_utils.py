import pytest
import os
from unittest.mock import patch

from src.stock_adviser.utils import (
    settings, get_settings, validate_api_keys,
    get_market_config, APIEndpoints
)


class TestConfig:
    """설정 관련 테스트"""
    
    def test_get_settings(self):
        """설정 조회 테스트"""
        config = get_settings()
        
        assert config is not None
        assert hasattr(config, 'environment')
        assert hasattr(config, 'log_level')
        assert hasattr(config, 'database_url')
    
    def test_market_config_kr(self):
        """한국 시장 설정 테스트"""
        kr_config = get_market_config('KR')
        
        assert kr_config['currency'] == 'KRW'
        assert kr_config['timezone'] == 'Asia/Seoul'
        assert 'kospi' in kr_config['market_indices']
        assert 'kosdaq' in kr_config['market_indices']
    
    def test_market_config_us(self):
        """미국 시장 설정 테스트"""
        us_config = get_market_config('US')
        
        assert us_config['currency'] == 'USD'
        assert us_config['timezone'] == 'America/New_York'
        assert 'sp500' in us_config['market_indices']
        assert 'nasdaq' in us_config['market_indices']
    
    def test_market_config_invalid(self):
        """잘못된 시장 코드 테스트"""
        with pytest.raises(ValueError):
            get_market_config('INVALID')
    
    def test_yfinance_symbol_conversion(self):
        """yfinance 심볼 변환 테스트"""
        # 한국 종목
        kr_symbol = APIEndpoints.get_yfinance_symbol('005930', 'KR')
        assert kr_symbol == '005930.KS'
        
        # 이미 접미사가 있는 경우
        kr_symbol_with_suffix = APIEndpoints.get_yfinance_symbol('005930.KS', 'KR')
        assert kr_symbol_with_suffix == '005930.KS'
        
        # 미국 종목
        us_symbol = APIEndpoints.get_yfinance_symbol('AAPL', 'US')
        assert us_symbol == 'AAPL'
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_validate_api_keys_with_key(self):
        """API 키 검증 테스트 (키 있음)"""
        # 환경변수 설정 후 설정 재로드
        from src.stock_adviser.utils.config import Settings
        test_settings = Settings()
        
        with patch('src.stock_adviser.utils.config.settings', test_settings):
            status = validate_api_keys()
            
        assert 'openai' in status
        assert status['openai']['status'] == 'configured'
        assert status['openai']['required'] is True
    
    def test_validate_api_keys_without_key(self):
        """API 키 검증 테스트 (키 없음)"""
        with patch.object(settings, 'openai_api_key', None):
            status = validate_api_keys()
            
        assert 'openai' in status
        assert status['openai']['status'] == 'missing'
        assert status['openai']['required'] is True


class TestLogger:
    """로거 관련 테스트"""
    
    def test_logger_creation(self):
        """로거 생성 테스트"""
        from src.stock_adviser.utils import setup_logger, get_logger
        
        # 새로운 로거 생성
        logger = setup_logger('test_logger', console_output=True, file_output=False)
        
        assert logger is not None
        assert logger.name == 'test_logger'
        
        # 기존 로거 조회
        same_logger = get_logger('test_logger')
        assert same_logger == logger
    
    def test_analysis_logger(self):
        """분석 로거 테스트"""
        from src.stock_adviser.utils import StockAnalysisLogger
        
        analysis_logger = StockAnalysisLogger('test_analysis')
        
        assert analysis_logger is not None
        assert analysis_logger.logger is not None
        
        # 로그 메서드 테스트 (실제 로그는 생성되지 않음)
        try:
            analysis_logger.log_analysis_start('TEST', 'test_analysis')
            analysis_logger.log_data_fetch('TEST', 'test_source', True)
            analysis_logger.log_agent_execution('Test Agent', 'TEST', 1.0, True)
        except Exception as e:
            pytest.fail(f"Analysis logger methods failed: {str(e)}")
    
    def test_performance_logger(self):
        """성능 로거 테스트"""
        from src.stock_adviser.utils import PerformanceLogger
        
        perf_logger = PerformanceLogger('test_performance')
        
        assert perf_logger is not None
        assert perf_logger.logger is not None
        
        # 로그 메서드 테스트
        try:
            perf_logger.log_api_call('/test', 0.5, 200, 'TEST')
            perf_logger.log_processing_time('test_operation', 1.0, 'TEST')
        except Exception as e:
            pytest.fail(f"Performance logger methods failed: {str(e)}")


if __name__ == '__main__':
    pytest.main([__file__])