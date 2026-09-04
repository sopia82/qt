import sys
import argparse
import logging
from datetime import datetime

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.data.collector_macro import MacroDataCollector
from src.data.collector_news import MacroNewsCollector
from src.data.collector_us import USStockCollector
from src.data.collector_kr import KRStockCollector

from src.engine.gate0_macro_event import Gate0MacroEventEngine
from src.engine.gate1_market_regime import Gate1MarketRegimeEngine
from src.engine.gate2_screening import Gate2ScreeningEngine
from src.engine.gate3_timing import Gate3TimingEngine
from src.engine.gate4_risk import Gate4RiskEngine
from src.notification.notifier import NotificationManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/trading.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("Q-TAP")

def run_pipeline(sample_size=None, dry_run=False):
    """
    Executes full Q-TAP automated pipeline:
    1. Collects Macro & News -> Evaluates Gate 0 & Gate 1
    2. Collects S&P 500 & KOSPI 100 stocks
    3. Evaluates Gate 2 (Screening), Gate 3 (Timing), Gate 4 (Risk/Sizing)
    4. Outputs report to console and Telegram
    """
    logger.info("=== Starting Q-TAP Automated Trading Pipeline ===")

    # Initialize components
    macro_collector = MacroDataCollector()
    news_collector = MacroNewsCollector()
    us_collector = USStockCollector()
    kr_collector = KRStockCollector()

    g0_engine = Gate0MacroEventEngine()
    g1_engine = Gate1MarketRegimeEngine()
    g2_engine = Gate2ScreeningEngine()
    g3_engine = Gate3TimingEngine()
    g4_engine = Gate4RiskEngine()
    notifier = NotificationManager()

    # Step 1: Macro & Political Event Evaluation (Gate 0 & Gate 1)
    logger.info("[Step 1] Fetching Macro & News data...")
    macro_data = macro_collector.fetch_macro_indicators()
    news_data = news_collector.fetch_news_and_score()

    gate0_result = g0_engine.evaluate(macro_data, news_data)
    gate1_result = g1_engine.evaluate(macro_data)

    logger.info(f"Gate 0 Status: {gate0_result['status']} | Allow Entries: {gate0_result['allow_new_entries']}")

    short_term_candidates = []
    long_term_candidates = []

    # Step 2: Fetch Stock Data & Apply Gate 2 ~ Gate 4
    if gate0_result["allow_new_entries"]:
        fetch_limit = sample_size if sample_size else (4 if dry_run else None)

        logger.info(f"[Step 2] Collecting S&P 500 stocks (Limit: {fetch_limit})...")
        us_stocks = us_collector.fetch_all(max_count=fetch_limit)

        logger.info(f"[Step 2] Collecting KOSPI 100 stocks (Limit: {fetch_limit})...")
        kr_stocks = kr_collector.fetch_all(max_count=fetch_limit)

        all_stocks = us_stocks + kr_stocks

        for stock in all_stocks:
            # 1. Short-Term Analysis
            st_score = g2_engine.score_short_term(stock)
            if st_score["qualified"] or dry_run:
                st_timing = g3_engine.calculate_short_term_timing(stock)
                st_risk = g4_risk = g4_engine.calculate_position_size(
                    stock, "SHORT_TERM", gate0_result["max_portfolio_exposure"]
                )
                short_term_candidates.append({
                    "market": stock["market"],
                    "ticker": stock["ticker"],
                    "name": stock["name"],
                    "score": st_score["short_term_score"],
                    "entry_price": st_timing["entry_price"],
                    "stop_loss": st_timing["stop_loss"],
                    "target_price": st_timing["target_price"],
                    "alloc_pct": st_risk["target_allocation_pct"],
                    "factors": st_score["key_factors"]
                })

            # 2. Long-Term Analysis
            lt_score = g2_engine.score_long_term(stock)
            if lt_score["qualified"] or dry_run:
                lt_timing = g3_engine.calculate_long_term_timing(stock)
                lt_risk = g4_engine.calculate_position_size(
                    stock, "LONG_TERM", gate0_result["max_portfolio_exposure"]
                )
                long_term_candidates.append({
                    "market": stock["market"],
                    "ticker": stock["ticker"],
                    "name": stock["name"],
                    "score": lt_score["long_term_score"],
                    "entry_price": lt_timing["entry_price"],
                    "stop_loss": lt_timing["stop_loss"],
                    "target_price": lt_timing["target_price"],
                    "alloc_pct": lt_risk["target_allocation_pct"],
                    "factors": lt_score["key_factors"]
                })
    else:
        logger.warning("Trading paused due to Gate 0 Macro / Blackout risk threshold.")

    # Sort picks by score descending
    short_term_picks = sorted(short_term_candidates, key=lambda x: x["score"], reverse=True)
    long_term_picks = sorted(long_term_candidates, key=lambda x: x["score"], reverse=True)

    summary = {
        "gate0": gate0_result,
        "gate1": gate1_result,
        "short_term_picks": short_term_picks,
        "long_term_picks": long_term_picks,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Step 3: Dispatch Report
    notifier.report(summary)
    logger.info("=== Q-TAP Pipeline Execution Completed Successfully ===")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Q-TAP Automated Trading System")
    parser.add_argument("--dry-run", action="store_true", help="Run quick dry-run test with sample tickers")
    parser.add_argument("--sample", type=int, default=None, help="Sample size limit for quick testing")
    args = parser.parse_args()

    run_pipeline(sample_size=args.sample, dry_run=args.dry_run)
