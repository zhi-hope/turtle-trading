"""
海龟交易法则策略实现
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import yfinance as yf


class TurtleTradingStrategy:
    def __init__(self, 
                 entry_window: int = 20,      # 入场窗口（唐奇安通道周期）
                 exit_window: int = 10,       # 出场窗口（唐奇安通道周期）
                 atr_window: int = 20,        # ATR计算窗口
                 atr_multiplier: float = 2.0, # ATR止损倍数
                 risk_percent: float = 0.01): # 账户风险百分比
        """
        初始化海龟交易策略
        
        Args:
            entry_window: 入场信号窗口（唐奇安通道周期）
            exit_window: 出场信号窗口（唐奇安通道周期）
            atr_window: ATR计算窗口
            atr_multiplier: ATR止损倍数
            risk_percent: 账户风险百分比
        """
        self.entry_window = entry_window
        self.exit_window = exit_window
        self.atr_window = atr_window
        self.atr_multiplier = atr_multiplier
        self.risk_percent = risk_percent
        
    def calculate_donchian_channels(self, data: pd.DataFrame, window: int) -> pd.DataFrame:
        """
        计算唐奇安通道
        
        Args:
            data: 价格数据
            window: 计算窗口
            
        Returns:
            包含唐奇安通道的数据框
        """
        data_copy = data.copy()
        data_copy['Donchian_High'] = data_copy['High'].rolling(window=window).max()
        data_copy['Donchian_Low'] = data_copy['Low'].rolling(window=window).min()
        return data_copy
    
    def calculate_atr(self, data: pd.DataFrame, window: int) -> pd.Series:
        """
        计算ATR（平均真实波幅）
        
        Args:
            data: 价格数据
            window: 计算窗口
            
        Returns:
            ATR序列
        """
        data_copy = data.copy()
        # 计算真实波幅（TR）
        data_copy['H-L'] = data_copy['High'] - data_copy['Low']
        data_copy['H-PC'] = abs(data_copy['High'] - data_copy['Close'].shift(1))
        data_copy['L-PC'] = abs(data_copy['Low'] - data_copy['Close'].shift(1))
        data_copy['TR'] = data_copy[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # 计算ATR
        atr = data_copy['TR'].rolling(window=window).mean()
        return atr
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成海龟交易信号
        
        Args:
            data: 价格数据
            
        Returns:
            包含信号的数据框
        """
        data_copy = data.copy()
        
        # 计算唐奇安通道（入场信号）
        data_copy = self.calculate_donchian_channels(data_copy, self.entry_window)
        
        # 计算唐奇安通道（出场信号）
        exit_data = data_copy[['High', 'Low', 'Close']].copy()
        exit_data = self.calculate_donchian_channels(exit_data, self.exit_window)
        data_copy['Exit_High'] = exit_data['Donchian_High']
        data_copy['Exit_Low'] = exit_data['Donchian_Low']
        
        # 计算ATR
        data_copy['ATR'] = self.calculate_atr(data_copy, self.atr_window)
        
        # 初始化信号列
        data_copy['Signal'] = 0
        data_copy['Position'] = 0
        data_copy['Entry_Price'] = 0.0  # 记录入场价格
        data_copy['Stop_Loss'] = 0.0    # 记录止损价格
        
        # 初始化持仓状态
        position = 0
        entry_price = 0.0
        
        # 逐日生成信号
        for i in range(1, len(data_copy)):
            current_close = data_copy['Close'].iloc[i]
            current_high = data_copy['High'].iloc[i]
            current_low = data_copy['Low'].iloc[i]
            prev_close = data_copy['Close'].iloc[i-1]
            
            # 获取唐奇安通道值
            donchian_high = data_copy['Donchian_High'].iloc[i-1]  # 前一日的值
            donchian_low = data_copy['Donchian_Low'].iloc[i-1]    # 前一日的值
            exit_high = data_copy['Exit_High'].iloc[i-1]          # 前一日的值
            exit_low = data_copy['Exit_Low'].iloc[i-1]            # 前一日的值
            atr = data_copy['ATR'].iloc[i]
            
            # ATR止损价格
            long_stop_loss = entry_price - atr * self.atr_multiplier if position > 0 else 0
            short_stop_loss = entry_price + atr * self.atr_multiplier if position < 0 else 0
            
            # 检查止损条件
            stop_loss_triggered = False
            if position > 0 and current_low <= long_stop_loss:  # 多头止损
                data_copy.loc[data_copy.index[i], 'Signal'] = -1
                position = 0
                entry_price = 0.0
                stop_loss_triggered = True
            elif position < 0 and current_high >= short_stop_loss:  # 空头止损
                data_copy.loc[data_copy.index[i], 'Signal'] = 1
                position = 0
                entry_price = 0.0
                stop_loss_triggered = True
            
            # 如果没有触发止损，检查其他信号
            if not stop_loss_triggered:
                # 生成入场信号
                if position == 0:  # 当前无持仓
                    if current_close > donchian_high:  # 多头入场
                        data_copy.loc[data_copy.index[i], 'Signal'] = 1
                        position = 1
                        entry_price = current_close
                    elif current_close < donchian_low:  # 空头入场
                        data_copy.loc[data_copy.index[i], 'Signal'] = -1
                        position = -1
                        entry_price = current_close
                else:  # 当前有持仓
                    # 生成出场信号
                    if position > 0 and (current_close < exit_low or current_close < long_stop_loss):  # 多头出场
                        data_copy.loc[data_copy.index[i], 'Signal'] = -1
                        position = 0
                        entry_price = 0.0
                    elif position < 0 and (current_close > exit_high or current_close > short_stop_loss):  # 空头出场
                        data_copy.loc[data_copy.index[i], 'Signal'] = 1
                        position = 0
                        entry_price = 0.0
            
            # 记录持仓和止损信息
            data_copy.loc[data_copy.index[i], 'Position'] = position
            data_copy.loc[data_copy.index[i], 'Entry_Price'] = entry_price
            data_copy.loc[data_copy.index[i], 'Stop_Loss'] = long_stop_loss if position > 0 else short_stop_loss if position < 0 else 0
        
        return data_copy
    
    def calculate_position_size(self, 
                              data: pd.DataFrame, 
                              account_value: float,
                              contract_size: float = 1.0) -> pd.DataFrame:
        """
        计算头寸规模
        
        Args:
            data: 价格数据
            account_value: 账户价值
            contract_size: 合约乘数
            
        Returns:
            包含头寸规模的数据框
        """
        data_copy = data.copy()
        
        # 计算每笔交易允许的最大损失金额
        max_loss_per_trade = account_value * self.risk_percent
        
        # 计算头寸规模
        # 头寸规模 = 账户风险金额 / (ATR × 每点价值)
        data_copy['Position_Size'] = max_loss_per_trade / (data_copy['ATR'] * contract_size)
        
        # 处理无穷大和NaN值
        data_copy['Position_Size'] = data_copy['Position_Size'].replace([np.inf, -np.inf], 0)
        data_copy['Position_Size'] = data_copy['Position_Size'].fillna(0)
        
        return data_copy
    
    def run_strategy(self, 
                    data: pd.DataFrame, 
                    account_value: float = 100000.0,
                    contract_size: float = 1.0) -> pd.DataFrame:
        """
        运行海龟交易策略
        
        Args:
            data: 价格数据
            account_value: 初始账户价值
            contract_size: 合约乘数
            
        Returns:
            包含策略结果的数据框
        """
        # 生成信号
        data_with_signals = self.generate_signals(data)
        
        # 计算头寸规模
        data_with_positions = self.calculate_position_size(data_with_signals, account_value, contract_size)
        
        return data_with_positions


 