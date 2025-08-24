# 海龟交易策略回测工具

本项目是一个基于 Python 的回测引擎，用于测试著名的“海龟交易”策略。它允许用户在真实历史股价数据上测试该策略，并评估其性能。

## 项目结构

项目采用标准化的结构，将源代码、测试和配置文件清晰地分离开来。

```
turtle_trading/
├── src/
│   ├── __init__.py
│   ├── data_utils.py             # 获取历史股价数据
│   ├── turtle_trading_strategy.py# 实现核心策略逻辑
│   ├── turtle_backtest.py        # 回测引擎
│   └── main.py                   # 运行回测的主入口
├── tests/
│   ├── conftest.py
│   ├── test_backtester.py
│   └── test_strategy.py
├── .gitignore
├── pytest.ini                    # Pytest 配置文件
└── README.md
```

## 如何运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行回测

主程序是交互式的，启动后会提示您输入股票代码、日期范围和其他参数。

```bash
python -m src.main
```

### 3. 运行测试

要运行项目的单元测试，请使用 `pytest`。

```bash
pytest
```
