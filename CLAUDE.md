# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository implements the Turtle Trading strategy, a classic trend-following system developed by Richard Dennis in the 1980s. The implementation includes the core strategy logic, a backtesting engine, and example programs.

## Code Architecture and Structure

### Core Components

1. **turtle_trading_strategy.py** - Core strategy implementation:
   - `TurtleTradingStrategy` class with signal generation logic
   - Donchian channel calculations for entry/exit signals
   - ATR-based position sizing and stop-loss mechanisms
   - Signal generation based on price breakouts

2. **turtle_backtest.py** - Backtesting engine:
   - `TurtleBacktester` class for performance evaluation
   - Trade execution simulation
   - Equity curve and performance metrics calculation
   - Integration with the strategy module

3. **main.py** - Complete example program:
   - Demonstrates both direct strategy usage and full backtesting
   - Shows how to configure and run the strategy
   - Displays results and performance metrics

4. **test_turtle.py** - Testing program with simulated data:
   - Creates mock price data for testing without external dependencies
   - Validates strategy and backtesting functionality
   - Provides quick feedback without network calls

### Key Design Patterns

- Strategy pattern: The `TurtleTradingStrategy` class encapsulates the trading logic
- Composition: The `TurtleBacktester` uses the strategy class rather than inheriting from it
- Separation of concerns: Data loading, strategy logic, and backtesting are separate modules

## Common Development Tasks

### Running the System

1. **Install dependencies**:
   ```bash
   pip install pandas numpy yfinance
   ```

2. **Run the main example program**:
   ```bash
   python main.py
   ```

3. **Run tests (no network required)**:
   ```bash
   python test_turtle.py
   ```

### User Input Parameters

The system accepts the following user inputs:
- **Symbol**: Trading instrument symbol (e.g., "AAPL" for Apple stock)
- **Start Date**: Backtest start date in YYYY-MM-DD format
- **End Date**: Backtest end date in YYYY-MM-DD format
- **Initial Capital**: Starting account balance for backtesting
- **Strategy Parameters**:
  - Entry window: Donchian channel period for entry signals (default: 20 days)
  - Exit window: Donchian channel period for exit signals (default: 10 days)
  - ATR window: Period for ATR calculation (default: 20 days)
  - ATR multiplier: Stop-loss multiplier (default: 2.0)
  - Risk percent: Percentage of account risked per trade (default: 1%)

Users can now input these parameters interactively when running the main.py program. The program will prompt for stock symbol, date range, and initial capital, with default values provided if no input is given.

### Testing

- Unit tests are in `test_turtle.py`
- Tests use simulated data to avoid external dependencies
- No dedicated testing framework is used; tests are run directly with Python

### Key Classes and Methods

1. **TurtleTradingStrategy**:
   - `generate_signals()`: Creates buy/sell signals based on Donchian channels
   - `calculate_position_size()`: Determines position size based on ATR and risk management
   - `run_strategy()`: Main method that combines signal generation and position sizing

2. **TurtleBacktester**:
   - `run_backtest()`: Executes the backtest and returns results
   - `get_performance_metrics()`: Calculates key performance indicators
   - `_calculate_trades()`: Processes signals into actual trades
   - `_calculate_equity_curve()`: Tracks account value over time

## Strategy Logic

The Turtle Trading strategy follows these rules:
1. Entry signals: Price breaks out above the N-day high (long) or below the N-day low (short)
2. Exit signals: Price closes below the M-day low (long positions) or above the M-day high (short positions)
3. Position sizing: Based on ATR to control risk per trade
4. Stop-loss: Set at 2x ATR from entry price