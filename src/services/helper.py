from typing import List, Dict
import time
import pandas as pd


class HelperMethods:
    @staticmethod
    def filter_tickers_by_exchange(exchange_name: str="", tickers: List=[]):
        return [ticker.get('symbol') for ticker in tickers if ticker.get('exchangeShortName') == exchange_name]
    
    @staticmethod
    def persist_on_csv(tickers: List[Dict]):
        df = pd.DataFrame(tickers)
        df.to_csv("nasdaq_stock_data.csv", index=False)
