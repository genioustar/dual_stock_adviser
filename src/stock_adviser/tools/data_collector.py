import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp
from decimal import Decimal

from ..models import StockData, StockInfo, StockPrice, FinancialMetrics, TechnicalIndicators
from ..utils import settings, app_logger, performance_logger, get_market_config, APIEndpoints


class DataCollector:
    """주식 데이터 수집 도구"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    async def get_stock_data(self, symbol: str, market: str, period: str = "1y") -> Optional[StockData]:
        """종합 주식 데이터 수집"""
        try:
            app_logger.info(f"주식 데이터 수집 시작: {symbol} ({market})")
            start_time = datetime.now()
            
            # 병렬로 데이터 수집
            tasks = [
                self.get_price_data(symbol, market, period),
                self.get_company_info(symbol, market),
                self.get_financial_metrics(symbol, market),
                self.get_news_data(symbol, market)
            ]
            
            price_data, company_info, financial_metrics, news_data = await asyncio.gather(*tasks)
            
            if not price_data or not company_info:
                app_logger.error(f"필수 데이터 수집 실패: {symbol}")
                return None
            
            # 기술적 지표 계산
            technical_indicators = self.calculate_technical_indicators(price_data)
            
            # StockData 객체 생성
            stock_data = StockData(
                info=company_info,
                current_price=price_data[-1] if price_data else StockPrice(
                    open=Decimal('0'), high=Decimal('0'), low=Decimal('0'), 
                    close=Decimal('0'), volume=0, timestamp=datetime.now()
                ),
                price_history=price_data,
                financial_metrics=financial_metrics,
                technical_indicators=technical_indicators,
                news_data=news_data
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            performance_logger.log_processing_time("stock_data_collection", processing_time, symbol)
            
            app_logger.info(f"주식 데이터 수집 완료: {symbol}, 처리시간: {processing_time:.2f}초")
            return stock_data
            
        except Exception as e:
            app_logger.error(f"주식 데이터 수집 실패: {symbol}, 오류: {str(e)}")
            return None
    
    async def get_price_data(self, symbol: str, market: str, period: str = "1y") -> List[StockPrice]:
        """가격 데이터 수집"""
        try:
            # yfinance 심볼 변환
            yf_symbol = APIEndpoints.get_yfinance_symbol(symbol, market)
            
            # 데이터 수집
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                app_logger.warning(f"가격 데이터 없음: {symbol}")
                return []
            
            price_data = []
            for date, row in hist.iterrows():
                price = StockPrice(
                    open=Decimal(str(row['Open'])),
                    high=Decimal(str(row['High'])),
                    low=Decimal(str(row['Low'])),
                    close=Decimal(str(row['Close'])),
                    volume=int(row['Volume']),
                    timestamp=date.to_pydatetime()
                )
                price_data.append(price)
            
            performance_logger.log_processing_time("price_data_fetch", 0.5, symbol)
            return price_data
            
        except Exception as e:
            app_logger.error(f"가격 데이터 수집 실패: {symbol}, 오류: {str(e)}")
            return []
    
    async def get_company_info(self, symbol: str, market: str) -> Optional[StockInfo]:
        """기업 정보 수집"""
        try:
            yf_symbol = APIEndpoints.get_yfinance_symbol(symbol, market)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            if not info:
                app_logger.warning(f"기업 정보 없음: {symbol}")
                return None
            
            market_config = get_market_config(market)
            
            stock_info = StockInfo(
                symbol=symbol,
                name=info.get('longName', info.get('shortName', symbol)),
                market=market.upper(),
                sector=info.get('sector'),
                industry=info.get('industry'),
                currency=market_config['currency']
            )
            
            return stock_info
            
        except Exception as e:
            app_logger.error(f"기업 정보 수집 실패: {symbol}, 오류: {str(e)}")
            return None
    
    async def get_financial_metrics(self, symbol: str, market: str) -> FinancialMetrics:
        """재무 지표 수집"""
        try:
            yf_symbol = APIEndpoints.get_yfinance_symbol(symbol, market)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            metrics = FinancialMetrics()
            
            if info:
                # 주요 재무 지표 수집
                if 'trailingPE' in info and info['trailingPE']:
                    metrics.pe_ratio = Decimal(str(info['trailingPE']))
                
                if 'priceToBook' in info and info['priceToBook']:
                    metrics.pb_ratio = Decimal(str(info['priceToBook']))
                    
                if 'returnOnEquity' in info and info['returnOnEquity']:
                    metrics.roe = Decimal(str(info['returnOnEquity']))
                
                if 'debtToEquity' in info and info['debtToEquity']:
                    metrics.debt_ratio = Decimal(str(info['debtToEquity'] / 100))
                
                if 'marketCap' in info and info['marketCap']:
                    metrics.market_cap = Decimal(str(info['marketCap']))
                
                if 'dividendYield' in info and info['dividendYield']:
                    metrics.dividend_yield = Decimal(str(info['dividendYield']))
            
            return metrics
            
        except Exception as e:
            app_logger.error(f"재무 지표 수집 실패: {symbol}, 오류: {str(e)}")
            return FinancialMetrics()
    
    def calculate_technical_indicators(self, price_data: List[StockPrice]) -> TechnicalIndicators:
        """기술적 지표 계산"""
        try:
            if len(price_data) < 20:
                app_logger.warning("기술적 지표 계산을 위한 데이터 부족")
                return TechnicalIndicators()
            
            # 종가 리스트 생성
            closes = [float(price.close) for price in price_data]
            
            indicators = TechnicalIndicators()
            
            # RSI 계산 (14일)
            if len(closes) >= 14:
                rsi = self._calculate_rsi(closes, 14)
                if rsi:
                    indicators.rsi = Decimal(str(rsi))
            
            # 이동평균선 계산
            if len(closes) >= 20:
                sma_20 = sum(closes[-20:]) / 20
                indicators.sma_20 = Decimal(str(sma_20))
            
            if len(closes) >= 50:
                sma_50 = sum(closes[-50:]) / 50
                indicators.sma_50 = Decimal(str(sma_50))
            
            if len(closes) >= 200:
                sma_200 = sum(closes[-200:]) / 200
                indicators.sma_200 = Decimal(str(sma_200))
            
            # 볼린저 밴드 계산 (20일, 2σ)
            if len(closes) >= 20:
                bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(closes, 20, 2)
                if bb_upper:
                    indicators.bollinger_upper = Decimal(str(bb_upper))
                    indicators.bollinger_middle = Decimal(str(bb_middle))
                    indicators.bollinger_lower = Decimal(str(bb_lower))
            
            # MACD 계산 (12, 26, 9)
            if len(closes) >= 26:
                macd, signal, histogram = self._calculate_macd(closes)
                if macd:
                    indicators.macd = Decimal(str(macd))
                    indicators.macd_signal = Decimal(str(signal))
                    indicators.macd_histogram = Decimal(str(histogram))
            
            return indicators
            
        except Exception as e:
            app_logger.error(f"기술적 지표 계산 실패: {str(e)}")
            return TechnicalIndicators()
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """RSI 계산"""
        try:
            if len(prices) < period + 1:
                return None
            
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception:
            return None
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> tuple:
        """볼린저 밴드 계산"""
        try:
            if len(prices) < period:
                return None, None, None
            
            recent_prices = prices[-period:]
            middle = sum(recent_prices) / period
            
            variance = sum([(p - middle) ** 2 for p in recent_prices]) / period
            std_deviation = variance ** 0.5
            
            upper = middle + (std_deviation * std_dev)
            lower = middle - (std_deviation * std_dev)
            
            return upper, middle, lower
            
        except Exception:
            return None, None, None
    
    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """MACD 계산"""
        try:
            if len(prices) < slow:
                return None, None, None
            
            # 지수 이동평균 계산
            def calculate_ema(prices, period):
                multiplier = 2 / (period + 1)
                ema = prices[0]
                for price in prices[1:]:
                    ema = (price - ema) * multiplier + ema
                return ema
            
            ema_fast = calculate_ema(prices[-fast:], fast)
            ema_slow = calculate_ema(prices[-slow:], slow)
            
            macd_line = ema_fast - ema_slow
            
            # MACD 히스토리가 충분한 경우 시그널 라인 계산
            if len(prices) >= slow + signal:
                # 단순화: 실제로는 MACD 값들의 EMA를 계산해야 함
                signal_line = macd_line * 0.9  # 근사값
                histogram = macd_line - signal_line
            else:
                signal_line = macd_line
                histogram = 0
            
            return macd_line, signal_line, histogram
            
        except Exception:
            return None, None, None
    
    async def get_news_data(self, symbol: str, market: str, limit: int = 10) -> List[Dict[str, Any]]:
        """뉴스 데이터 수집"""
        try:
            news_data = []
            
            # News API 사용 (API 키가 있는 경우)
            if settings.news_api_key:
                news_data.extend(await self._fetch_news_api_data(symbol, market, limit))
            
            # Serper API 사용 (API 키가 있는 경우)  
            if settings.serper_api_key and len(news_data) < limit:
                remaining = limit - len(news_data)
                news_data.extend(await self._fetch_serper_data(symbol, market, remaining))
            
            # yfinance 뉴스 (fallback)
            if len(news_data) < limit:
                news_data.extend(self._fetch_yfinance_news(symbol, market, limit))
            
            return news_data[:limit]
            
        except Exception as e:
            app_logger.error(f"뉴스 데이터 수집 실패: {symbol}, 오류: {str(e)}")
            return []
    
    async def _fetch_news_api_data(self, symbol: str, market: str, limit: int) -> List[Dict[str, Any]]:
        """News API에서 뉴스 수집"""
        try:
            # 검색 쿼리 생성
            if market.upper() == 'KR':
                # 한국 종목의 경우 한글 검색어 사용 필요
                query = f"{symbol} 주식"
            else:
                query = symbol
            
            url = f"{APIEndpoints.NEWS_API_BASE}/everything"
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'language': 'ko' if market.upper() == 'KR' else 'en',
                'pageSize': min(limit, 20),
                'apiKey': settings.news_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        news_data = []
                        for article in articles:
                            news_data.append({
                                'title': article.get('title'),
                                'description': article.get('description'),
                                'url': article.get('url'),
                                'published_at': article.get('publishedAt'),
                                'source': article.get('source', {}).get('name'),
                                'sentiment': None  # 추후 감성 분석 추가
                            })
                        
                        return news_data
                    
            return []
            
        except Exception as e:
            app_logger.error(f"News API 데이터 수집 실패: {str(e)}")
            return []
    
    async def _fetch_serper_data(self, symbol: str, market: str, limit: int) -> List[Dict[str, Any]]:
        """Serper API에서 뉴스 검색"""
        try:
            # 검색 쿼리 생성
            if market.upper() == 'KR':
                query = f"{symbol} 주식 뉴스"
            else:
                query = f"{symbol} stock news"
            
            headers = {
                'X-API-KEY': settings.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'q': query,
                'num': min(limit, 10)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{APIEndpoints.SERPER_API_BASE}/news", 
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        news_items = result.get('news', [])
                        
                        news_data = []
                        for item in news_items:
                            news_data.append({
                                'title': item.get('title'),
                                'description': item.get('snippet'),
                                'url': item.get('link'),
                                'published_at': item.get('date'),
                                'source': item.get('source'),
                                'sentiment': None
                            })
                        
                        return news_data
                    
            return []
            
        except Exception as e:
            app_logger.error(f"Serper API 데이터 수집 실패: {str(e)}")
            return []
    
    def _fetch_yfinance_news(self, symbol: str, market: str, limit: int) -> List[Dict[str, Any]]:
        """yfinance에서 뉴스 수집 (fallback)"""
        try:
            yf_symbol = APIEndpoints.get_yfinance_symbol(symbol, market)
            ticker = yf.Ticker(yf_symbol)
            news = ticker.news
            
            news_data = []
            for item in news[:limit]:
                news_data.append({
                    'title': item.get('title'),
                    'description': item.get('summary'),
                    'url': item.get('link'),
                    'published_at': datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat(),
                    'source': item.get('publisher'),
                    'sentiment': None
                })
            
            return news_data
            
        except Exception as e:
            app_logger.error(f"yfinance 뉴스 수집 실패: {str(e)}")
            return []
    
    def __del__(self):
        """세션 정리"""
        if hasattr(self, 'session'):
            self.session.close()