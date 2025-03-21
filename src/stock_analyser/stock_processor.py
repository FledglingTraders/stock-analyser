from typing import Dict

from src.services.data_collector import DataCollector
from src.services.technical_indicators import TechnicalIndicators
from src.settings.shared import get_app_config
from src.settings.shared import logger
from src.services.helper import HelperMethods


class StockAnalyser:
    def __init__(self) -> None:
        self.app_config = get_app_config()

    def start_process(
        self, app_config: dict = {}, start_date: str = None, end_date: str = None
    ):
        def __init__(self) -> None:
            self.app_config = get_app_config()
            self.start_date = start_date
            self.end_date = end_date

        # TODO
        # 1. Fetch the list of NASDAQ tickers
        # 2. Persist the list of NASDAQ tickers on my database using stock_analyser_lib
        # 3. Fetch financial data of each ticker using pool of threads for each ticker
        # 4. Persist the financial data on my database using stock_analyser_lib
        # 5. Use visualisation tools to display the data (powerBI, Tableau, elk etc)

        stock_list = DataCollector.fetch_nasdaq_tickers_list(app_config=app_config)

        if stock_list and len(stock_list) > 0:

            for stock in stock_list:
                if stock == "AAPL":
                    stock_metadata = DataCollector.fetch_stock_metadata(
                        ticker=stock, app_config=app_config
                    )
                    historical_data = (
                        DataCollector.fetch_historical_and_technical_indicators(
                            ticker=stock, app_config=app_config
                        )
                    )

        else:
            logger.error("No stock data found")
