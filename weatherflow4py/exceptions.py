class TokenError(Exception):
    def __init__(self, message="APIToken not set"):
        super().__init__(message)
