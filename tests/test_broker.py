import pytest
from unittest.mock import patch, MagicMock
from src.broker import AlpacaBroker
import alpaca_trade_api as tradeapi

# @patch intercepts the tools our broker uses so they don't hit the real internet
@patch('src.broker.tradeapi.REST')
@patch('src.broker.os.getenv')
def test_broker_gets_position(mock_getenv, mock_rest_class):
    # 1. Provide fake API keys so the __init__ doesn't crash
    mock_getenv.return_value = "FAKE_KEY"
    
    # 2. Create a fake Alpaca server instance
    mock_api_instance = mock_rest_class.return_value
    
    # 3. Fake the 'fail fast' account validation response
    mock_api_instance.get_account.return_value.status = "ACTIVE"
    
    # 4. Fake the position response (Alpaca returns share quantities as strings)
    mock_position = MagicMock()
    mock_position.qty = "15.0"
    mock_api_instance.get_position.return_value = mock_position
    
    # --- ACT ---
    broker = AlpacaBroker()
    shares = broker.get_position("SPY")
    
    # --- ASSERT ---
    # Verify the broker successfully translated the string "15.0" into a float 15.0
    assert shares == 15.0
    # Verify the broker actually asked Alpaca for 'SPY' specifically
    mock_api_instance.get_position.assert_called_with("SPY")

@patch('src.broker.tradeapi.REST')
@patch('src.broker.os.getenv')
def test_broker_returns_zero_for_no_position(mock_getenv, mock_rest_class):
    mock_getenv.return_value = "FAKE_KEY"
    mock_api_instance = mock_rest_class.return_value
    mock_api_instance.get_account.return_value.status = "ACTIVE"
    
    # Simulate Alpaca throwing an APIError for no position
    mock_api_instance.get_position.side_effect = tradeapi.rest.APIError({"message": "position does not exist"})
    
    broker = AlpacaBroker()
    shares = broker.get_position("SPY")
    
    assert shares == 0.0

@patch('src.broker.tradeapi.REST')
@patch('src.broker.os.getenv')
def test_broker_raises_on_missing_keys(mock_getenv, mock_rest_class):
    mock_getenv.return_value = None
    with pytest.raises(ValueError, match="Missing Alpaca API keys"):
        AlpacaBroker()