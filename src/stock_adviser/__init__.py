"""
한미 주식 투자 자문 AI 시스템
Dual Stock Adviser - AI-powered stock analysis system for Korean and US markets
"""

from .services import DualStockAdviser, StockAnalysisService
from .models import (
    StockData, StockAnalysisResult, RecommendationType, RiskLevel,
    MarketSentiment, RiskMetrics
)

__version__ = "0.1.0"
__author__ = "Dual Stock Adviser Team"
__email__ = "contact@dualstockadviser.com"

__all__ = [
    'DualStockAdviser',
    'StockAnalysisService', 
    'StockData',
    'StockAnalysisResult',
    'RecommendationType',
    'RiskLevel',
    'MarketSentiment',
    'RiskMetrics'
]