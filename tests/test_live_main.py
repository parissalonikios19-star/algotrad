import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from live_main import run_live_bot

# ==========================================
# HELPER - creates a fake signals dataframe
# ==========================================
def make_signals(signal_value, days=3):
    """Helper to create a fake signals DataFrame with recent dates."""
    from datetime import datetime, timedelta
    dates = pd.date_range(end=datetime.today().date(), periods=days)
    return pd.DataFrame({
        'Close': [490.0, 495.0, 500.0],
        'Signal': [signal_value] * days
    }, index=dates)


# ==========================================
# CORE TRADING LOGIC TESTS
# ==========================================

@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_buy_order_submitted_and_alert_sent(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Bot should buy, confirm the order, and send an alert."""
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 0.0
    mock_broker.get_buying_power.return_value = 1000.0
    mock_broker.is_market_open.return_value = False
    mock_broker.has_open_trade.return_value = False
    mock_broker.get_portfolio_value.return_value = 10000.0
    mock_broker.get_initial_equity.return_value = 10000.0
    mock_broker.submit_order.return_value = MagicMock(id='order-123')
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    mock_strategy.generate_signals.return_value = make_signals(1.0)

    run_live_bot()

    # Math: $1000 * 0.95 = $950 // $100 = 9 shares
    mock_broker.submit_order.assert_called_once_with('SPY', 9, 'buy')
    mock_broker.confirm_order.assert_called_once_with('order-123')
    mock_send_alert.assert_called_once()


@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_sell_order_submitted_and_alert_sent(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Bot should sell, confirm the order, and send an alert."""
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 15.0
    mock_broker.is_market_open.return_value = False
    mock_broker.get_portfolio_value.return_value = 10000.0
    mock_broker.get_initial_equity.return_value = 10000.0
    mock_broker.submit_order.return_value = MagicMock(id='order-456')
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    mock_strategy.generate_signals.return_value = make_signals(0.0)

    run_live_bot()

    mock_broker.submit_order.assert_called_once_with('SPY', 15.0, 'sell')
    mock_broker.confirm_order.assert_called_once_with('order-456')
    mock_send_alert.assert_called_once()


@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_synced_state_no_order_no_alert(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Bot should do nothing and send no alert when state is synced."""
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 10.0   # IN and signal is BUY — synced
    mock_broker.is_market_open.return_value = False
    mock_broker.get_portfolio_value.return_value = 10000.0
    mock_broker.get_initial_equity.return_value = 10000.0
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    mock_strategy.generate_signals.return_value = make_signals(1.0)

    run_live_bot()

    mock_broker.submit_order.assert_not_called()
    mock_send_alert.assert_not_called()


# ==========================================
# KILL SWITCH TESTS
# ==========================================

@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_kill_switch_halts_and_sends_alert(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Kill switch should halt trading and send an emergency alert."""
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 0.0
    mock_broker.is_market_open.return_value = False
    # Simulate -6% daily loss
    mock_broker.get_portfolio_value.return_value = 9400.0
    mock_broker.get_initial_equity.return_value = 10000.0
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    mock_strategy.generate_signals.return_value = make_signals(1.0)

    run_live_bot()

    # No orders should be placed
    mock_broker.submit_order.assert_not_called()
    # Alert should be sent
    mock_send_alert.assert_called_once()


@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_kill_switch_does_not_trigger_on_small_loss(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Kill switch should NOT trigger on a loss below the threshold."""
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 0.0
    mock_broker.is_market_open.return_value = False
    mock_broker.has_open_trade.return_value = False
    mock_broker.get_buying_power.return_value = 1000.0
    # Simulate -3% daily loss (below threshold)
    mock_broker.get_portfolio_value.return_value = 9700.0
    mock_broker.get_initial_equity.return_value = 10000.0
    mock_broker.submit_order.return_value = MagicMock(id='order-789')
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    mock_strategy.generate_signals.return_value = make_signals(1.0)

    run_live_bot()

    # Bot should still trade normally
    mock_broker.submit_order.assert_called_once()


# ==========================================
# MARKET HOURS GUARD TESTS
# ==========================================

@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_market_open_skips_trading(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Bot should skip all trading if market is currently open."""
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 0.0
    mock_broker.is_market_open.return_value = True   # Market is OPEN
    mock_broker.get_portfolio_value.return_value = 10000.0
    mock_broker.get_initial_equity.return_value = 10000.0
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    mock_strategy.generate_signals.return_value = make_signals(1.0)

    run_live_bot()

    mock_broker.submit_order.assert_not_called()
    mock_send_alert.assert_not_called()


# ==========================================
# DUPLICATE ORDER GUARD TESTS
# ==========================================

@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_open_order_skips_duplicate_buy(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Bot should skip buying if an open order already exists."""
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 0.0
    mock_broker.is_market_open.return_value = False
    mock_broker.has_open_trade.return_value = True   # Open order exists
    mock_broker.get_portfolio_value.return_value = 10000.0
    mock_broker.get_initial_equity.return_value = 10000.0
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value
    mock_strategy.generate_signals.return_value = make_signals(1.0)

    run_live_bot()

    mock_broker.submit_order.assert_not_called()
    mock_send_alert.assert_not_called()


# ==========================================
# DATA STALENESS TESTS
# ==========================================

@patch('live_main.send_alert')
@patch('live_main.AlpacaBroker')
@patch('live_main.DataHandler')
@patch('live_main.MACrossoverStrategy')
def test_stale_data_aborts(mock_strategy_class, mock_handler_class, mock_broker_class, mock_send_alert):
    """Bot should abort if data is more than 5 days old."""
    from datetime import datetime, timedelta
    mock_broker = mock_broker_class.return_value
    mock_broker.get_last_price.return_value = 100.0
    mock_broker.get_position.return_value = 0.0
    mock_handler = mock_handler_class.return_value
    mock_handler.fetch_data.return_value = pd.DataFrame()
    mock_strategy = mock_strategy_class.return_value

    # Create signals with dates from 10 days ago
    old_dates = pd.date_range(end=datetime.today().date() - timedelta(days=10), periods=3)
    stale_signals = pd.DataFrame({
        'Close': [490.0, 495.0, 500.0],
        'Signal': [1.0, 1.0, 1.0]
    }, index=old_dates)
    mock_strategy.generate_signals.return_value = stale_signals

    run_live_bot()

    # Should abort before any trading
    mock_broker.submit_order.assert_not_called()
