# Algorithmic Trading Engine

A fully automated, state-based quantitative trading system built in Python. This algorithm executes a Moving Average Crossover strategy (50-day vs. 200-day) on the SPDR S&P 500 ETF Trust (SPY). It features historical backtesting, automated live paper trading via the Alpaca API, and a robust state-machine to prevent execution errors.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Data Manipulation & Math:** Pandas, NumPy
* **Market Data Sourcing:** `yfinance` (Yahoo Finance API)
* **Brokerage Integration:** Alpaca Trading API (`alpaca-trade-api`)
* **Environment Management:** `python-dotenv`
* **Task Scheduling:** `schedule`
* **Testing Framework:** `pytest`, `unittest.mock`

## 🚀 Key Features
* **Dual-Mode Execution:** Capable of running historical backtests (`main.py`) and live market execution (`live_main.py`).
* **State-Machine Logic:** The bot never relies on internal math for live trading. It queries the broker for exact share counts and cash balances before calculating execution sizes, preventing "ghost orders" and double-buying.
* **Fail-Fast Authorization:** Automatically validates API keys upon initialization.
* **Automated Scheduling:** Includes a local cron-job wrapper (`scheduler.py`) to wake the bot up 15 minutes before market close, execute trades, and go back to sleep.
* **Enterprise Logging:** Implements dual-logging (Terminal + `.log` file) to keep a permanent audit trail of all automated decisions.

## 📂 Project Architecture

```text
algotrad/
├── .env                  # API Vault (Ignored by Git)
├── .gitignore            # Security rules
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── main.py               # Historical Backtester Orchestrator
├── live_main.py          # Live Market Orchestrator
├── scheduler.py          # Automation Alarm Clock
├── logs/
│   └── trading.log       # Permanent audit trail
├── notebooks/            # Jupyter notebooks for quantitative research
├── src/                  # Core Modules (The Toolbox)
│   ├── broker.py         # Alpaca API connection and order execution
│   ├── data_handler.py   # Yahoo Finance data fetching and cleaning
│   ├── portfolio.py      # Event-driven backtesting ledger
│   └── strategy.py       # Moving Average math and signal generation
└── tests/                # Automated Test Suite (Pytest + Mocking)
    ├── test_data.py
    ├── test_portfolio.py
    ├── test_strategy.py
    └── test_live_main.py