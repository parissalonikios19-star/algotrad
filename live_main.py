import os
import logging
from datetime import datetime , timedelta
from src.data_handler import DataHandler
from src.strategy import MACrossoverStrategy
from src.broker import AlpacaBroker

# dual logging , terminal and file
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler("logs/trading.log"), logging.StreamHandler()]
    )
logger = logging.getLogger(__name__)

def run_live_bot():
    TICKER = 'SPY'
    CASH_BUFFER = 0.95
    MAX_DAILY_LOSS_PCT = -5.0

    # need at least 250 days (300 to be sure) to have 200 days worth of data
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=300)).strftime('%Y-%m-%d')

    logger.info(f"=== Waking up Live Bot for {TICKER} ===")

    # initialize 
    broker = AlpacaBroker()
    handler = DataHandler(TICKER , start_date= start_date , end_date= end_date)
    strategy = MACrossoverStrategy(short_window= 50 , long_window= 200)

    # fetch data and generate signals
    raw_data = handler.fetch_data()
    signals = strategy.generate_signals(raw_data)

    # confirm we have enough recent data
    last_data_date = signals.index[-1].date()
    today = datetime.today().date()
    days_gap = (today - last_data_date).days
    # not enough data , for example public holidays
    if days_gap > 5:
        logger.error(f"[!] Data appears stale — last date is {last_data_date}. Aborting.")
        return
    # small data gap
    if days_gap > 1:
        logger.warning(f"[!] Possible holiday gap — last data date is {last_data_date}.")
        
    target_signal = signals['Signal'].iloc[-2]  # yesterdays confirmed signal
    last_price = broker.get_last_price(TICKER)

    logger.info(f"[*] Current Price: ${last_price:.2f}")
    logger.info(f"[*] Target Signal: {'BUY/HOLD (1.0)' if target_signal == 1.0 else 'SELL/CASH (0.0)'}")

    current_shares = broker.get_position(TICKER)
    logger.info(f"[*] Actual Shares Owned: {current_shares}")

    # algorithm is designed to trade when market is closed
    if broker.is_market_open():
        logger.warning("[!] Market is currently open. Bot is designed to run after close. Skipping to avoid live execution.")
        return
    
    # EMERGENCY EXIT — halt if daily loss exceeds 5%
    portfolio_value = broker.get_portfolio_value()
    initial_equity = broker.get_initial_equity()
    daily_loss_pct = ((portfolio_value - initial_equity) / initial_equity) * 100

    if daily_loss_pct < MAX_DAILY_LOSS_PCT:
        logger.critical(f"[!!!] EMERGENCY EXIT TRIGGERED. Daily loss: {daily_loss_pct:.2f}%. Bot halting.")
        return

    if target_signal == 1.0 and current_shares == 0:
        
        # if there is an open position ,  wait until it has gone through
        if broker.has_open_trade(TICKER):
             logger.info("[*] Open order already exists . Skipping to avoid duplicate buy.")
        else:

            logger.info("[*] MISMATCH: Strategy wants IN, but we are OUT. Buying...")
        
            # Calculate how many shares we can afford
            buying_power = broker.get_buying_power()
        
            # Leave a cash buffer to account for slippage/market fluctuations
            investable_cash = buying_power * CASH_BUFFER
            qty = int(investable_cash // last_price)
        
            if qty > 0:
                order = broker.submit_order(TICKER, qty, 'buy')
                if order:
                    broker.confirm_order(order.id)
            else:
                logger.warning("[!] Insufficient funds to buy 1 share.")

    elif target_signal == 0.0 and current_shares > 0:
        logger.info("[*] MISMATCH: Strategy wants OUT, but we are IN. Liquidating...")
        order = broker.submit_order(TICKER, current_shares, 'sell')
        if order:
            broker.confirm_order(order.id)
    else:
        logger.info("[*] State is perfectly synced. No action required today.")
        
    logger.info("=== Bot going back to sleep ===")




if __name__ == "__main__":
    try:
        run_live_bot()
    except Exception as e:
        logger.error(f"Live bot encountered a fatal error: {e}")