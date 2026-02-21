import yfinance as yf
import pandas as pd

#this class is responsible for fetching and processing historical price data

class DataHandler:
    
    def __init__(self , ticker , start_date , end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
    
    def _clean_data(self , data):
        print("[*] Running data sanity checks...")
        # drop empty row
        data = data.dropna(how='all')
        # if price is missing assume it stayed the same
        data = data.ffill(limit=3)
        if data['Close'].isna().any():
            raise ValueError("[!] Data contains unfillable gaps after forward-fill.")
        # check for wrong values , negative prices
        if (data['Close'] <= 0).any():
            raise ValueError(f"[!] FATAL ERROR: {self.ticker} data contains zero or negative prices.")
        # ckeck if there is enough data to calculate needed metrics
        if len(data) < 200:
            raise ValueError(f"[!] FATAL ERROR: Only {len(data)} days of data fetched. Need at least 200.")
        
        print("[*] Data passed all integrity checks.")
        return data



    def fetch_data(self):
        print(f"[*] Fetching historical data for {self.ticker}...")
        # try to dowload data from yfinance
        try:
            data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        except Exception as e:
            raise ConnectionError(f"[!] Failed to fetch data for {self.ticker}: {e}")
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if data.empty:
            raise ValueError(f"[!] No data found for {self.ticker}. Check your dates or ticker symbol.")
        print("[*] Data fetched successfully.")

        # clean data
        clean_data = self._clean_data(data)
        return clean_data