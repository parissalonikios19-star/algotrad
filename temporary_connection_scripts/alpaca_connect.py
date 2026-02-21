import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

api = tradeapi.REST(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY"),
    os.getenv("ALPACA_BASE_URL")
)

account = api.get_account()
print(f"Account status: {account.status}")
print(f"Buying power:   ${float(account.buying_power):,.2f}")
print(f"Portfolio value: ${float(account.portfolio_value):,.2f}")