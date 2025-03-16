from typing import List, Dict
import time
import pandas as pd


class HelperMethods:
    @staticmethod
    def merge_indicator_data(indicators: Dict={}):
        # Convert all indicator lists to DataFrames
        df_rsi = pd.DataFrame(indicators["rsi"])
        # df_macd = pd.DataFrame(indicators["macd"])
        df_sma = pd.DataFrame(indicators["sma"])
        # df_bollinger = pd.DataFrame(indicators["bollinger"])
        df_ema = pd.DataFrame(indicators["ema"])
        df_adx = pd.DataFrame(indicators["adx"])
        df_wma = pd.DataFrame(indicators["wma"])
        df_dema = pd.DataFrame(indicators["dema"])
        df_tema = pd.DataFrame(indicators["tema"])
        df_williams = pd.DataFrame(indicators["williams"])

        # Merge all indicators into one DataFrame using "date" as index
        df = df_rsi.rename(columns={"rsi": "rsi"}).set_index("date")
        # df["macd"] = df_macd["macd"] if not df_macd.empty else None
        # df["sma_50"] = df_sma["sma_50"] if not df_sma.empty else None
        # df["sma_200"] = df_sma["sma_200"] if not df_sma.empty else None
        # df["bollinger_upper"] = df_bollinger["bollinger_upper"] if not df_bollinger.empty else None
        # df["bollinger_lower"] = df_bollinger["bollinger_lower"] if not df_bollinger.empty else None
        df["ema"] = df_ema["ema"] if not df_ema.empty else None
        df["adx"] = df_adx["adx"] if not df_adx.empty else None
        df["wma"] = df_wma["wma"] if not df_wma.empty else None
        df["dema"] = df_dema["dema"] if not df_dema.empty else None
        df["tema"] = df_tema["tema"] if not df_tema.empty else None
        df["williams"] = df_williams["williams"] if not df_williams.empty else None

        # Convert index to datetime format
        df.index = pd.to_datetime(df.index)
        return df

    @staticmethod
    def filter_tickers_by_exchange(exchange_name: str="", tickers: List=[]):
        return [ticker.get('symbol') for ticker in tickers if ticker.get('exchangeShortName') == exchange_name]
    
    @staticmethod
    def persist_on_csv(tickers: List[Dict]):
        df = pd.DataFrame(tickers)
        df.to_csv("nasdaq_stock_data.csv", index=False)
