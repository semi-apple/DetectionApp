"""
This file defines exceptions that would happen while loging in.

Classes:
- LotNumberNotFoundException: Cannot find lot number while detecting.
- SerialNumberNotFoundException: Cannot find serial number while detecting.
- LogoNotFoundException: Cannot find logo while detecting.
"""


class LotNumberNotFoundException(Exception):
    """
    Exception raised for error when lot number not found.

    Attributes:
        username -- thread that causes error.
        message -- explanation of the error.
    """

    def __init__(self, message='Lot Number Not Found.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class SerialNumberNotFoundException(Exception):
    """
    Exception raised for error when serial number not found/

    Attributes:
        username -- thread that causes error.
        message -- explanation of the error.
    """

    def __init__(self, message='Serial Number Not Found.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class LogoNotFoundException(Exception):
    """
    Exception raised for error when logo not found/

    Attributes:
        username -- thread that causes error.
        message -- explanation of the error.
    """

    def __init__(self, message='Logo Not Found.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'