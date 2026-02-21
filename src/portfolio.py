import pandas as pd

class Portfolio:
    """
    Simulates a realistic brokerage account using an event-driven ledger.
    Tracks exact cash, dynamic share counts, and transaction fees.
    """
    def __init__(self, initial_capital=10000.0):
        self.initial_capital = initial_capital

    def backtest(self, data):
        print("[*] Running robust state-based portfolio simulation...")
        
        # check for required columns
        required_columns = ['Close', 'Signal']
        for col in required_columns:
            if col not in data.columns:
                raise KeyError(f"[!] PORTFOLIO ERROR: Missing required column '{col}'. Check your Strategy output.")
        data = data.copy()

        cash = self.initial_capital
        shares = 0.0
        fee_pct = 0.001
        
        cash_history = []
        shares_history = []
        total_history = []
        
        prices = data['Close'].values
        target_signals = data['Signal'].shift(1).fillna(0).values 
        
        for i in range(len(prices)):
            price = prices[i]
            target = target_signals[i]
            
            # --- TARGET PORTFOLIO SYNCING ---
            
            # State Mismatch: Strategy wants IN, but we are OUT. -> BUY
            if target == 1.0 and shares == 0.0:
                fee = cash * fee_pct
                available_cash = cash - fee
                shares = available_cash / price
                cash = 0.0
                
            # State Mismatch: Strategy wants OUT, but we are IN. -> SELL
            elif target == 0.0 and shares > 0.0:
                gross_proceeds = shares * price
                fee = gross_proceeds * fee_pct
                cash = gross_proceeds - fee
                shares = 0.0
                
            # If target == 1.0 and shares > 0 (We are IN and should be IN) -> DO NOTHING
            # If target == 0.0 and shares == 0 (We are OUT and should be OUT) -> DO NOTHING
                
            # --- RECORD DAILY LEDGER ---
            cash_history.append(cash)
            shares_history.append(shares)
            total_history.append(cash + (shares * price))
            
        data['Cash'] = cash_history
        data['Shares'] = shares_history
        data['Total'] = total_history
        
        self.positions = data
        print("[*] Backtest complete.")
        return self.positions

