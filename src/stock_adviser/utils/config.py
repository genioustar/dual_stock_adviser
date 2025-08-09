import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API Keys - AI Providers
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key for CrewAI")
    google_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-1.5-pro", description="Gemini model to use")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic Claude API key")
    
    # Other APIs
    serper_api_key: Optional[str] = Field(default=None, description="Serper API key for web search")
    news_api_key: Optional[str] = Field(default=None, description="News API key")
    alpha_vantage_api_key: Optional[str] = Field(default=None, description="Alpha Vantage API key")
    financial_modeling_prep_api_key: Optional[str] = Field(default=None, description="Financial Modeling Prep API key")
    
    # Database
    database_url: str = Field(default="sqlite:///stock_adviser.db", description="Database URL")
    
    # Application Settings
    environment: str = Field(default="development", description="Environment (development, test, production)")
    log_level: str = Field(default="INFO", description="Log level")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Configuration
    api_rate_limit: int = Field(default=100, description="API rate limit per minute")
    api_timeout: int = Field(default=30, description="API timeout in seconds")
    api_retry_attempts: int = Field(default=3, description="Number of API retry attempts")
    api_backoff_factor: float = Field(default=2.0, description="Backoff factor for retries")
    
    # Data Sources
    data_provider_primary: str = Field(default="yfinance", description="Primary data provider")
    data_provider_fallback: str = Field(default="alpha_vantage", description="Fallback data provider")
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    
    # Analysis Settings
    sentiment_threshold: float = Field(default=0.6, description="Sentiment analysis threshold")
    risk_calculation_method: str = Field(default="var", description="Risk calculation method")
    confidence_interval: float = Field(default=0.95, description="Statistical confidence interval")
    
    # CrewAI Settings
    crewai_verbose: bool = Field(default=True, description="CrewAI verbose mode")
    crewai_memory: bool = Field(default=True, description="CrewAI memory enabled")
    crewai_max_iter: int = Field(default=5, description="CrewAI max iterations")
    
    # Security
    jwt_secret_key: Optional[str] = Field(default=None, description="JWT secret key")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    
    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent)
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / "logs")
    config_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / "config")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 디렉토리 생성
        self.logs_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

# 글로벌 설정 인스턴스
settings = Settings()

def get_settings() -> Settings:
    """설정 인스턴스 반환"""
    return settings

def update_settings(**kwargs) -> Settings:
    """설정 업데이트"""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    return settings

class MarketConfig:
    """시장별 설정"""
    
    KOREAN_MARKET = {
        'symbol_suffix': '.KS',  # KOSPI
        'symbol_suffix_kosdaq': '.KQ',  # KOSDAQ
        'currency': 'KRW',
        'timezone': 'Asia/Seoul',
        'trading_hours': {
            'open': '09:00',
            'close': '15:30'
        },
        'market_indices': {
            'kospi': '^KS11',
            'kosdaq': '^KQ11'
        }
    }
    
    US_MARKET = {
        'currency': 'USD',
        'timezone': 'America/New_York',
        'trading_hours': {
            'open': '09:30',
            'close': '16:00'
        },
        'market_indices': {
            'sp500': '^GSPC',
            'nasdaq': '^IXIC',
            'dow': '^DJI'
        }
    }

class APIEndpoints:
    """API 엔드포인트 설정"""
    
    ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
    NEWS_API_BASE = "https://newsapi.org/v2"
    SERPER_API_BASE = "https://google.serper.dev"
    
    @staticmethod
    def get_yfinance_symbol(symbol: str, market: str) -> str:
        """yfinance용 심볼 변환"""
        if market.upper() == 'KR':
            if not symbol.endswith('.KS') and not symbol.endswith('.KQ'):
                # 기본적으로 KOSPI로 설정
                return f"{symbol}.KS"
        return symbol

def get_market_config(market: str) -> dict:
    """시장별 설정 반환"""
    market = market.upper()
    if market == 'KR':
        return MarketConfig.KOREAN_MARKET
    elif market == 'US':
        return MarketConfig.US_MARKET
    else:
        raise ValueError(f"Unsupported market: {market}")

def validate_api_keys() -> dict:
    """API 키 유효성 검증"""
    status = {}
    
    # AI Provider 키 체크 (하나는 필수)
    ai_providers = {
        'openai': settings.openai_api_key,
        'gemini': settings.google_api_key,
        'anthropic': settings.anthropic_api_key
    }
    
    available_providers = []
    for provider, key in ai_providers.items():
        if key:
            status[provider] = {'status': 'configured', 'required': False}
            available_providers.append(provider)
        else:
            status[provider] = {'status': 'missing', 'required': False}
    
    # 최소 하나의 AI Provider는 필요
    if not available_providers:
        status['ai_provider'] = {'status': 'missing', 'required': True, 
                                'message': 'At least one AI provider key required (OpenAI, Gemini, or Anthropic)'}
    else:
        status['ai_provider'] = {'status': 'configured', 'required': True,
                               'available': available_providers}
    
    # 선택적 API 키
    optional_keys = {
        'serper_api_key': 'serper',
        'news_api_key': 'news',
        'alpha_vantage_api_key': 'alpha_vantage',
        'financial_modeling_prep_api_key': 'fmp'
    }
    
    for setting_name, service_name in optional_keys.items():
        key_value = getattr(settings, setting_name)
        if key_value:
            status[service_name] = {'status': 'configured', 'required': False}
        else:
            status[service_name] = {'status': 'missing', 'required': False}
    
    return status