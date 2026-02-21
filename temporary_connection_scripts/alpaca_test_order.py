import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

api = tradeapi.REST(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY"),
    os.getenv("ALPACA_BASE_URL")
)

# Submit a paper buy order for 1 share of SPY
order = api.submit_order(
    symbol='SPY',
    qty=1,
    side='buy',
    type='market',
    time_in_force='day'
)

print(f"Order submitted!")
print(f"Order ID:  {order.id}")
print(f"Symbol:    {order.symbol}")
print(f"Side:      {order.side}")
print(f"Qty:       {order.qty}")
print(f"Status:    {order.status}")