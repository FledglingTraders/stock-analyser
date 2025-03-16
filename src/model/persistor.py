from stock_analyser_lib.repositories.stock_repo import StockRepository
from stock_analyser_lib.repositories.historical_data_repo import (
    HistoricalDataRepository,
)


class StockDataHelper:
    @staticmethod
    def persist_stock_data(stock_data: dict):
        StockRepository.add_stock(**stock_data)

    @staticmethod
    def persist_bulk_stock_data(stock_data: list):
        StockRepository.bulk_upsert_historical_data(stock_data)


class HistoricalDataHelper:
    @staticmethod
    def persist_historical_data(data: dict):
        HistoricalDataRepository.add_historical_data(**data)

    @staticmethod
    def persist_bulk_historical_data(data: list):
        HistoricalDataRepository.bulk_upsert_historical_data(data)
