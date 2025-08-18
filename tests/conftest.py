"""
Pytest configuration and fixtures
"""

import pytest
import pandas as pd
import numpy as np

@pytest.fixture(scope='session')
def sample_stock_data() -> pd.DataFrame:
    """Creates a sample DataFrame for testing"""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Generate a predictable price series
    price = 100
    prices = [price]
    returns = np.random.normal(0.001, 0.02, 99)
    for r in returns:
        price *= (1 + r)
        prices.append(price)
    
    data = pd.DataFrame(
        {
            'Open': np.array(prices) * 0.99,
            'High': np.array(prices) * 1.02,
            'Low': np.array(prices) * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1_000_000, 2_000_000, size=100)
        },
        index=dates
    )
    # Ensure High is the max and Low is the min
    data['High'] = data[['Open', 'High', 'Close']].max(axis=1)
    data['Low'] = data[['Open', 'Low', 'Close']].min(axis=1)
    
    return data
