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

from src.services.technical_indicators import TechnicalIndicators


class DataCollector:

    @staticmethod
    @time_execution
    def fetch_nasdaq_tickers_list(app_config: Dict = None) -> Optional[List[str]]:
        fmp_config = app_config.get("API_KEYS", {}).get("FMP", {})

        url = f"{fmp_config.get('URL')}/stock/list?apikey={fmp_config.get('API_TOKEN')}"

        tickers = None
        try:
            tickers = ApisHandler.get(app_config=app_config, url=url)
            logger.info("Fetched NASDAQ tickers successfully.")
        except HttpErrorException as http_error:
            logger.error(f"Fetch nasdaq tickers failed. Http Error Reason {http_error}")
        except CustomException as error:
            logger.error(f"Fetch nasdaq tickers failed. Reason {error}")

        nasdaq_tickers = None
        if tickers:
            nasdaq_tickers = HelperMethods.filter_tickers_by_exchange(
                exchange_name="NASDAQ", tickers=tickers
            )
            logger.info(
                f"Filtered NASDAQ tickers successfully. Total tickers: {len(nasdaq_tickers)}"
            )
        return nasdaq_tickers

    @staticmethod
    @time_execution
    def fetch_stock_metadata(ticker: str, app_config: Dict = None) -> Optional[Dict]:
        fmp_config = app_config.get("API_KEYS", {}).get("FMP", {})

        url = f"{fmp_config.get('URL')}/profile/{ticker}?apikey={fmp_config.get('API_TOKEN')}"

        ticker_data = None
        try:
            ticker_data = ApisHandler.get(app_config=app_config, url=url)
        except HttpErrorException as http_error:
            logger.error(f"Fetch Ticker financial data. Http Errpr Reason {http_error}")
        except CustomException as error:
            logger.error(f"etch Ticker financial data failed. Reason {error}")

        if ticker_data and len(ticker_data) > 0:
            stock = ticker_data[0]

            stock_metadata = {
                "symbol": stock.get("symbol", ""),
                "name": stock.get("name", ""),
                "sector": stock.get("sector", ""),
                "industry": stock.get("industry", ""),
                "market_cap": stock.get("mktCap", 0),
            }
            return stock_metadata

        logger.info(f"Ticker data is empty for {ticker}")

        return None

    @staticmethod
    @time_execution
    def fetch_historical_and_technical_indicators(
        app_config: Dict, ticker: str, start_date: str = None, end_date: str = None
    ) -> List:

        fmp_config = app_config.get("API_KEYS", {}).get("FMP", {})
        base_url = fmp_config.get("URL")
        api_token = fmp_config.get("API_TOKEN")

        # Build the historical URL with date range if specified
        date_range = ""
        if start_date and end_date:
            date_range = f"&from={start_date}&to={end_date}"

        logger.info(f"Get historical data for ticker {ticker} ...")
        try:
            # Fetch historical OHLCV data

            historical_data = TechnicalIndicators.get_ohlcv_data(
                base_url=base_url,
                ticker=ticker,
                api_token=api_token,
                date_range=date_range,
            )

            if not historical_data:
                logger.warning(f"Failed to fetch historical data for {ticker}.")
                return None

            # Remove invalid data (zero volume or identical OHLC values)
            historical_data = [
                record
                for record in historical_data
                if record.get("volume", 0) > 0
                and not (
                    record.get("open")
                    == record.get("high")
                    == record.get("low")
                    == record.get("close")
                )
            ]

            if not historical_data:
                logger.warning(
                    f"All retrieved OHLCV data for {ticker} was invalid. Skipping."
                )
                return None

            df = pd.DataFrame(historical_data)
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

            # ✅ Step 2: Compute SMA manually
            df["sma_50"] = TechnicalIndicators.compute_sma(df, 50)
            df["sma_200"] = TechnicalIndicators.compute_sma(df, 200)

            # Fetch Technical Indicators
            indicators_df = TechnicalIndicators.fetch_all_technical_indicator(
                base_url, ticker, api_token, date_range
            )
            if indicators_df.empty:
                logger.warning(
                    f"No technical indicators found for {ticker}. Using only OHLCV data."
                )
                return df  # Return OHLCV if no indicators are found

            # Merge OHLCV and Technical Indicators
            merged_df = df.join(indicators_df, on="date", how="left")

            logger.info(
                f"Fetched and formatted historical data for {ticker} from {start_date} to {end_date}."
            )
            return merged_df

        except HttpErrorException as http_error:
            logger.error(
                f"Failed to fetch historical data for {ticker}. HTTP Error: {http_error}"
            )
        except CustomException as error:
            logger.error(
                f"Failed to fetch historical data for {ticker}. Error: {error}"
            )

        return None

    @staticmethod
    def merge_technical_indicator_into_historical_data(
        ticker: str,
        historical_data: List,
        rsi_data: List,
        macd_data: List,
        sma_data: List,
        bollinger_data: List,
    ) -> List:

        # Prepare the list for formatted historical data
        formatted_historical_data = []

        # Merge technical indicators into historical data
        for i, record in enumerate(historical_data):
            formatted_record = {
                "symbol": ticker,
                "date": datetime.strptime(record["date"], "%Y-%m-%d").date(),
                "open": float(record.get("open", 0)),
                "high": float(record.get("high", 0)),
                "low": float(record.get("low", 0)),
                "close": float(record.get("close", 0)),
                "volume": int(record.get("volume", 0)),
                "rsi": (
                    float(rsi_data[i].get("rsi", 0))
                    if rsi_data and i < len(rsi_data)
                    else None
                ),
                "macd": (
                    float(macd_data[i].get("macd", 0))
                    if macd_data and i < len(macd_data)
                    else None
                ),
                "sma_50": (
                    float(sma_data[i].get("sma_50", 0))
                    if sma_data and i < len(sma_data)
                    else None
                ),
                "sma_200": (
                    float(sma_data[i].get("sma_200", 0))
                    if sma_data and i < len(sma_data)
                    else None
                ),
                "bollinger_upper": (
                    float(bollinger_data[i].get("bollinger_upper", 0))
                    if bollinger_data and i < len(bollinger_data)
                    else None
                ),
                "bollinger_lower": (
                    float(bollinger_data[i].get("bollinger_lower", 0))
                    if bollinger_data and i < len(bollinger_data)
                    else None
                ),
            }

            formatted_historical_data.append(formatted_record)
