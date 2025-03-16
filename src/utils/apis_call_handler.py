import requests
from typing import Dict

from src.settings.shared import logger
from src.utils.decorators import retry
from src.exceptions.exceptions import HttpErrorException, CustomException


class ApisHandler:
    @staticmethod
    def get(url: str = "", **kwrgs) -> Dict:
        try:
            response = requests.get(url=url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_error:
            raise HttpErrorException(
                message=f"Http Error, reason {http_error}"
            ) from http_error
        except Exception as error:
            raise CustomException(message=f"Api Call failed, reason {error}") from error
