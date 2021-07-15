__all__ = ["RegistryException"]


class RegistryException(Exception):
    """Exception class for all registry errors."""

    def __init__(self, message):
        """
        Init.

        Args:
            message: exception message
        """
        super().__init__(message)
