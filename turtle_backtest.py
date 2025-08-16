"""
海龟交易策略回测引擎
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from turtle_trading_strategy import TurtleTradingStrategy, get_stock_data


class TurtleBacktester:
    def __init__(self, 
                 symbol: str,
                 start_date: str,
                 end_date: str,
                 initial_capital: float = 100000.0,
                 contract_size: float = 1.0):
        """
        初始化回测引擎
        
        Args:
            symbol: 交易标的代码
            start_date: 回测开始日期
            end_date: 回测结束日期
            initial_capital: 初始资金
            contract_size: 合约乘数
        """
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.contract_size = contract_size
        self.data = None
        self.strategy = None
        self.results = None
        
    def load_data(self) -> bool:
        """
        加载数据
        
        Returns:
            是否成功加载数据
        """
        self.data = get_stock_data(self.symbol, self.start_date, self.end_date)
        return not self.data.empty
    
    def setup_strategy(self, **kwargs):
        """
        设置策略参数
        
        Args:
            **kwargs: 策略参数
        """
        self.strategy = TurtleTradingStrategy(**kwargs)
    
    def run_backtest(self) -> Dict:
        """
        运行回测
        
        Returns:
            回测结果
        """
        if self.data is None:
            if not self.load_data():
                return {}
        
        if self.strategy is None:
            self.setup_strategy()
        
        # 运行策略
        strategy_results = self.strategy.run_strategy(
            self.data, 
            self.initial_capital, 
            self.contract_size
        )
        
        # 计算交易记录
        trades = self._calculate_trades(strategy_results)
        
        # 计算账户权益
        equity_curve = self._calculate_equity_curve(trades, strategy_results)
        
        # 合并结果
        self.results = pd.concat([strategy_results, equity_curve], axis=1)
        
        return {
            'symbol': self.symbol,
            'initial_capital': self.initial_capital,
            'final_capital': equity_curve['Equity'].iloc[-1] if not equity_curve.empty else self.initial_capital,
            'total_return': (equity_curve['Equity'].iloc[-1] / self.initial_capital - 1) * 100 if not equity_curve.empty else 0,
            'trades': trades,
            'equity_curve': equity_curve,
            'strategy_results': strategy_results
        }
    
    def _calculate_trades(self, strategy_results: pd.DataFrame) -> pd.DataFrame:
        """
        根据策略信号计算交易记录
        
        Args:
            strategy_results: 策略结果
            
        Returns:
            交易记录
        """
        trades = []
        position = 0
        entry_price = 0.0
        entry_date = None
        
        for i, (date, row) in enumerate(strategy_results.iterrows()):
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
                profit = (exit_price - entry_price) * position * self.contract_size
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
            last_date = strategy_results.index[-1]
            last_price = strategy_results['Close'].iloc[-1]
            profit = (last_price - entry_price) * position * self.contract_size
            trades.append({
                'Entry_Date': entry_date,
                'Exit_Date': last_date,
                'Entry_Price': entry_price,
                'Exit_Price': last_price,
                'Position': position,
                'Profit': profit,
                'Return': (last_price / entry_price - 1) * 100 if position > 0 else (entry_price / last_price - 1) * 100
            })
        
        return pd.DataFrame(trades)
    
    def _calculate_equity_curve(self, trades: pd.DataFrame, strategy_results: pd.DataFrame) -> pd.DataFrame:
        """
        计算账户权益曲线
        
        Args:
            trades: 交易记录
            strategy_results: 策略结果
            
        Returns:
            权益曲线
        """
        equity_curve = pd.DataFrame(index=strategy_results.index)
        equity_curve['Equity'] = self.initial_capital
        equity_curve['Returns'] = 0.0
        
        if trades.empty:
            return equity_curve
        
        # 计算每日权益变化
        current_capital = self.initial_capital
        trade_idx = 0
        
        for i, (date, row) in enumerate(strategy_results.iterrows()):
            # 检查是否有交易在当天平仓
            if trade_idx < len(trades) and date >= trades.iloc[trade_idx]['Exit_Date']:
                current_capital += trades.iloc[trade_idx]['Profit']
                trade_idx += 1
            
            equity_curve.loc[date, 'Equity'] = current_capital
            if i > 0:
                prev_equity = equity_curve.iloc[i-1]['Equity']
                if prev_equity != 0:
                    equity_curve.loc[date, 'Returns'] = (current_capital / prev_equity - 1) * 100
        
        return equity_curve
    
    def get_performance_metrics(self) -> Dict:
        """
        计算绩效指标
        
        Returns:
            绩效指标字典
        """
        if self.results is None:
            return {}
        
        # 获取回测结果
        backtest_result = self.run_backtest()
        trades = backtest_result['trades']
        equity_curve = backtest_result['equity_curve']
        
        if trades.empty or equity_curve.empty:
            return {}
        
        # 计算绩效指标
        total_return = backtest_result['total_return']
        final_capital = backtest_result['final_capital']
        
        # 计算年化收益率
        days = (pd.to_datetime(self.end_date) - pd.to_datetime(self.start_date)).days
        annual_return = (final_capital / self.initial_capital) ** (365.25 / days) - 1
        annual_return_percent = annual_return * 100
        
        # 计算最大回撤
        equity = equity_curve['Equity']
        rolling_max = equity.expanding().max()
        drawdown = (equity - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        
        # 计算夏普比率（简化计算，无风险收益率设为0）
        returns = equity_curve['Returns']
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
        
        # 交易统计
        total_trades = len(trades)
        winning_trades = len(trades[trades['Profit'] > 0])
        losing_trades = len(trades[trades['Profit'] < 0])
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        
        # 平均盈亏
        avg_win = trades[trades['Profit'] > 0]['Profit'].mean() if winning_trades > 0 else 0
        avg_loss = trades[trades['Profit'] < 0]['Profit'].mean() if losing_trades > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        return {
            '初始资金': self.initial_capital,
            '最终资金': final_capital,
            '总收益率(%)': total_return,
            '年化收益率(%)': annual_return_percent,
            '最大回撤(%)': max_drawdown,
            '夏普比率': sharpe_ratio,
            '总交易次数': total_trades,
            '胜率(%)': win_rate,
            '盈利次数': winning_trades,
            '亏损次数': losing_trades,
            '平均盈利': avg_win,
            '平均亏损': avg_loss,
            '盈亏比': profit_factor
        }


if __name__ == "__main__":
    # 示例使用
    # 创建回测实例
    backtester = TurtleBacktester(
        symbol="AAPL",
        start_date="2020-01-01",
        end_date="2023-12-31",
        initial_capital=100000.0
    )
    
    # 运行回测
    results = backtester.run_backtest()
    
    # 获取绩效指标
    metrics = backtester.get_performance_metrics()
    
    # 显示结果
    print("海龟交易策略回测结果")
    print("=" * 50)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")