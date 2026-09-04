import feedparser
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Political & Macro Sentiment Keywords
BULLISH_KEYWORDS = [
    "rate cut", "easing", "inflation cooling", "soft landing", "trade deal",
    "stimulus", "tax cut", "growth beats", "record highs", "peace talks",
    "금리 인하", "물가 안정", "경기 부양", "실적 호조", "수출 호조", "반등"
]

BEARISH_KEYWORDS = [
    "war", "military strike", "tariff hike", "sanction", "rate hike",
    "inflation surge", "recession fears", "escalation", "missile", "trade war",
    "debt crisis", "전쟁", "관세 폭탄", "긴축 강화", "물가 급등", "경기 침체",
    "수출 둔화", "환율 폭등", "제재"
]

BLACKOUT_KEYWORDS = [
    "fomc decision", "fed meeting today", "cpi report today", "jobs report today",
    "금통위 금리결정", "소비자물가 발표"
]

class MacroNewsCollector:
    """Automated news RSS reader and sentiment/blackout scorer."""

    def __init__(self):
        self.rss_feeds = [
            "https://finance.yahoo.com/news/rssindex",
            "https://news.google.com/rss/search?q=economy+inflation+fed+tariff&hl=en-US&gl=US&ceid=US:en"
        ]

    def fetch_news_and_score(self) -> dict:
        bull_count = 0
        bear_count = 0
        blackout_detected = False
        headlines = []

        for url in self.rss_feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:15]:
                    title = entry.title
                    summary = entry.get("summary", "")
                    full_text = f"{title} {summary}".lower()
                    headlines.append(title)

                    # Sentiment matching
                    for kw in BULLISH_KEYWORDS:
                        if kw in full_text:
                            bull_count += 1
                    for kw in BEARISH_KEYWORDS:
                        if kw in full_text:
                            bear_count += 1
                    for kw in BLACKOUT_KEYWORDS:
                        if kw in full_text:
                            blackout_detected = True
            except Exception as e:
                logger.warning(f"Error parsing news RSS {url}: {e}")

        total = bull_count + bear_count
        if total > 0:
            sentiment_score = round((bull_count - bear_count) / total, 2)
        else:
            sentiment_score = 0.0

        return {
            "sentiment_score": sentiment_score,  # -1.0 (Very Bearish) to +1.0 (Very Bullish)
            "bull_signals": bull_count,
            "bear_signals": bear_count,
            "blackout_alert": blackout_detected,
            "sample_headlines": headlines[:5]
        }

if __name__ == "__main__":
    collector = MacroNewsCollector()
    result = collector.fetch_news_and_score()
    print("News Sentiment Result:", result)
