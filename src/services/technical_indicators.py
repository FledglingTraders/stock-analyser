from typing import List, Dict
import pandas as pd

from src.exceptions.exceptions import HttpErrorException, CustomException
from src.utils.apis_call_handler import ApisHandler
from src.enums.stock_indicator import StockTechnicalIndicator
from src.settings.shared import logger
from src.services.helper import HelperMethods

class TechnicalIndicators:
    @staticmethod
    def get_ohlcv_data(base_url: str, ticker: str, api_token: str, date_range: str = None) -> List:
        # Fetch historical OHLCV data
        historical_url = f"{base_url}/historical-price-full/{ticker}?apikey={api_token}{date_range}"
        historical_response = ApisHandler.get(url=historical_url)
        historical_data = historical_response.get('historical', [])
        if not historical_data:
            logger.error(f"No historical data found for {ticker}")
            return []
        return historical_response.get('historical', [])
    
    @staticmethod
    def compute_sma(df: pd.DataFrame, window: int) -> pd.Series:
        """
        Computes the Simple Moving Average (SMA) over a given window.

        Args:
            df (pd.DataFrame): DataFrame containing historical OHLCV data.
            window (int): Number of days for moving average.

        Returns:
            pd.Series: Computed SMA values.
        """
        return df['close'].rolling(window=window).mean()
    
    @staticmethod
    def get_tech_indicator_data(
            base_url: str,
            ticker: str,
            api_token: str,
            date_range: str = None,
            indicator_type: str = None) -> List:
        try:
            url = f"{base_url}/technical_indicator/1day/{ticker}?type={indicator_type}&period=14&apikey={api_token}{date_range}"
            indicator_data = ApisHandler.get(url=url)
            if not indicator_data:
                logger.error(f"No {indicator_type} data found for {ticker}")
                return []
            return indicator_data
        except HttpErrorException as http_error:
            logger.error(f"Failed to fetch {indicator_type} data for {ticker}. HTTP Error: {http_error}")
        except CustomException as error:
            logger.error(f"Failed to fetch {indicator_type} data for {ticker}. Error: {error}")
        return []
    
    @staticmethod
    def fetch_all_technical_indicator(
            base_url: str,
            ticker: str,
            api_token: str,
            date_range: str = None) -> pd.DataFrame:
        # Fetch technical indicators
        
        rsi_data = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.RSI.value
        )
        # macd_data = TechnicalIndicators.get_tech_indicator_data(              
        #     base_url=base_url,
        #     ticker=ticker,
        #     api_token=api_token,
        #     date_range=date_range,
        #     indicator_type=StockTechnicalIndicator.MACD.value
        # )
        sma_data = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.SMA.value
        )
        # bollinger_data = TechnicalIndicators.get_tech_indicator_data(
        #     base_url=base_url,
        #     ticker=ticker,
        #     api_token=api_token,
        #     date_range=date_range,
        #     indicator_type=StockTechnicalIndicator.BOLLINGER.value
        # )
        ema = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.EMA.value
        )
        adx = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.ADX.value
        )
        wma = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.WMA.value
        )
        dema = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.DOUBLE_EMA.value
        )
        tema = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.TRIPLE_EMA.value
        )
        williams = TechnicalIndicators.get_tech_indicator_data(
            base_url=base_url,
            ticker=ticker,
            api_token=api_token,
            date_range=date_range,
            indicator_type=StockTechnicalIndicator.WILLIAMS.value
        )

        indicators = {
            'rsi': rsi_data,
            'sma': sma_data,
            'ema': ema,
            'adx': adx,
            'wma': wma,
            'dema': dema,
            'tema': tema,
            'williams': williams
        }

        df = HelperMethods.merge_indicator_data(indicators)
        if df.empty:
            logger.warning(f"No technical indicators found for {ticker}.")
            return df
        logger.info(f"Successfully fetched technical indicators for {ticker}.")
        return df