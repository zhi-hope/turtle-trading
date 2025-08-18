"""
Unit tests for the Turtle Backtester
"""

import pandas as pd
from turtle_trading_strategy import TurtleTradingStrategy
from turtle_backtest import TurtleBacktester

def test_backtester_run(sample_stock_data):
    """Test the backtester runs without errors and produces results"""
    backtester = TurtleBacktester(
        symbol="TEST",
        start_date="2020-01-01",
        end_date="2020-04-10",
        initial_capital=100000.0,
        commission_rate=0.001,
        slippage=0.0005
    )
    # Manually set data to avoid yfinance call
    backtester.data = sample_stock_data
    
    results = backtester.run_backtest()
    
    assert isinstance(results, dict)
    assert 'final_capital' in results
    assert 'total_return' in results
    assert 'trades' in results
    assert not results['trades'].empty

def test_performance_metrics(sample_stock_data):
    """Test that performance metrics are calculated"""
    backtester = TurtleBacktester(
        symbol="TEST",
        start_date="2020-01-01",
        end_date="2020-04-10",
        initial_capital=100000.0
    )
    backtester.data = sample_stock_data
    backtester.run_backtest() # Run backtest to generate results
    
    metrics = backtester.get_performance_metrics()
    
    assert isinstance(metrics, dict)
    assert '总收益率(%)' in metrics
    assert '最大回撤(%)' in metrics
    assert '夏普比率' in metrics
    assert '索提诺比率' in metrics
    assert '卡玛比率' in metrics
    assert metrics['总交易次数'] > 0

def test_commission_and_slippage(sample_stock_data):
    """Test that commission and slippage affect profits"""
    # Backtest without costs
    backtester_no_cost = TurtleBacktester(
        symbol="TEST",
        start_date="2020-01-01",
        end_date="2020-04-10",
        initial_capital=100000.0,
        commission_rate=0.0,
        slippage=0.0
    )
    backtester_no_cost.data = sample_stock_data
    results_no_cost = backtester_no_cost.run_backtest()
    profit_no_cost = results_no_cost['trades']['Profit'].sum()

    # Backtest with costs
    backtester_with_cost = TurtleBacktester(
        symbol="TEST",
        start_date="2020-01-01",
        end_date="2020-04-10",
        initial_capital=100000.0,
        commission_rate=0.001, # 0.1%
        slippage=0.0005 # 0.05%
    )
    backtester_with_cost.data = sample_stock_data
    results_with_cost = backtester_with_cost.run_backtest()
    profit_with_cost = results_with_cost['trades']['Profit'].sum()

    assert profit_with_cost < profit_no_cost
