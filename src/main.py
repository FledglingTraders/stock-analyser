from settings.shared import set_app_config, get_app_config
from stock_analyser.stock_processor import StockAnalyser
from settings.shared import logger


def main():
    logger.info('Start processing')
    set_app_config()
    app_config = get_app_config()
    analyser = StockAnalyser()
    analyser.start_process(app_config=app_config)


if __name__ == "__main__":
    main()
