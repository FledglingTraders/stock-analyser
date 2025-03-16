import logging
import json

# Create logget with a stdout handler and a formater
logger = logging.getLogger("stock_analyser")
console = logging.StreamHandler()

formater = logging.Formatter(
    "%(asctime)s %(levelname)-8s | %(filename)-25s | %(lineno)3d | %(message)s"
)

# Tell the handler to use this format
console.setFormatter(formater)
console.setLevel(logging.INFO)
logger.addHandler(console)
logger.setLevel(logging.INFO)
app_config = {}


def set_app_config(config_file_path: str = "config/config.json"):
    global app_config

    with open(config_file_path) as f:
        app_config = json.load(f)


def get_app_config():
    global app_config
    return app_config
