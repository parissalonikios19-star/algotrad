import src.data_handler
import src.strategy
import src.portfolio
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


#main file that runs the trading algorithm

def run_algo():
    TICKER='SPY'
    START = '2007-01-01'
    END = '2011-12-31'
    CASH = 10000.00

    logger.info(f"Starting Algo Engine for {TICKER}")

    handler = src.data_handler.DataHandler(TICKER , START , END)
    strategy = src.strategy.MACrossoverStrategy()
    portfolio = src.portfolio.Portfolio(CASH)

    raw_data = handler.fetch_data()
    signals = strategy.generate_signals(raw_data)
    results = portfolio.backtest(signals)

    final_val = results['Total'].iloc[-1]
    total_ret = ((final_val - CASH) / CASH) * 100

    logger.info("=" * 30)
    logger.info(f"FINAL PERFORMANCE: {TICKER}")
    logger.info(f"Ending Value:  ${final_val:,.2f}")
    logger.info(f"Total Return:  {total_ret:.2f}%")
    logger.info("=" * 30)

if __name__ == "__main__":
    try:
        run_algo()
    except (ValueError, ConnectionError, KeyError) as e:
        logger.error(f"Algo failed: {e}")

