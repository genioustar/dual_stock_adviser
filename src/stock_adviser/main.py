#!/usr/bin/env python3
"""
한미 주식 투자 자문 AI 시스템
Main Application Entry Point
"""

import asyncio
import sys
import argparse
from typing import Dict, Any, Optional
import json
from decimal import Decimal

from .services.analysis_service import DualStockAdviser
from .utils import app_logger, settings, validate_api_keys
from .models import RecommendationType


class DecimalEncoder(json.JSONEncoder):
    """Decimal 타입을 JSON으로 인코딩하기 위한 커스텀 인코더"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


async def analyze_single_stock(adviser: DualStockAdviser, symbol: str, market: str, user_profile: Optional[Dict] = None):
    """단일 종목 분석"""
    try:
        print(f"\n📊 {symbol} ({market}) 분석 중...")
        
        result = await adviser.analyze_stock(symbol, market, user_profile)
        
        if not result:
            print(f"❌ {symbol} 분석 실패")
            return
        
        # 결과 출력
        print(f"\n{result.generate_summary()}")
        
        return result
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {str(e)}")
        app_logger.error(f"단일 종목 분석 오류: {symbol}, {str(e)}")


async def analyze_multiple_stocks(adviser: DualStockAdviser, symbols: list, market: str):
    """여러 종목 비교 분석"""
    try:
        print(f"\n📊 {len(symbols)}개 종목 비교 분석 중...")
        
        # 병렬 분석
        tasks = [adviser.analyze_stock(symbol, market) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ {symbols[i]} 분석 실패: {str(result)}")
            elif result:
                successful_results.append(result)
        
        if successful_results:
            print(f"\n📈 비교 분석 결과 ({len(successful_results)}/{len(symbols)} 성공)")
            print("=" * 60)
            
            for result in successful_results:
                rec_emoji = {
                    RecommendationType.STRONG_BUY.value: "🟢",
                    RecommendationType.BUY.value: "🔵", 
                    RecommendationType.HOLD.value: "🟡",
                    RecommendationType.SELL.value: "🟠",
                    RecommendationType.STRONG_SELL.value: "🔴"
                }.get(result.recommendation.value, "⚪")
                
                print(f"{rec_emoji} {result.company_name} ({result.symbol})")
                print(f"   추천: {result.recommendation.value.upper()}")
                print(f"   현재가: {float(result.current_price):,.0f}원")
                print(f"   목표가: {float(result.price_targets.target_price):,.0f}원")
                print(f"   신뢰도: {float(result.confidence_level)*100:.0f}%")
                print()
        
    except Exception as e:
        print(f"❌ 비교 분석 중 오류 발생: {str(e)}")
        app_logger.error(f"다중 종목 분석 오류: {str(e)}")


async def analyze_portfolio_command(adviser: DualStockAdviser, portfolio_config: str):
    """포트폴리오 분석"""
    try:
        # 포트폴리오 설정 로드 (파일 또는 JSON 문자열)
        if portfolio_config.endswith('.json'):
            with open(portfolio_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = json.loads(portfolio_config)
        
        holdings = config.get('holdings', [])
        if not holdings:
            print("❌ 포트폴리오에 보유 종목이 없습니다.")
            return
        
        print(f"\n📊 포트폴리오 분석 중... ({len(holdings)}개 종목)")
        
        result = await adviser.analyze_portfolio(holdings)
        
        if result.get('error'):
            print(f"❌ 포트폴리오 분석 실패: {result['error']}")
            return
        
        # 결과 출력
        print(f"\n📈 포트폴리오 분석 결과")
        print("=" * 50)
        summary = result.get('portfolio_summary', {})
        print(f"분석 종목: {summary.get('total_stocks', 0)}개")
        print(f"평균 신뢰도: {summary.get('average_confidence', 0)*100:.0f}%")
        
        # 추천 분포
        rec_dist = summary.get('recommendation_distribution', {})
        if rec_dist:
            print("\n추천 분포:")
            for rec, count in rec_dist.items():
                print(f"  {rec}: {count}개")
        
        # 리스크 분포
        risk_dist = summary.get('risk_distribution', {})
        if risk_dist:
            print("\n리스크 분포:")
            for risk, count in risk_dist.items():
                print(f"  {risk}: {count}개")
        
    except Exception as e:
        print(f"❌ 포트폴리오 분석 중 오류 발생: {str(e)}")
        app_logger.error(f"포트폴리오 분석 오류: {str(e)}")


def setup_user_profile(args) -> Optional[Dict[str, Any]]:
    """사용자 프로필 설정"""
    profile = {}
    
    if hasattr(args, 'risk_tolerance') and args.risk_tolerance:
        profile['risk_tolerance'] = args.risk_tolerance
    
    if hasattr(args, 'investment_horizon') and args.investment_horizon:
        profile['investment_horizon'] = args.investment_horizon
        
    if hasattr(args, 'investment_style') and args.investment_style:
        profile['investment_style'] = args.investment_style
    
    return profile if profile else None


def check_api_keys():
    """API 키 확인"""
    print("🔑 API 키 상태 확인...")
    status = validate_api_keys()
    
    required_missing = []
    optional_missing = []
    
    for service, info in status.items():
        if info['status'] == 'missing':
            if info['required']:
                required_missing.append(service)
            else:
                optional_missing.append(service)
        else:
            print(f"  ✅ {service}: 설정됨")
    
    if required_missing:
        print(f"\n❌ 필수 API 키 누락: {', '.join(required_missing)}")
        print("  .env 파일에 필수 API 키를 설정해주세요.")
        return False
    
    if optional_missing:
        print(f"\n⚠️  선택적 API 키 누락: {', '.join(optional_missing)}")
        print("  일부 기능이 제한될 수 있습니다.")
    
    return True


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="한미 주식 투자 자문 AI 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 단일 종목 분석
  python -m stock_adviser analyze --symbol "005930" --market "KR"
  
  # 미국 종목 분석
  python -m stock_adviser analyze --symbol "AAPL" --market "US"
  
  # 여러 종목 비교
  python -m stock_adviser compare --symbols "AAPL,MSFT,GOOGL" --market "US"
  
  # 포트폴리오 분석
  python -m stock_adviser portfolio --config portfolio.json
        """
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('--debug', action='store_true', help='디버그 모드')
    
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령')
    
    # analyze 명령
    analyze_parser = subparsers.add_parser('analyze', help='단일 종목 분석')
    analyze_parser.add_argument('--symbol', required=True, help='종목 코드 (예: 005930, AAPL)')
    analyze_parser.add_argument('--market', default='KR', choices=['KR', 'US'], help='시장 (기본: KR)')
    analyze_parser.add_argument('--risk-tolerance', choices=['conservative', 'moderate', 'aggressive'], help='위험 허용도')
    analyze_parser.add_argument('--investment-horizon', choices=['short_term', 'medium_term', 'long_term'], help='투자 기간')
    analyze_parser.add_argument('--investment-style', choices=['conservative', 'moderate', 'aggressive'], help='투자 스타일')
    analyze_parser.add_argument('--json', action='store_true', help='JSON 형태로 결과 출력')
    
    # compare 명령  
    compare_parser = subparsers.add_parser('compare', help='여러 종목 비교 분석')
    compare_parser.add_argument('--symbols', required=True, help='종목 코드들 (쉼표로 구분, 예: AAPL,MSFT,GOOGL)')
    compare_parser.add_argument('--market', default='US', choices=['KR', 'US'], help='시장 (기본: US)')
    
    # portfolio 명령
    portfolio_parser = subparsers.add_parser('portfolio', help='포트폴리오 분석')
    portfolio_parser.add_argument('--config', required=True, help='포트폴리오 설정 파일 (.json) 또는 JSON 문자열')
    
    # API 키 확인 명령
    subparsers.add_parser('check-keys', help='API 키 상태 확인')
    
    args = parser.parse_args()
    
    if args.debug:
        app_logger.setLevel('DEBUG')
        print("🐛 디버그 모드 활성화")
    
    print("🤖 한미 주식 투자 자문 AI 시스템")
    print("=" * 50)
    
    # API 키 상태 확인
    if not check_api_keys():
        print("\n❌ 필수 API 키가 설정되지 않았습니다.")
        print("   .env 파일을 확인해주세요.")
        sys.exit(1)
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'check-keys':
        return
    
    try:
        # DualStockAdviser 초기화
        adviser = DualStockAdviser()
        
        if args.command == 'analyze':
            user_profile = setup_user_profile(args)
            result = await analyze_single_stock(adviser, args.symbol, args.market, user_profile)
            
            if args.json and result:
                print("\n📄 JSON 결과:")
                print(json.dumps(result.to_dict(), cls=DecimalEncoder, indent=2, ensure_ascii=False))
        
        elif args.command == 'compare':
            symbols = [s.strip() for s in args.symbols.split(',')]
            await analyze_multiple_stocks(adviser, symbols, args.market)
        
        elif args.command == 'portfolio':
            await analyze_portfolio_command(adviser, args.config)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {str(e)}")
        app_logger.error(f"메인 실행 오류: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())