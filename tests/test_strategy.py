"""
Unit tests for the Turtle Trading Strategy
"""

import pandas as pd

from src.turtle_trading_strategy import TurtleTradingStrategy

def test_calculate_donchian_channels(sample_stock_data):
    """Test Donchian Channel calculation"""
    strategy = TurtleTradingStrategy(entry_window=20)
    data = strategy.calculate_donchian_channels(sample_stock_data, window=20)
    
    assert 'Donchian_High' in data.columns
    assert 'Donchian_Low' in data.columns
    assert not data['Donchian_High'].isnull().all()
    assert not data['Donchian_Low'].isnull().all()
    
    # The first 19 values should be NaN
    assert data['Donchian_High'].iloc[:19].isnull().all()
    # Check a specific value
    assert data['Donchian_High'].iloc[19] == sample_stock_data['High'].iloc[:20].max()
    assert data['Donchian_Low'].iloc[19] == sample_stock_data['Low'].iloc[:20].min()

def test_calculate_atr(sample_stock_data):
    """Test ATR calculation"""
    strategy = TurtleTradingStrategy(atr_window=20)
    atr = strategy.calculate_atr(sample_stock_data, window=20)
    
    assert isinstance(atr, pd.Series)
    assert not atr.isnull().all()
    # The first 19 values should be NaN
    assert atr.iloc[:19].isnull().all()
    # Check that ATR is positive
    assert (atr.dropna() > 0).all()

def test_calculate_position_size(sample_stock_data):
    """Test position size calculation"""
    strategy = TurtleTradingStrategy(risk_percent=0.01)
    data = sample_stock_data.copy()
    data['ATR'] = strategy.calculate_atr(data, window=20)
    data = data.dropna()
    
    sized_data = strategy.calculate_position_size(data, account_value=100000, contract_size=1.0)
    
    assert 'Position_Size' in sized_data.columns
    assert not sized_data['Position_Size'].isnull().all()
    assert (sized_data['Position_Size'] > 0).all()
    
    # Check calculation for a specific row
    account_value = 100000
    risk_percent = 0.01
    atr = sized_data['ATR'].iloc[0]
    expected_size = (account_value * risk_percent) / atr
    assert sized_data['Position_Size'].iloc[0] == expected_size
