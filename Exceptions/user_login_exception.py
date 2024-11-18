"""
This file defines exceptions that would happen while loging in.

Classes:
- UserNotFoundException: User does not exist in database.
- IncorrectPasswordException: User does exist in database with incorrect password input.
"""


class UserNotFoundException(Exception):
    """
    Exception raised for error in the input user.

    Attributes:
        username -- input username which caused the error.
        message -- explanation of the error.
    """

    def __init__(self, username, message='User not found.'):
        self.username = username
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.username} -> {self.message}'


class IncorrectPasswordException(Exception):
    """
    Exception raised for error with incorrect password input.

    Attributes:
        username -- input username which caused the error.
        message -- explanation of the error.
    """

    def __init__(self, username, message='Incorrect password! Please try again.'):
        self.username = username
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.username} -> {self.message}'
