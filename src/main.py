"""
海龟交易法完整示例程序
"""

import pandas as pd
from turtle_trading_strategy import TurtleTradingStrategy
from turtle_backtest import TurtleBacktester
from data_utils import get_stock_data

def main():
    # 设置参数 - 通过用户输入
    print("请输入回测参数:")
    symbol_input = input("股票代码，多个股票请用逗号分隔 (例如: AAPL,GOOGL,TSLA): ") or "AAPL"
    symbols = [s.strip() for s in symbol_input.split(',')] if ',' in symbol_input else [symbol_input.strip()]
    
    start_date = input("开始日期 (YYYY-MM-DD): ") or "2020-01-01"
    end_date = input("结束日期 (YYYY-MM-DD): ") or "2023-12-31"
    
    initial_capital_input = input("初始资金 (默认 100000.0): ")
    initial_capital = float(initial_capital_input) if initial_capital_input else 100000.0
    
    commission_input = input("手续费率 (默认 0.001): ")
    commission = float(commission_input) if commission_input else 0.001

    slippage_input = input("滑点 (默认 0.001): ")
    slippage = float(slippage_input) if slippage_input else 0.001
    
    print("海龟交易策略示例")
    print("=" * 50)
    
    # 方法1: 直接使用策略生成信号
    print("\n1. 策略信号生成示例:")
    # 处理多股票情况
    if len(symbols) > 1:
        from data_utils import get_multiple_stocks_data
        data_dict = get_multiple_stocks_data(symbols, start_date, end_date)
        
        for symbol, data in data_dict.items():
            if not data.empty:
                # 创建策略实例
                strategy = TurtleTradingStrategy(
                    entry_window=20,      # 入场窗口
                    exit_window=10,       # 出场窗口
                    atr_window=20,        # ATR计算窗口
                    atr_multiplier=2.0,   # ATR止损倍数
                    risk_percent=0.01     # 账户风险百分比
                )
                
                # 运行策略
                results = strategy.run_strategy(data, initial_capital)
                
                # 显示最后10条记录
                print(f"\n{symbol} 最后10条策略信号:")
                print(results[['Close', 'Donchian_High', 'Donchian_Low', 'Signal', 'Position_Size', 'Entry_Price', 'Stop_Loss']].tail(10))
    else:
        symbol = symbols[0]
        data = get_stock_data(symbol, start_date, end_date)
        if not data.empty:
            # 创建策略实例
            strategy = TurtleTradingStrategy(
                entry_window=20,      # 入场窗口
                exit_window=10,       # 出场窗口
                atr_window=20,        # ATR计算窗口
                atr_multiplier=2.0,   # ATR止损倍数
                risk_percent=0.01     # 账户风险百分比
            )
            
            # 运行策略
            results = strategy.run_strategy(data, initial_capital)
            
            # 显示最后10条记录
            print(f"\n{symbol} 最后10条策略信号:")
            print(results[['Close', 'Donchian_High', 'Donchian_Low', 'Signal', 'Position_Size', 'Entry_Price', 'Stop_Loss']].tail(10))
    
    # 方法2: 使用回测引擎进行完整回测
    print("\n\n2. 策略回测示例:")
    # 处理多股票情况
    if len(symbols) > 1:
        backtester = TurtleBacktester(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            commission_rate=commission,
            slippage=slippage,
            contract_size=1.0
        )
    else:
        backtester = TurtleBacktester(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            commission_rate=commission,
            slippage=slippage,
            contract_size=1.0
        )
    
    # 运行回测
    backtest_results = backtester.run_backtest()
    
    # 获取绩效指标
    metrics = backtester.get_performance_metrics()
    
    # 显示回测结果
    if metrics:
        # 处理多股票情况
        if len(symbols) > 1:
            print(f"\n多股票海龟交易策略回测结果")
            print("=" * 50)
            for symbol, symbol_metrics in metrics.items():
                print(f"\n{symbol} 回测结果:")
                print("-" * 30)
                for key, value in symbol_metrics.items():
                    if isinstance(value, float):
                        print(f"{key}: {value:.2f}")
                    else:
                        print(f"{key}: {value}")
        else:
            print(f"\n{symbol} 海龟交易策略回测结果")
            print("=" * 50)
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
    
    # 显示交易记录
    if len(symbols) > 1:
        # 处理多股票交易记录
        for symbol, result in backtest_results.items():
            trades = result.get('trades', pd.DataFrame())
            if not trades.empty:
                print(f"\n{symbol} 交易记录 (显示前10条):")
                print(trades.head(10))
    else:
        trades = backtest_results.get('trades', pd.DataFrame())
        if not trades.empty:
            print(f"\n交易记录 (显示前10条):")
            print(trades.head(10))
    
    print("\n示例程序执行完成!")

if __name__ == "__main__":
    main()