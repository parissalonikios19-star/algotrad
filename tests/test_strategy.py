import pytest
import pandas as pd
import numpy as np
from src.strategy import MACrossoverStrategy

def test_strategy_parameter_validation():
    # TEST 1: The bot should instantly crash if short window is larger than long window.
    # We use pytest.raises to tell the tester: "Expect a ValueError here. If it happens, we pass."
    with pytest.raises(ValueError , match="must be less than"):
        _ = MACrossoverStrategy(short_window=200, long_window=50)

def test_strategy_generates_correct_columns():
    # TEST 2: The bot should output a DataFrame with the correct contract columns.
    
    # 1. Create fake minimal data
    dates = pd.date_range(start='2020-01-01', periods=250)
    prices = np.linspace(100, 150, 250) 
    fake_data = pd.DataFrame({'Close': prices}, index=dates)
    
    # 2. Run the strategy
    strategy = MACrossoverStrategy(short_window=50, long_window=200)
    result = strategy.generate_signals(fake_data)
    
    # 3. Assert (Check) that the contract is fulfilled
    assert 'Signal' in result.columns
    assert 'SMA_Short' in result.columns
    assert 'SMA_Long' in result.columns