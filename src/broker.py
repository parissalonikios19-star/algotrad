import os
import logging
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import time

logger = logging.getLogger(__name__)

class AlpacaBroker:

    def __init__(self):
        load_dotenv()
        
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        base_url = os.getenv("ALPACA_BASE_URL")

        if not api_key or not secret_key:
            raise ValueError("[!] Missing Alpaca API keys. Check your .env file.")
        
        self.api = tradeapi.REST(api_key , secret_key , base_url)

        self._validate_keys()

    # checks that api keys are valid
    def _validate_keys(self):
        logger.info("[*] Validating API keys with Alpaca...")
        try:
            # If the keys are bad, this specific line will trigger an exception
            account = self.api.get_account()
            logger.info(f"[*] Keys valid! Account Status: {account.status}")
        except Exception as e:
            # We use a PermissionError to clearly state it's an access issue
            raise PermissionError(f"[!] API Key Validation Failed. Are your keys correct? Error: {e}")

    # get accounts buying power
    def get_buying_power(self):
        account = self.api.get_account()
        return float(account.buying_power)
    
    # get latest price of a ticker
    def get_last_price(self , ticker):
        return float(self.api.get_latest_trade(ticker).price)

    # checks if there is an open position , (trade on weekends stays open while market is closed)
    def has_open_trade(self , ticker):
        orders = self.api.list_orders(status='open', symbols=[ticker])
        return len(orders)>0
    
    # checks if market is currently open
    def is_market_open(self):
        clock = self.api.get_clock()
        return clock.is_open
    
    # checks if order has gone through
    def confirm_order(self , order_id ,wait_seconds=5):
        time.sleep(wait_seconds)
        order = self.api.get_order(order_id)
        logger.info(f"[*] Order confirmation — Status: {order.status}")
        if order.status not in ['filled', 'partially_filled', 'accepted', 'pending_new']:
            logger.warning(f"[!] Order {order_id} has unexpected status: {order.status}")
        return order.status

    # checks how much of 'ticker' the portfolio owns
    def get_position(self , ticker):
        try:
            position = self.api.get_position(ticker)
            return float(position.qty)
        except tradeapi.rest.APIError as e:
            # Alpaca throws an error if you have 0 shares of a stock. We catch it and return 0.
            if 'does not exist' in str(e):
                return 0.0
            raise e
        
    # executes live trade , buy or sell
    def submit_order(self , ticker , quantity , side):
        logger.info(f"[*] Submitting {side.upper()} order for {quantity} shares of {ticker}...")
        try:
            order = self.api.submit_order(
                symbol=ticker,
                qty=quantity,
                side=side,
                type='market',
                time_in_force='day' # if not comlpeted in the same day , reject it
            )
            logger.info(f"[*] Order submitted successfully! Status: {order.status}")
            return order
        except Exception as e:
            logger.error(f"[!] Failed to submit order: {e}")
            return None
        
    # calculates portfolio value
    def get_portfolio_value(self):
        account = self.api.get_account()
        return float(account.portfolio_value)
    
    # equity at last days close
    def get_initial_equity(self):
        account = self.api.get_account()
        return float(account.last_equity)