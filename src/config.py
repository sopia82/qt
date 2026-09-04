import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Macro / FRED API
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# System Mode
SYSTEM_MODE = os.getenv("SYSTEM_MODE", "SIMULATION")

# Risk & Position Limits
MAX_SHORT_TERM_POSITIONS = int(os.getenv("MAX_SHORT_TERM_POSITIONS", 4))
MAX_LONG_TERM_POSITIONS = int(os.getenv("MAX_LONG_TERM_POSITIONS", 8))
SHORT_TERM_STOP_LOSS_PCT = float(os.getenv("SHORT_TERM_STOP_LOSS_PCT", 0.03))
LONG_TERM_STOP_LOSS_PCT = float(os.getenv("LONG_TERM_STOP_LOSS_PCT", 0.07))

# S&P 500 Focus Candidates (High liquidity & representative sector leaders)
SP500_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B",
    "JPM", "V", "UNH", "XOM", "LLY", "AVGO", "COST", "AMD",
    "NFLX", "CAT", "GE", "QCOM", "TXN", "HON", "BA", "GS"
]

# KOSPI 100 Focus Candidates (Core large caps across sectors)
KOSPI_UNIVERSE = [
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("373220", "LG에너지솔루션"),
    ("207940", "삼성바이오로직스"),
    ("005380", "현대차"),
    ("000270", "기아"),
    ("068270", "셀트리온"),
    ("105560", "KB금융"),
    ("055550", "신한지주"),
    ("035420", "NAVER"),
    ("035720", "카카오"),
    ("051910", "LG화학"),
    ("006400", "삼성SDI"),
    ("012330", "현대모비스"),
    ("028260", "삼성물산"),
    ("032830", "삼성생명"),
    ("086790", "하나금융지주"),
    ("015760", "한국전력"),
    ("009150", "삼성전기"),
    ("010130", "고려아연")
]

# Macro Symbols
MACRO_SYMBOLS = {
    "VIX": "^VIX",
    "SP500": "^GSPC",
    "KOSPI": "^KS11",
    "US_10Y": "^TNX",
    "USDKRW": "KRW=X",
    "WTI": "CL=F",
    "DXY": "UUP"
}
