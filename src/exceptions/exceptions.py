class CustomException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class HttpErrorException(CustomException):
    def __init__(self, message):
        super().__init__(message)
