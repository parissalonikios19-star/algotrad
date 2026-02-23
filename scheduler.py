import os 
import time
import schedule
import logging
from live_main import run_live_bot
import pytz
from datetime import datetime

# create a "logs" folder if doesnt already exist
os.makedirs("logs", exist_ok=True)
# dual logging , terminal and file
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler("logs/trading.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# set time
LOCAL_TZ = pytz.timezone("Europe/Athens")
RUN_TIME_LOCAL = "22:45"

# Convert 22:45 Athens time to UTC dynamically (handles daylight saving)
def get_utc_run_time():
    today = datetime.now(LOCAL_TZ).date()
    local_dt = LOCAL_TZ.localize(datetime.strptime(f"{today} {RUN_TIME_LOCAL}", "%Y-%m-%d %H:%M"))
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime("%H:%M")

def trading_job():
    logger.info("[*] ALARM CLOCK: Waking up the trading bot...")
    try:
        run_live_bot()
    except Exception as e:
        logger.error(f"[!] Bot failed during scheduled run: {e}")
    logger.info("[*] ALARM CLOCK: Bot finished. Going back to sleep.")

# Use UTC mode on server, local time for testing
if os.getenv("USE_UTC", "false").lower() == "true":
    utc_run_time = get_utc_run_time()
    logger.info(f"[*] UTC mode: scheduling at {utc_run_time} UTC ({RUN_TIME_LOCAL} Athens time)")
else:
    utc_run_time = RUN_TIME_LOCAL
    logger.info(f"[*] Local mode: scheduling at {utc_run_time} local time")

schedule.every().monday.at(utc_run_time).do(trading_job)
schedule.every().tuesday.at(utc_run_time).do(trading_job)
schedule.every().wednesday.at(utc_run_time).do(trading_job)
schedule.every().thursday.at(utc_run_time).do(trading_job)
schedule.every().friday.at(utc_run_time).do(trading_job)

if __name__ == "__main__":
    logger.info("[*] Scheduler initialized. Waiting for the next trading window...")
    
    # The Infinite Loop
    while True:
        schedule.run_pending()
        # Sleep for 60 seconds so we don't fry your CPU constantly checking the time
        time.sleep(60)