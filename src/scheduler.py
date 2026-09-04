import time
import schedule
import logging
from datetime import datetime
from main import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Scheduler] %(message)s"
)
logger = logging.getLogger("Scheduler")

def job_us_close():
    logger.info("Triggering 06:30 US Market Close Analysis Job...")
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Error executing US close job: {e}")

def job_kr_premarket():
    logger.info("Triggering 08:30 KR Pre-Market Analysis Job...")
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Error executing KR pre-market job: {e}")

def start_scheduler():
    logger.info("Q-TAP Automated Daemon Scheduler Started.")
    logger.info("Registered Schedule: [06:30 US Close Analysis] & [08:30 KR Pre-Market Analysis]")

    # 1. Daily 06:30 (After US Market Closes)
    schedule.every().day.at("06:30").do(job_us_close)

    # 2. Daily 08:30 (Before Korean Market Opens)
    schedule.every().day.at("08:30").do(job_kr_premarket)

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    start_scheduler()
