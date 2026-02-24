# Moving Average Crossover Trading Engine

A modular, event-driven algorithmic trading system that implements a 50/200-day Simple Moving Average (SMA) crossover strategy. The system supports both historical backtesting and fully automated live paper/real trading via the Alpaca Markets API.

---

## Features

* **Modular architecture** — Data, Strategy, Portfolio, and Broker logic are fully separated
* **Realistic backtesting** — Event-driven portfolio simulation with exact cash and share tracking
* **Transaction cost modelling** — 0.1% fee applied on every buy and sell
* **Lookahead bias protection** — Signals are shifted by one day before execution
* **Live trading integration** — Connects to Alpaca Markets API for order execution
* **Duplicate order guard** — Checks for existing open orders before submitting a new one
* **Order confirmation** — Verifies order status after submission on both buys and sells
* **Market hours guard** — Skips execution if the US market is currently open
* **Data staleness check** — Aborts if fetched data is more than 5 days old
* **Kill switch** — Halts all trading if daily portfolio loss exceeds a configurable threshold
* **Email alerting** — Sends an email notification on every trade and on emergency exit via Gmail SMTP
* **Timezone-aware scheduling** — Converts Athens local time to UTC dynamically, handling daylight saving automatically
* **Automated scheduling** — Runs automatically at market close Monday–Friday
* **Persistent logging** — All events logged to terminal and `logs/trading.log`
* **Full test suite** — Pytest suite covering all core modules with mocks for broker and notifier tests

---

## Prerequisites

* Python 3.9 or higher
* A virtual environment (recommended)
* An [Alpaca Markets](https://alpaca.markets) account (free) for live/paper trading
* A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) for email alerts

---

## Project Structure

```
├── src/
│   ├── data_handler.py       # Fetches and validates historical market data (yfinance)
│   ├── strategy.py           # Calculates SMAs and generates buy/sell signals
│   ├── portfolio.py          # Simulates trades, cash balances, and fees (backtesting)
│   ├── broker.py             # Alpaca API wrapper for live order execution
│   └── notifier.py           # Gmail SMTP email alerting
│
├── tests/
│   ├── test_data_handler.py  # Tests for data validation logic
│   ├── test_strategy.py      # Tests for signal generation logic
│   ├── test_portfolio.py     # Tests for portfolio state and syncing logic
│   ├── test_broker.py        # Tests for broker connection and order handling (mocked)
│   ├── test_notifier.py      # Tests for email alert sending (mocked)
│   └── test_live_main.py     # Tests for live bot decision logic (mocked)
│
├── main.py                   # Entry point for running historical backtests
├── live_main.py              # Entry point for running the live trading bot once
├── scheduler.py              # Schedules live_main.py to run at market close daily
├── .env                      # API keys and credentials (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

1. **Clone the repository**

```
git clone <your-repo-url>
cd algotrad
```

2. **Create and activate a virtual environment**

```
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

3. **Install dependencies**

```
pip install -r requirements.txt
```

4. **Set up your environment variables**

Create a `.env` file in the project root:

```
# Alpaca API
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Email alerts (Gmail only)
EMAIL_USER=your_gmail@gmail.com
EMAIL_PASS=your_gmail_app_password_here

# Timezone — set to true on a cloud server running UTC, leave unset for local testing
USE_UTC=true
```

> ⚠️ Use the `paper-api` URL for paper trading. Switch to `https://api.alpaca.markets` only when ready to go live with real money.

> ⚠️ `EMAIL_PASS` must be a Gmail **App Password**, not your regular Gmail password. Generate one at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). Standard passwords will be rejected by Gmail's SMTP server.

---

## How to Run

### Backtest (Historical Simulation)

Runs the strategy against historical SPY data from 2007–2011. This window is chosen to demonstrate the strategy's core strength: avoiding the 2008 financial crisis drawdown by exiting to cash when the 50-day SMA crosses below the 200-day SMA. For a broader historical evaluation, adjust `START` and `END` in `main.py`.

```
python main.py
```

### Live Bot (Single Run)

Fetches today's data, generates a signal, and executes a trade if needed:

```
python live_main.py
```

### Automated Scheduler

Runs the live bot automatically at 23:15 Athens time (UTC+2 in winter, UTC+3 in summer), Monday–Friday:

```
python scheduler.py
```

> ℹ️ On a cloud server set to UTC, ensure `USE_UTC=true` is in your `.env` file. On your local machine, leave it unset — the scheduler will use your machine's local clock.

---

## How to Run the Tests

```
pytest
```

To run a specific test file:

```
pytest tests/test_live_main.py
```

---

## How the Strategy Works

The system uses a **Golden Cross / Death Cross** moving average crossover:

| Condition | Signal | Action |
| --- | --- | --- |
| 50-day SMA crosses **above** 200-day SMA | `1.0` (BUY) | Enter long position |
| 50-day SMA crosses **below** 200-day SMA | `0.0` (SELL) | Exit to cash |

The live bot compares the current signal against the actual Alpaca position and only trades when there is a mismatch — avoiding unnecessary orders.

---

## Safety Mechanisms

The live bot includes several layers of protection that run before any trade is executed:

| Mechanism | Behaviour |
| --- | --- |
| **Market hours guard** | Skips execution entirely if the US market is currently open |
| **Data staleness check** | Aborts if the most recent data is more than 5 days old |
| **Kill switch** | Halts all trading if daily portfolio loss exceeds `MAX_DAILY_LOSS_PCT` (default: -5%) and sends an emergency email alert |
| **Duplicate order guard** | Checks for open pending orders before submitting a buy to prevent double-buying |
| **Order confirmation** | Waits 5 seconds after submission and logs the confirmed order status |
| **Email alerts** | Sends an email notification on every successful buy, every successful sell, and on kill switch activation |

---

## Architecture Overview

```
DataHandler → Strategy → Portfolio (backtest)
                    ↘
                  live_main → AlpacaBroker → Alpaca API
                    ↓
                 Notifier (email alert on trade or emergency)
                    ↑
                scheduler (runs daily at market close)
```

---

## Configuration

Key parameters can be adjusted directly in `main.py` and `live_main.py`:

| Parameter | Default | Description |
| --- | --- | --- |
| `TICKER` | `SPY` | The asset to trade |
| `CASH` | `10000.0` | Starting capital for backtests |
| `CASH_BUFFER` | `0.95` | Fraction of buying power to deploy (5% kept as buffer for slippage) |
| `MAX_DAILY_LOSS_PCT` | `-5.0` | Kill switch threshold — halts trading if daily loss exceeds this |
| `short_window` | `50` | Short SMA period (days) |
| `long_window` | `200` | Long SMA period (days) |
| `RUN_TIME_LOCAL` | `"23:15"` | Scheduled run time in Athens local time (`scheduler.py`) |

---

## Logging

All events are logged to both the terminal and `logs/trading.log`. The log file and `logs/` directory are created automatically on first run and are excluded from git via `.gitignore`.

Example log output:

```
2026-02-23 23:15:01 INFO [*] UTC mode: scheduling at 21:15 UTC (23:15 Athens time)
2026-02-23 23:15:01 INFO [*] Scheduler initialized. Waiting for the next trading window...
2026-02-23 23:15:02 INFO [*] ALARM CLOCK: Waking up the trading bot...
2026-02-23 23:15:02 INFO === Waking up Live Bot for SPY ===
2026-02-23 23:15:03 INFO [*] Keys valid! Account Status: ACTIVE
2026-02-23 23:15:04 INFO [*] Current Price: $681.41
2026-02-23 23:15:04 INFO [*] Target Signal: BUY/HOLD (1.0)
2026-02-23 23:15:04 INFO [*] Actual Shares Owned: 138.0
2026-02-23 23:15:04 INFO [*] State is perfectly synced. No action required today.
2026-02-23 23:15:04 INFO === Bot going back to sleep ===
```

---

## Deploying to a Cloud Server

To run the bot 24/7 without keeping your local machine on, deploy to a Linux VPS (e.g. DigitalOcean, GCP, AWS). The server's timezone should be UTC (the default on most Linux servers).

```
# 1. Clone the repo
git clone <your-repo-url> && cd algotrad

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file with USE_UTC=true
# 4. Run a manual test first
python live_main.py

# 5. Start the scheduler in a persistent session
screen -S algotrad
python scheduler.py

# 6. Detach with Ctrl+A then D — the bot keeps running
```

---

## Important Warnings

> **This system trades real money if pointed at the live Alpaca API. Always validate on paper trading before switching to live.**

* Run in paper trading mode for at least 30 days before going live
* Monitor live performance vs backtest expectations regularly
* The kill switch halts new orders but does not liquidate existing positions — review manually if triggered
* The strategy is not guaranteed to be profitable
* Past backtest performance does not guarantee future results

---

## License

This project is for educational purposes. Use at your own risk.

---

*Created by Paris Salonikios*
