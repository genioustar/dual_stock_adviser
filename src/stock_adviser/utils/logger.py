import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

from .config import settings

class ColoredFormatter(logging.Formatter):
    """컬러 포맷터 (터미널용)"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON 포맷터 (구조화된 로그용)"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
            
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logger(
    name: str,
    level: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = True,
    json_format: bool = False
) -> logging.Logger:
    """로거 설정"""
    
    logger = logging.getLogger(name)
    
    # 이미 설정된 경우 반환
    if logger.handlers:
        return logger
    
    # 로그 레벨 설정
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 포맷터 설정
    if json_format:
        formatter = JSONFormatter()
        console_formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # 콘솔 핸들러
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # 파일 핸들러
    if file_output:
        # 메인 로그 파일
        file_handler = logging.handlers.RotatingFileHandler(
            settings.logs_dir / f"{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 에러 로그 파일 (ERROR 이상)
        error_handler = logging.handlers.RotatingFileHandler(
            settings.logs_dir / "error.log",
            maxBytes=10*1024*1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """로거 반환 (이미 설정된 경우 재사용)"""
    return logging.getLogger(name)

class StockAnalysisLogger:
    """주식 분석 전용 로거"""
    
    def __init__(self, logger_name: str = "stock_analysis"):
        self.logger = setup_logger(
            logger_name,
            json_format=True,
            file_output=True
        )
    
    def log_analysis_start(self, symbol: str, analysis_type: str):
        """분석 시작 로그"""
        self.logger.info(
            f"분석 시작: {symbol}",
            extra={
                'event': 'analysis_start',
                'symbol': symbol,
                'analysis_type': analysis_type,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_analysis_complete(self, symbol: str, result: dict, processing_time: float):
        """분석 완료 로그"""
        self.logger.info(
            f"분석 완료: {symbol}",
            extra={
                'event': 'analysis_complete',
                'symbol': symbol,
                'result': result,
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_analysis_error(self, symbol: str, error: Exception):
        """분석 에러 로그"""
        self.logger.error(
            f"분석 실패: {symbol}",
            extra={
                'event': 'analysis_error',
                'symbol': symbol,
                'error': str(error),
                'timestamp': datetime.utcnow().isoformat()
            },
            exc_info=True
        )
    
    def log_data_fetch(self, symbol: str, data_source: str, success: bool):
        """데이터 수집 로그"""
        level = logging.INFO if success else logging.WARNING
        self.logger.log(
            level,
            f"데이터 수집 {'성공' if success else '실패'}: {symbol} from {data_source}",
            extra={
                'event': 'data_fetch',
                'symbol': symbol,
                'data_source': data_source,
                'success': success,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_agent_execution(self, agent_name: str, symbol: str, execution_time: float, success: bool):
        """Agent 실행 로그"""
        level = logging.INFO if success else logging.ERROR
        self.logger.log(
            level,
            f"Agent 실행 {'완료' if success else '실패'}: {agent_name} for {symbol}",
            extra={
                'event': 'agent_execution',
                'agent_name': agent_name,
                'symbol': symbol,
                'execution_time': execution_time,
                'success': success,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

class PerformanceLogger:
    """성능 모니터링 로거"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = setup_logger(
            logger_name,
            json_format=True
        )
        
        # 성능 로그 파일 핸들러 추가
        perf_handler = logging.handlers.RotatingFileHandler(
            settings.logs_dir / "performance.log",
            maxBytes=5*1024*1024,
            backupCount=3
        )
        perf_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(perf_handler)
    
    def log_api_call(self, endpoint: str, response_time: float, status_code: int, symbol: str = None):
        """API 호출 성능 로그"""
        self.logger.info(
            f"API Call: {endpoint}",
            extra={
                'event': 'api_call',
                'endpoint': endpoint,
                'response_time': response_time,
                'status_code': status_code,
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_processing_time(self, operation: str, processing_time: float, symbol: str = None):
        """처리 시간 로그"""
        self.logger.info(
            f"Processing: {operation}",
            extra={
                'event': 'processing_time',
                'operation': operation,
                'processing_time': processing_time,
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

# 글로벌 로거 인스턴스
app_logger = setup_logger("stock_adviser")
analysis_logger = StockAnalysisLogger()
performance_logger = PerformanceLogger()

def configure_logging():
    """전체 로깅 설정"""
    # 루트 로거 레벨 설정
    logging.getLogger().setLevel(logging.WARNING)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.ERROR)
    
    app_logger.info("로깅 시스템 초기화 완료")

# 초기화
configure_logging()