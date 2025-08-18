# 海龟交易法实现 (增强版)

这是一个完整的海龟交易法Python实现，包含策略信号生成、一个更真实的的回测引擎以及单元测试。

## 主要特性

- **策略实现**: 完整实现了海龟交易法则的核心逻辑。
- **真实回测**: 回测引擎支持手续费和滑点模拟，提供更贴近现实的绩效评估。
- **丰富指标**: 除了标准的回报率和夏普比率，还计算索提诺比率和卡玛比率。
- **单元测试**: 项目包含一套使用 `pytest` 编写的单元测试，确保代码的质量和可靠性。

## 文件结构

- `main.py`: 项目主入口，用于运行回测。
- `turtle_trading_strategy.py`: 海龟交易策略的核心实现。
- `turtle_backtest.py`: 增强版的回测引擎。
- `data_utils.py`: 用于从 `yfinance` 获取数据的工具函数。
- `requirements.txt`: 项目依赖库。
- `tests/`: 包含所有单元测试的目录。
  - `conftest.py`: 为测试提供共享数据 (fixtures)。
  - `test_strategy.py`: 策略逻辑的单元测试。
  - `test_backtester.py`: 回测引擎的单元测试。

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行回测
```bash
python main.py
```
程序运行时会提示输入以下参数：
- 股票代码 (例如: AAPL, GOOGL, TSLA)
- 开始/结束日期 (格式: YYYY-MM-DD)
- 初始资金
- **手续费率** (例如: 0.001 代表 0.1%)
- **滑点** (例如: 0.0005 代表 0.05%)

### 3. 运行测试
要验证代码的正确性，可以运行单元测试：
```bash
pytest
```

## 类说明

### TurtleTradingStrategy
核心策略类，用于生成交易信号。

**参数**:
- `entry_window`: 入场信号窗口 (默认20天)
- `exit_window`: 出场信号窗口 (默认10天)
- `atr_window`: ATR计算窗口 (默认20天)
- `atr_multiplier`: ATR止损倍数 (默认2.0)
- `risk_percent`: 账户风险百分比 (默认0.01)

### TurtleBacktester
回测引擎类，用于策略性能评估。

**参数**:
- `symbol`: 交易标的代码
- `start_date`: 回测开始日期
- `end_date`: 回测结束日期
- `initial_capital`: 初始资金 (默认100000.0)
- `commission_rate`: **手续费率** (默认0.001)
- `slippage`: **滑点** (默认0.0005)
- `contract_size`: 合约乘数 (默认1.0)

## 绩效指标说明
- **夏普比率 (Sharpe Ratio)**: 衡量承受单位风险所获得的的超额回报。越高越好。
- **索提诺比率 (Sortino Ratio)**: 只考虑下行风险的夏普比率，能更好地区分策略在处理亏损时的表现。越高越好。
- **卡玛比率 (Calmar Ratio)**: 年化收益与最大回撤的比率，衡量策略的恢复能力。越高越好。

## 注意事项

1. 本实现仅供学习和研究使用，不构成投资建议。
2. 实盘交易前请进行充分测试。
3. 策略参数可根据具体市场环境进行调整。
