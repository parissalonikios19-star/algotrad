import pytest
import pandas as pd
from src.portfolio import Portfolio

def test_portfolio_missing_columns():
    port = Portfolio(initial_capital=10000.0)
    
    # Give it a DataFrame without 'Close' or 'Signal'
    bad_data = pd.DataFrame({'Price': [100, 101, 102]}) 
    
    with pytest.raises(KeyError, match="Missing required column"):
        port.backtest(bad_data)

def test_portfolio_state_syncing():
    port = Portfolio(initial_capital=1000.0)
    
    # Fake 3 days of market action
    # Day 1: Math generates a 'Buy' (1.0)
    # Day 2: Math generates a 'Sell' (0.0)
    # Day 3: Math stays flat (0.0)
    data = pd.DataFrame({
        'Close': [100.0, 100.0, 100.0],
        'Signal': [1.0, 0.0, 0.0] 
    })
    
    results = port.backtest(data)
    
    # Because our bot shifts the signal by 1 day to prevent time-travel:
    # Day 1 (index 0) execution: Looks at Day 0 signal (NaN) -> Stays in Cash (Shares == 0)
    # Day 2 (index 1) execution: Looks at Day 1 signal (1.0) -> Buys (Shares > 0)
    # Day 3 (index 2) execution: Looks at Day 2 signal (0.0) -> Sells (Shares == 0)
    
    assert results['Shares'].iloc[0] == 0.0
    assert results['Shares'].iloc[1] > 0.0
    assert results['Shares'].iloc[2] == 0.0