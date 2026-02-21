import os 
import time
import schedule
import logging
from live_main import run_live_bot

# create a "logs" folder if doesnt already exist
os.makedirs("logs", exist_ok=True)
# dual logging , terminal and file
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler("logs/trading.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def trading_job():
    logger.info("[*] ALARM CLOCK: Waking up the trading bot...")
    try:
        run_live_bot()
    except Exception as e:
        logger.error(f"[!] Bot failed during scheduled run: {e}")
    logger.info("[*] ALARM CLOCK: Bot finished. Going back to sleep.")

# Runs at 22:45 local machine time. Adjust if deploying to a server in a different timezone.
schedule.every().monday.at("22:45").do(trading_job)
schedule.every().tuesday.at("22:45").do(trading_job)
schedule.every().wednesday.at("22:45").do(trading_job)
schedule.every().thursday.at("22:45").do(trading_job)
schedule.every().friday.at("22:45").do(trading_job)

if __name__ == "__main__":
    logger.info("[*] Scheduler initialized. Waiting for the next trading window...")
    
    # The Infinite Loop
    while True:
        schedule.run_pending()
        # Sleep for 60 seconds so we don't fry your CPU constantly checking the time
        time.sleep(60)