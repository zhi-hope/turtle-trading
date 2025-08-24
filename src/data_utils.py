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

def get_multiple_stocks_data(symbols: list, start_date: str, end_date: str) -> dict:
    """
    获取多个股票的数据
    
    Args:
        symbols: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        股票数据字典
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    
    data_dict = {}
    lock = threading.Lock()
    
    def fetch_single_stock(symbol):
        data = get_stock_data(symbol, start_date, end_date)
        if not data.empty:
            with lock:
                data_dict[symbol] = data
    
    # 使用线程池并行获取数据
    with ThreadPoolExecutor(max_workers=min(len(symbols), 10)) as executor:
        futures = [executor.submit(fetch_single_stock, symbol) for symbol in symbols]
        for future in as_completed(futures):
            future.result()  # 等待任务完成
    
    return data_dict
