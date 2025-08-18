"""
数据工具函数
"""

import pandas as pd
import yfinance as yf

def get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取股票数据
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        股票数据
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        if data.empty:
            print(f"未能获取到 {symbol} 的数据")
            return pd.DataFrame()
        return data
    except Exception as e:
        print(f"获取 {symbol} 数据时出错: {e}")
        return pd.DataFrame()
