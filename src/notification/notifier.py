import requests
import logging
from tabulate import tabulate
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

class NotificationManager:
    """Dispatches console reports and Telegram smartphone alerts."""

    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID

    def send_telegram_message(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.debug("Telegram credentials not configured. Skipping Telegram dispatch.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                logger.info("Telegram notification sent successfully.")
                return True
            else:
                logger.warning(f"Failed to send Telegram message: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False

    def report(self, analysis_summary: dict):
        """Prints a comprehensive report and dispatches telegram notification."""
        gate0 = analysis_summary.get("gate0", {})
        gate1 = analysis_summary.get("gate1", {})
        short_term_picks = analysis_summary.get("short_term_picks", [])
        long_term_picks = analysis_summary.get("long_term_picks", [])

        report_lines = []
        report_lines.append("=" * 65)
        report_lines.append("  [Q-TAP] QUANTUM TRADING ANALYSIS REPORT")
        report_lines.append("=" * 65)

        # Gate 0 Report
        status_kr = {
            "NORMAL": "정상 (안정 국면)",
            "CAUTION": "경계 (보수적 운영)",
            "BLACKOUT": "이벤트 동결 (블랙아웃)",
            "CRITICAL_RISK_OFF": "긴급 위험 회피 (현금 확대)"
        }.get(gate0.get("status", "NORMAL"), "NORMAL")

        report_lines.append(f"\n[Gate 0: 정치·거시 리스크] 상태: {status_kr}")
        report_lines.append(f" - VIX 공포지수: {gate0.get('vix')} | 뉴스 감성 점수: {gate0.get('sentiment_score')}")
        for r in gate0.get("reasons", []):
            report_lines.append(f"   * {r}")

        # Gate 1 Report
        report_lines.append(f"\n[Gate 1: 시장 추세 국면]")
        us_regime = gate1.get("US_SP500", {})
        kr_regime = gate1.get("KR_KOSPI", {})
        if us_regime:
            report_lines.append(f" - 미국 S&P 500: {us_regime.get('desc')}")
        if kr_regime:
            report_lines.append(f" - 한국 KOSPI  : {kr_regime.get('desc')}")

        # Short-Term Picks Table
        report_lines.append(f"\n[단기 포착 종목 (Tactical Picks - 1일~2주)]")
        if short_term_picks:
            st_table = []
            for p in short_term_picks:
                st_table.append([
                    p.get("market"),
                    p.get("name"),
                    p.get("ticker"),
                    p.get("score"),
                    p.get("entry_price"),
                    p.get("stop_loss"),
                    p.get("target_price"),
                    f"{p.get('alloc_pct')}%"
                ])
            headers = ["시장", "종목명", "티커", "점수", "진입가", "손절가", "목표가", "비중"]
            report_lines.append(tabulate(st_table, headers=headers, tablefmt="grid"))
        else:
            report_lines.append(" - 현재 단기 조건을 충족하는 유효 돌파 종목 없음 (관망)")

        # Long-Term Picks Table
        report_lines.append(f"\n[중장기 우량 종목 (Strategic Picks - 3개월~1년)]")
        if long_term_picks:
            lt_table = []
            for p in long_term_picks:
                lt_table.append([
                    p.get("market"),
                    p.get("name"),
                    p.get("ticker"),
                    p.get("score"),
                    p.get("entry_price"),
                    p.get("stop_loss"),
                    p.get("target_price"),
                    f"{p.get('alloc_pct')}%"
                ])
            headers = ["시장", "종목명", "티커", "점수", "진입가", "손절가", "목표가", "비중"]
            report_lines.append(tabulate(lt_table, headers=headers, tablefmt="grid"))
        else:
            report_lines.append(" - 현재 중장기 기준을 충족하는 종목 없음")

        report_lines.append("\n" + "=" * 65)

        full_text = "\n".join(report_lines)
        print(full_text)

        # Telegram markdown format
        tg_lines = [
            "*🚀 [Q-TAP] 퀀텀 트레이딩 자동 분석 리포트*",
            f"• *거시 리스크*: {status_kr}",
            f"• *S&P 500*: {us_regime.get('regime', 'N/A')}",
            f"• *KOSPI*: {kr_regime.get('regime', 'N/A')}",
            "",
            "🎯 *단기 추천 종목*:"
        ]
        if short_term_picks:
            for p in short_term_picks[:3]:
                tg_lines.append(f" - *{p['name']}({p['ticker']})*: 진입 {p['entry_price']} | 손절 {p['stop_loss']} | 비중 {p['alloc_pct']}%")
        else:
            tg_lines.append(" - 조건 충족 종목 없음 (관망)")

        tg_lines.append("\n💎 *중장기 추천 종목*:")
        if long_term_picks:
            for p in long_term_picks[:3]:
                tg_lines.append(f" - *{p['name']}({p['ticker']})*: 진입 {p['entry_price']} | 손절 {p['stop_loss']} | 비중 {p['alloc_pct']}%")
        else:
            tg_lines.append(" - 조건 충족 종목 없음")

        self.send_telegram_message("\n".join(tg_lines))
