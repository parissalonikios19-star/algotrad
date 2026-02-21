# Moving Average Crossover Trading Engine

A modular, event-driven algorithmic trading system that implements a 50/200-day Simple Moving Average (SMA) crossover strategy. The system supports both historical backtesting and fully automated live paper/real trading via the Alpaca Markets API.

---

## Features

- **Modular architecture** — Data, Strategy, Portfolio, and Broker logic are fully separated
- **Realistic backtesting** — Event-driven portfolio simulation with exact cash and share tracking
- **Transaction cost modelling** — 0.1% fee applied on every buy and sell
- **Lookahead bias protection** — Signals are shifted by one day before execution
- **Live trading integration** — Connects to Alpaca Markets API for order execution
- **Automated scheduling** — Runs automatically at market close Monday–Friday
- **Persistent logging** — All events logged to terminal and `logs/trading.log`
- **Full test suite** — Pytest suite covering all core modules with mocks for broker tests

---

## Prerequisites

- Python 3.9 or higher
- A virtual environment (recommended)
- An [Alpaca Markets](https://alpaca.markets) account (free) for live/paper trading

---

## Project Structure

```
├── src/
│   ├── data_handler.py       # Fetches and validates historical market data (yfinance)
│   ├── strategy.py           # Calculates SMAs and generates buy/sell signals
│   ├── portfolio.py          # Simulates trades, cash balances, and fees (backtesting)
│   └── broker.py             # Alpaca API wrapper for live order execution
│
├── tests/
│   ├── test_data_handler.py  # Tests for data validation logic
│   ├── test_strategy.py      # Tests for signal generation logic
│   ├── test_portfolio.py     # Tests for portfolio state and syncing logic
│   ├── test_broker.py        # Tests for broker connection and order handling (mocked)
│   └── test_live_main.py     # Tests for live bot decision logic (mocked)
│
├── main.py                   # Entry point for running historical backtests
├── live_main.py              # Entry point for running the live trading bot once
├── scheduler.py              # Schedules live_main.py to run at market close daily
├── .env                      # API keys (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up your environment variables**

Create a `.env` file in the project root:
```
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

> ⚠️ Use the `paper-api` URL for paper trading. Switch to `https://api.alpaca.markets` only when ready to go live with real money.

---

## How to Run

### Backtest (Historical Simulation)
Runs the strategy against historical SPY data from 2007–2011:

```bash
python main.py
```
The default backtest window (2007–2011) is set to demonstrate the strategy's
ability to avoid the 2008 financial crisis drawdown. For a full historical
evaluation, adjust START and END in main.py.

### Live Bot (Single Run)
Fetches today's data, generates a signal, and executes a trade if needed:
```bash
python live_main.py
```

### Automated Scheduler
Runs the live bot automatically at 22:45 local time, Monday–Friday:
```bash
python scheduler.py
```

---

## How to Run the Tests

```bash
pytest
```

To run a specific test file:
```bash
pytest tests/test_portfolio.py
```

---

## How the Strategy Works

The system uses a **Golden Cross / Death Cross** moving average crossover:

| Condition | Signal | Action |
|-----------|--------|--------|
| 50-day SMA crosses **above** 200-day SMA | `1.0` (BUY) | Enter long position |
| 50-day SMA crosses **below** 200-day SMA | `0.0` (SELL) | Exit to cash |

The live bot compares the current signal against the actual Alpaca position and only trades when there is a mismatch — avoiding unnecessary orders.

---

## Architecture Overview

```
DataHandler → Strategy → Portfolio (backtest)
                    ↘
                  live_main → AlpacaBroker → Alpaca API
                    ↑
                scheduler (runs daily at market close)
```

---

## Important Warnings

> **This system trades real money if pointed at the live Alpaca API. Always validate on paper trading before switching to live.**

- Run in paper trading mode for at least 30 days before going live
- Monitor live performance vs backtest expectations regularly
- The strategy is not guaranteed to be profitable
- Past backtest performance does not guarantee future results

---

## Configuration

Key parameters can be adjusted directly in `main.py` and `live_main.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TICKER` | `SPY` | The asset to trade |
| `CASH` | `10000.0` | Starting capital for backtests |
| `CASH_BUFFER` | `0.95` | Fraction of buying power to deploy (5% kept as buffer) |
| `short_window` | `50` | Short SMA period (days) |
| `long_window` | `200` | Long SMA period (days) |

---

## Logging

All events are logged to both the terminal and `logs/trading.log`. The log file is created automatically on first run. Log files are excluded from git via `.gitignore`.

Example log output:
```
2025-01-15 22:45:01 INFO === Waking up Live Bot for SPY ===
2025-01-15 22:45:02 INFO [*] Keys valid! Account Status: ACTIVE
2025-01-15 22:45:03 INFO [*] Current Price: $482.35
2025-01-15 22:45:03 INFO [*] Target Signal: BUY/HOLD (1.0)
2025-01-15 22:45:03 INFO [*] Actual Shares Owned: 19.0
2025-01-15 22:45:03 INFO [*] State is perfectly synced. No action required today.
2025-01-15 22:45:03 INFO === Bot going back to sleep ===
```

---

## License

This project is for educational purposes. Use at your own risk.

---
*Created by Paris Salonikios*