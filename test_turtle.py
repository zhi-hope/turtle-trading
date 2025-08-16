"""
海龟交易法测试程序（使用模拟数据）
"""

import pandas as pd
import numpy as np
from turtle_trading_strategy import TurtleTradingStrategy
from turtle_backtest import TurtleBacktester

def create_sample_data():
    """创建示例数据用于测试"""
    # 创建一个简单的模拟价格数据
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    np.random.seed(42)  # 固定随机种子以确保结果可重现
    
    # 生成随机游走价格数据
    returns = np.random.normal(0.001, 0.02, 100)  # 日收益率均值0.1%，标准差2%
    price = 100  # 初始价格
    prices = [price]
    
    for r in returns[1:]:
        price = price * (1 + r)
        prices.append(price)
    
    # 创建DataFrame
    data = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'Close': prices,
        'Volume': [np.random.randint(1000000, 2000000) for _ in range(100)]
    }, index=dates)
    
    # 确保High >= Open, Close and Low <= Open, Close
    data['High'] = np.maximum.reduce([data['High'], data['Open'], data['Close']])
    data['Low'] = np.minimum.reduce([data['Low'], data['Open'], data['Close']])
    
    return data

def main():
    # 创建模拟数据
    data = create_sample_data()
    
    print("海龟交易策略测试")
    print("=" * 50)
    print(f"数据日期范围: {data.index[0].date()} 到 {data.index[-1].date()}")
    print(f"数据点数量: {len(data)}")
    print(f"起始价格: {data['Close'].iloc[0]:.2f}")
    print(f"结束价格: {data['Close'].iloc[-1]:.2f}")
    
    # 测试策略信号生成
    print("\n1. 策略信号生成测试:")
    strategy = TurtleTradingStrategy(
        entry_window=20,      # 入场窗口
        exit_window=10,       # 出场窗口
        atr_window=20,        # ATR计算窗口
        atr_multiplier=2.0,   # ATR止损倍数
        risk_percent=0.01     # 账户风险百分比
    )
    
    # 运行策略
    results = strategy.run_strategy(data, 100000.0)
    
    # 显示最后10条记录
    print("\n最后10条策略信号:")
    print(results[['Close', 'Donchian_High', 'Donchian_Low', 'Signal', 'Position_Size']].tail(10))
    
    # 统计信号
    long_signals = len(results[results['Signal'] == 1])
    short_signals = len(results[results['Signal'] == -1])
    total_signals = long_signals + short_signals
    
    print(f"\n信号统计:")
    print(f"  多头信号: {long_signals}")
    print(f"  空头信号: {short_signals}")
    print(f"  总信号数: {total_signals}")
    
    # 测试回测引擎
    print("\n\n2. 回测引擎测试:")
    
    # 为了测试回测引擎，我们需要模拟TurtleBacktester的行为
    # 但不实际调用yfinance
    
    # 直接使用我们已有的数据和结果
    trades = []
    position = 0
    entry_price = 0.0
    entry_date = None
    
    for i, (date, row) in enumerate(results.iterrows()):
        signal = row['Signal']
        close_price = row['Close']
        position_size = row['Position_Size']
        
        # 如果有信号且与当前持仓方向相反，则平仓
        if position != 0 and (
            (position > 0 and signal == -1) or  # 多头持仓，收到平仓/反向信号
            (position < 0 and signal == 1)      # 空头持仓，收到平仓/反向信号
        ):
            # 记录平仓交易
            exit_price = close_price
            profit = (exit_price - entry_price) * position
            trades.append({
                'Entry_Date': entry_date,
                'Exit_Date': date,
                'Entry_Price': entry_price,
                'Exit_Price': exit_price,
                'Position': position,
                'Profit': profit,
                'Return': (exit_price / entry_price - 1) * 100 if position > 0 else (entry_price / exit_price - 1) * 100
            })
            
            # 重置持仓
            position = 0
            entry_price = 0.0
            entry_date = None
        
        # 如果无持仓且有入场信号，则开仓
        if position == 0 and signal != 0:
            # 确定新持仓方向
            new_position = position_size if signal == 1 else -position_size
            position = new_position
            entry_price = close_price
            entry_date = date
    
    # 如果还有未平仓的仓位，在最后一天平仓
    if position != 0 and entry_date is not None:
        last_date = results.index[-1]
        last_price = results['Close'].iloc[-1]
        profit = (last_price - entry_price) * position
        trades.append({
            'Entry_Date': entry_date,
            'Exit_Date': last_date,
            'Entry_Price': entry_price,
            'Exit_Price': last_price,
            'Position': position,
            'Profit': profit,
            'Return': (last_price / entry_price - 1) * 100 if position > 0 else (entry_price / last_price - 1) * 100
        })
    
    trades_df = pd.DataFrame(trades)
    
    print(f"\n交易记录:")
    if not trades_df.empty:
        print(trades_df)
        print(f"\n交易统计:")
        print(f"  总交易次数: {len(trades_df)}")
        print(f"  盈利交易数: {len(trades_df[trades_df['Profit'] > 0])}")
        print(f"  亏损交易数: {len(trades_df[trades_df['Profit'] < 0])}")
        print(f"  总利润: {trades_df['Profit'].sum():.2f}")
        print(f"  平均利润: {trades_df['Profit'].mean():.2f}")
    else:
        print("  没有产生交易")
    
    print("\n测试程序执行完成!")

if __name__ == "__main__":
    main()
