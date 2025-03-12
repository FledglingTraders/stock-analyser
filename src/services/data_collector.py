from typing import Dict, List, Optional
import pandas as pd
import time
from datetime import datetime

from src.utils.apis_call_handler import ApisHandler
from src.settings.shared import get_app_config
from src.exceptions.exceptions import HttpErrorException, CustomException
from src.settings.shared import logger
from src.services.helper import HelperMethods
from src.utils.decorators import time_execution
from src.model.persistor import StockDataHelper, HistoricalDataHelper
from src.enums.stock_indicator import StockTechnicalIndicator


class DataCollector:

    @staticmethod
    @time_execution
    def fetch_nasdaq_tickers_list(app_config: Dict=None) -> Optional[List[str]]:
        fmp_config = app_config.get('API_KEYS', {}).get('FMP', {})

        url = f"{fmp_config.get('URL')}/stock/list?apikey={fmp_config.get('API_TOKEN')}"

        tickers = None
        try:
            tickers = ApisHandler.get(
                app_config=app_config,
                url=url)
            logger.info("Fetched NASDAQ tickers successfully.")
        except HttpErrorException as http_error:
            logger.error(f"Fetch nasdaq tickers failed. Http Error Reason {http_error}")
        except CustomException as error:
            logger.error(f"Fetch nasdaq tickers failed. Reason {error}")
        
        nasdaq_tickers = None
        if tickers:
            nasdaq_tickers = HelperMethods.filter_tickers_by_exchange(
                exchange_name='NASDAQ',
                tickers=tickers)
            logger.info(f"Filtered NASDAQ tickers successfully. Total tickers: {len(nasdaq_tickers)}")
        return nasdaq_tickers


    @staticmethod
    @time_execution
    def fetch_stock_metadata(ticker: str, app_config: Dict=None) -> Optional[Dict]:
        fmp_config = app_config.get('API_KEYS', {}).get('FMP', {})

        url = f"{fmp_config.get('URL')}/profile/{ticker}?apikey={fmp_config.get('API_TOKEN')}"

        ticker_data = None
        try:
            ticker_data = ApisHandler.get(
                app_config=app_config,
                url=url
            )
        except HttpErrorException as http_error:
            logger.error(f"Fetch Ticker financial data. Http Errpr Reason {http_error}")
        except CustomException as error:
            logger.error(f"etch Ticker financial data failed. Reason {error}")
        
        if ticker_data and len(ticker_data) > 0:
            stock = ticker_data[0]

            stock_metadata = {
                'symbol': stock.get('symbol', ''),
                'name': stock.get('name', ''),
                'sector': stock.get('sector', ''),
                'industry': stock.get('industry', ''),
                'market_cap': stock.get('mktCap', 0),
            }
            return stock_metadata

        logger.info(f"Ticker data is empty for {ticker}")

        return None
    
    @staticmethod
    @time_execution
    def fetch_historical_data_of_ticker(
            app_config: Dict,
            ticker: str,
            start_date: str = None,
            end_date: str = None) -> List:

        fmp_config = app_config.get('API_KEYS', {}).get('FMP', {})
        base_url = fmp_config.get('URL')
        api_token = fmp_config.get('API_TOKEN')

        # Build the historical URL with date range if specified
        date_range = ""
        if start_date and end_date:
            date_range = f"&from={start_date}&to={end_date}"

        logger.info(f"Get historical data for ticker {ticker} ...")
        try:
            # Fetch historical OHLCV data
            historical_data = DataCollector.get_ohlcv_data(
                base_url=base_url,
                ticker=ticker,
                api_token=api_token,
                date_range=date_range
            )
            
            if not historical_data:
                logger.warning(f"Failed to fetch historical data for {ticker}.")
                return None
            
            # Remove invalid data (zero volume or identical OHLC values)
            historical_data = [
                record for record in historical_data
                if record.get('volume', 0) > 0 and not (
                    record.get('open') == record.get('high') == record.get('low') == record.get('close')
                )
            ]

            if not historical_data:
                logger.warning(f"All retrieved OHLCV data for {ticker} was invalid. Skipping.")
                return None

            # Fetch technical indicators
            rsi_data = DataCollector.get_tech_indicator_data(
                base_url=base_url,
                ticker=ticker,
                api_token=api_token,
                date_range=date_range,
                indicator_type=StockTechnicalIndicator.RSI.value
            )
            macd_data = DataCollector.get_tech_indicator_data(              
                base_url=base_url,
                ticker=ticker,
                api_token=api_token,
                date_range=date_range,
                indicator_type=StockTechnicalIndicator.MACD.value
            )
            sma_data = DataCollector.get_tech_indicator_data(
                base_url=base_url,
                ticker=ticker,
                api_token=api_token,
                date_range=date_range,
                indicator_type=StockTechnicalIndicator.SMA.value
            )
            bollinger_data = DataCollector.get_tech_indicator_data(
                base_url=base_url,
                ticker=ticker,
                api_token=api_token,
                date_range=date_range,
                indicator_type=StockTechnicalIndicator.BOLLINGER.value
            )

            # Prepare the list for formatted historical data
            formatted_historical_data = DataCollector.merge_technical_indicator_into_historical_data(
                ticker=ticker,
                historical_data=historical_data,
                rsi_data=rsi_data,
                macd_data=macd_data,
                sma_data=sma_data,
                bollinger_data=bollinger_data
            )

            logger.info(f"Fetched and formatted historical data for {ticker} from {start_date} to {end_date}.")
            return formatted_historical_data

        except HttpErrorException as http_error:
            logger.error(f"Failed to fetch historical data for {ticker}. HTTP Error: {http_error}")
        except CustomException as error:
            logger.error(f"Failed to fetch historical data for {ticker}. Error: {error}")

        return None
    
    @staticmethod
    def get_ohlcv_data(base_url: str, ticker: str, api_token: str, date_range: str = None) -> List:
        # Fetch historical OHLCV data
        historical_url = f"{base_url}/historical-price-full/{ticker}?apikey={api_token}{date_range}"
        historical_response = ApisHandler.get(url=historical_url)
        return historical_response.get('historical', [])
    
    @staticmethod
    def get_tech_indicator_data(base_url: str, ticker: str, api_token: str, date_range: str = None, indicator_type: str = None) -> List:
        url = f"{base_url}/technical_indicator/daily/{ticker}?type={indicator_type}&apikey={api_token}{date_range}"
        try:
            indicator_data = ApisHandler.get(url=url)
            return indicator_data
        except HttpErrorException as http_error:
            logger.error(f"Failed to fetch {indicator_type} data for {ticker}. HTTP Error: {http_error}")
        except CustomException as error:
            logger.error(f"Failed to fetch {indicator_type} data for {ticker}. Error: {error}")
        return []

    @staticmethod
    def merge_technical_indicator_into_historical_data(
            ticker: str,
            historical_data: List,
            rsi_data: List,
            macd_data: List,
            sma_data: List,
            bollinger_data: List) -> List:
    
        # Prepare the list for formatted historical data
        formatted_historical_data = []

        # Merge technical indicators into historical data
        for i, record in enumerate(historical_data):
            formatted_record = {
                'symbol': ticker,
                'date': datetime.strptime(record['date'], '%Y-%m-%d').date(),
                'open': float(record.get('open', 0)),
                'high': float(record.get('high', 0)),
                'low': float(record.get('low', 0)),
                'close': float(record.get('close', 0)),
                'volume': int(record.get('volume', 0)),
                'rsi': float(rsi_data[i].get('rsi', 0)) if rsi_data and i < len(rsi_data) else None,
                'macd': float(macd_data[i].get('macd', 0)) if macd_data and i < len(macd_data) else None,
                'sma_50': float(sma_data[i].get('sma_50', 0)) if sma_data and i < len(sma_data) else None,
                'sma_200': float(sma_data[i].get('sma_200', 0)) if sma_data and i < len(sma_data) else None,
                'bollinger_upper': float(bollinger_data[i].get('bollinger_upper', 0)) if bollinger_data and i < len(bollinger_data) else None,
                'bollinger_lower': float(bollinger_data[i].get('bollinger_lower', 0)) if bollinger_data and i < len(bollinger_data) else None
            }

            formatted_historical_data.append(formatted_record)
        


 
