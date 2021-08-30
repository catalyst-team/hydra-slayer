__all__ = ["RegistryException"]


class RegistryException(Exception):
    """Exception class for all registry errors.

    Args:
        message: exception message
    """

    def __init__(self, message: str):
        super().__init__(message)
