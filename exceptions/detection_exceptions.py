"""
This file defines exceptions that would happen while loging in.

Classes:
- LotNumberNotFoundException: Cannot find lot number while detecting.
- SerialNumberNotFoundException: Cannot find serial number while detecting.
- LogoNotFoundException: Cannot find logo while detecting.
- BarcodeNotFoundException: Cannot find barcode.
- DetectionException: Error while detecting.
"""


class BarcodeNotFoundException(Exception):
    """
    Exception raised for error when barcode not found.

    Attributes:
        username -- thread that causes error.
        message -- explanation of the error.
    """

    def __init__(self, message='Barcode Not Found.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
    

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
    

class AssetNumberNotFoundException(Exception):
    """
    Exception raised for error when serial number not found/

    Attributes:
        username -- thread that causes error.
        message -- explanation of the error.
    """

    def __init__(self, message='Asset Number Not Found.'):
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


class DetectionException(Exception):
    """
    Exception raised when a detection error occurs.

    Attributes:
        message -- explanation of the error
        original_exception -- optional: original exception that caused the detection failure
    """
    def __init__(self, message="Detection Error.", original_exception=None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)

    def __str__(self):
        if self.original_exception:
            return f"{self.message} -- Caused by: {repr(self.original_exception)})"
        return self.message
    

class LaptopNotDetectedException(Exception):
    """
    Exception raised when laptop is not detected

    Attributes:
        username -- thread that causes error.
        message -- explanation of the error.
    """
    def __init__(self, message='Laptop Not Detected.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
    