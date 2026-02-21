import pytest
import pandas as pd
from unittest.mock import patch
from live_main import run_live_bot

# We patch the imports exactly where they are used inside live_main.py
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_live_bot_submits_buy_order(mock_strategy_class, mock_handler_class, mock_broker_class):
    # 1. SETUP THE FAKE BROKER
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 0.0      # We own 0 shares (We are OUT)
    mock_broker.get_buying_power.return_value = 1000.0 # We have $1,000 to spend
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    
    # 2. SETUP THE FAKE STRATEGY
    mock_strategy = mock_strategy_class.return_value
    # Create a fake signals dataframe where yesterday's signal (iloc[-2]) is 1.0 (BUY)
    fake_signals = pd.DataFrame({'Close': [490.0, 495.0, 500.0], 'Signal': [0.0, 1.0, 1.0]})
    mock_strategy.generate_signals.return_value = fake_signals
    
    # 3. RUN THE BOT
    run_live_bot()
    
    # 4. VERIFY THE DECISION
    # Math: $1000 * 0.95 (buffer) = $950. $950 // $100 price = 9 shares
    mock_broker.submit_order.assert_called_once_with('SPY', 9, 'buy')


@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_live_bot_submits_sell_order(mock_strategy_class, mock_handler_class, mock_broker_class):
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 15.0     # We own 15 shares (We are IN)
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()   
    
    mock_strategy = mock_strategy_class.return_value
    # iloc[-2] is 0.0 (SELL)
    fake_signals = pd.DataFrame({'Close': [490.0, 495.0, 500.0],'Signal': [1.0, 0.0, 0.0]}) 
    mock_strategy.generate_signals.return_value = fake_signals
    
    run_live_bot()
    
    mock_broker.submit_order.assert_called_once_with('SPY', 15.0, 'sell')


@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_live_bot_stays_synced(mock_strategy_class, mock_handler_class, mock_broker_class):
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 10.0     # We own 10 shares (We are IN)
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    # iloc[-2] is 1.0 (BUY/HOLD)
    fake_signals = pd.DataFrame({'Close': [490.0, 495.0, 500.0],'Signal': [0.0, 1.0, 1.0]}) 
    mock_strategy.generate_signals.return_value = fake_signals
    
    run_live_bot()
    
    # VERIFY THE DECISION: State is synced, so it should NOT submit any orders
    mock_broker.submit_order.assert_not_called()