import pytest
import pandas as pd
import numpy as np
from src.data_handler import DataHandler

def test_clean_data_negative_prices():
    handler = DataHandler("SPY", "2020-01-01", "2021-01-01")
    
    # Create 250 days of fake data where the price eventually drops below zero
    dates = pd.date_range(start='2020-01-01', periods=250)
    prices = np.linspace(100, -10, 250) 
    bad_data = pd.DataFrame({'Close': prices}, index=dates)
    
    # The test passes if the DataHandler correctly raises a ValueError
    with pytest.raises(ValueError, match="zero or negative prices"):
        handler._clean_data(bad_data)

def test_clean_data_insufficient_length():
    handler = DataHandler("SPY", "2020-01-01", "2021-01-01")
    
    # Create only 50 days of data (Strategy needs 200)
    dates = pd.date_range(start='2020-01-01', periods=50)
    prices = np.linspace(100, 110, 50)
    short_data = pd.DataFrame({'Close': prices}, index=dates)
    
    with pytest.raises(ValueError, match="Need at least 200"):
        handler._clean_data(short_data)