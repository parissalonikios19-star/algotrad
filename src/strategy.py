import numpy as np

# this class contains the logic for moving average crossover
# takes price data and calculates buy/hold/sell signals

class MACrossoverStrategy:

    def __init__(self , short_window=50 , long_window=200):
        # check for valid parameters
        if short_window >= long_window:
            raise ValueError(f"[!] short_window ({short_window}) must be less than long_window ({long_window}).")
        
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self , data):
        
        print(f"[*] Calculating {self.short_window}-day and {self.long_window}-day moving averages...")
        # check for needed columns
        if 'Close' not in data.columns:
            raise ValueError("[!] STRATEGY ERROR: Missing required column 'Close'.")
        data = data.copy()
        #calculate moving averages
        data['SMA_Short'] = data['Close'].rolling(window=self.short_window).mean()
        data['SMA_Long'] = data['Close'].rolling(window=self.long_window).mean()

        # calculate signals
        data['Signal'] = np.where(data['SMA_Short'] > data['SMA_Long'], 1.0, 0.0)

        # calculate positions
        data['Position'] = data['Signal'].diff()

        print("[*] Trading signals generated successfully.")
        return data