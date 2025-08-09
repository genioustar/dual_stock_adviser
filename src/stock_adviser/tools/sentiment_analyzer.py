from textblob import TextBlob
import nltk
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import re

from ..utils import app_logger


class SentimentAnalyzer:
    """감성 분석 도구"""
    
    def __init__(self):
        self._ensure_nltk_data()
        
    def _ensure_nltk_data(self):
        """필요한 NLTK 데이터 다운로드"""
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download('stopwords', quiet=True)
                nltk.download('punkt', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
            except Exception as e:
                app_logger.warning(f"NLTK 데이터 다운로드 실패: {str(e)}")
    
    def analyze_news_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """뉴스 데이터 감성 분석"""
        try:
            if not news_data:
                return self._get_default_sentiment_result()
            
            total_sentiment = 0.0
            sentiment_scores = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            analyzed_news = []
            
            for news in news_data:
                title = news.get('title', '')
                description = news.get('description', '')
                
                # 제목과 설명 결합
                text = f"{title} {description}".strip()
                
                if not text:
                    continue
                
                # 감성 분석 수행
                sentiment_score = self._analyze_text_sentiment(text)
                sentiment_scores.append(sentiment_score)
                total_sentiment += sentiment_score
                
                # 카테고리 분류
                if sentiment_score > 0.1:
                    category = 'positive'
                    positive_count += 1
                elif sentiment_score < -0.1:
                    category = 'negative'
                    negative_count += 1
                else:
                    category = 'neutral'
                    neutral_count += 1
                
                analyzed_news.append({
                    'title': title,
                    'sentiment_score': sentiment_score,
                    'sentiment_category': category,
                    'url': news.get('url'),
                    'published_at': news.get('published_at')
                })
            
            if not sentiment_scores:
                return self._get_default_sentiment_result()
            
            # 전체 감성 점수 계산
            avg_sentiment = total_sentiment / len(sentiment_scores)
            
            # 신뢰도 계산 (뉴스 개수와 점수 분산 기반)
            score_variance = sum((score - avg_sentiment) ** 2 for score in sentiment_scores) / len(sentiment_scores)
            confidence = min(1.0, max(0.1, 1 - (score_variance * 2)))  # 분산이 클수록 신뢰도 낮음
            confidence *= min(1.0, len(sentiment_scores) / 10)  # 뉴스 개수가 많을수록 신뢰도 높음
            
            # 전체 카테고리 결정
            if avg_sentiment > 0.2:
                overall_category = 'positive'
            elif avg_sentiment < -0.2:
                overall_category = 'negative'
            else:
                overall_category = 'neutral'
            
            return {
                'overall_sentiment': float(avg_sentiment),
                'overall_category': overall_category,
                'confidence': float(confidence),
                'news_count': len(analyzed_news),
                'sentiment_distribution': {
                    'positive': positive_count,
                    'negative': negative_count,
                    'neutral': neutral_count
                },
                'analyzed_news': analyzed_news,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            app_logger.error(f"뉴스 감성 분석 실패: {str(e)}")
            return self._get_default_sentiment_result()
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """텍스트 감성 분석"""
        try:
            # 텍스트 전처리
            cleaned_text = self._preprocess_text(text)
            
            # TextBlob을 사용한 감성 분석
            blob = TextBlob(cleaned_text)
            sentiment = blob.sentiment.polarity
            
            # 금융 특화 키워드 가중치 적용
            sentiment = self._apply_financial_keywords_weight(cleaned_text, sentiment)
            
            # -1.0 ~ 1.0 범위로 정규화
            return max(-1.0, min(1.0, sentiment))
            
        except Exception as e:
            app_logger.error(f"텍스트 감성 분석 실패: {str(e)}")
            return 0.0
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        try:
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', text)
            
            # 특수 문자 정리 (기본적인 것만)
            text = re.sub(r'[^\w\s가-힣]', ' ', text)
            
            # 여러 공백을 하나로
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception:
            return text
    
    def _apply_financial_keywords_weight(self, text: str, base_sentiment: float) -> float:
        """금융 특화 키워드 가중치 적용"""
        try:
            text_lower = text.lower()
            
            # 긍정적 금융 키워드
            positive_keywords = [
                '상승', '증가', '성장', '개선', '호조', '강세', '급등', '돌파',
                '수익', '이익', '매출', '실적', '호실적', '흑자', '배당',
                'growth', 'profit', 'revenue', 'earnings', 'bullish', 'rally',
                'surge', 'gain', 'rise', 'increase', 'outperform'
            ]
            
            # 부정적 금융 키워드  
            negative_keywords = [
                '하락', '감소', '급락', '폭락', '위험', '손실', '적자', '부진',
                '약세', '하향', '조정', '우려', '불안', '위기', '침체',
                'decline', 'fall', 'loss', 'bearish', 'crash', 'plunge',
                'drop', 'decrease', 'risk', 'concern', 'worry', 'crisis'
            ]
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
            
            # 키워드 가중치 적용
            keyword_weight = (positive_count - negative_count) * 0.1
            adjusted_sentiment = base_sentiment + keyword_weight
            
            return max(-1.0, min(1.0, adjusted_sentiment))
            
        except Exception:
            return base_sentiment
    
    def analyze_social_sentiment(self, social_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """소셜 미디어 감성 분석 (향후 구현)"""
        # 현재는 기본 구현만 제공
        return {
            'overall_sentiment': 0.0,
            'overall_category': 'neutral',
            'confidence': 0.0,
            'message': 'Social media sentiment analysis not implemented'
        }
    
    def get_sentiment_summary(self, symbol: str, news_sentiment: Dict, social_sentiment: Optional[Dict] = None) -> Dict[str, Any]:
        """감성 분석 종합 결과"""
        try:
            # 뉴스 감성 기준으로 종합 점수 계산
            overall_score = news_sentiment.get('overall_sentiment', 0.0)
            overall_confidence = news_sentiment.get('confidence', 0.0)
            
            # 소셜 미디어 감성이 있다면 결합 (향후 구현)
            if social_sentiment and social_sentiment.get('confidence', 0) > 0.3:
                social_score = social_sentiment.get('overall_sentiment', 0.0)
                social_confidence = social_sentiment.get('confidence', 0.0)
                
                # 가중 평균 계산
                total_weight = overall_confidence + social_confidence
                if total_weight > 0:
                    overall_score = (overall_score * overall_confidence + social_score * social_confidence) / total_weight
                    overall_confidence = min(1.0, (overall_confidence + social_confidence) / 2)
            
            # 전체 카테고리 결정
            if overall_score > 0.2:
                overall_category = 'positive'
            elif overall_score < -0.2:
                overall_category = 'negative'
            else:
                overall_category = 'neutral'
            
            return {
                'symbol': symbol,
                'sentiment_score': Decimal(str(overall_score)),
                'sentiment_category': overall_category,
                'confidence': Decimal(str(overall_confidence)),
                'news_sentiment': news_sentiment,
                'social_sentiment': social_sentiment,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            app_logger.error(f"감성 분석 종합 실패: {symbol}, 오류: {str(e)}")
            return self._get_default_sentiment_summary(symbol)
    
    def _get_default_sentiment_result(self) -> Dict[str, Any]:
        """기본 감성 분석 결과"""
        return {
            'overall_sentiment': 0.0,
            'overall_category': 'neutral',
            'confidence': 0.1,
            'news_count': 0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'analyzed_news': [],
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _get_default_sentiment_summary(self, symbol: str) -> Dict[str, Any]:
        """기본 감성 분석 종합 결과"""
        return {
            'symbol': symbol,
            'sentiment_score': Decimal('0.0'),
            'sentiment_category': 'neutral',
            'confidence': Decimal('0.1'),
            'news_sentiment': self._get_default_sentiment_result(),
            'social_sentiment': None,
            'analysis_timestamp': datetime.now().isoformat()
        }