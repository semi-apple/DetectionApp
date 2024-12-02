import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)
import pytest
from exceptions.user_login_exception import UserNotFoundException, IncorrectPasswordException


def test_user_not_found_exception_default_message():
    """Test UserNotFoundException with default message."""
    username = "test_user"
    with pytest.raises(UserNotFoundException) as exc_info:
        raise UserNotFoundException(username)
    assert str(exc_info.value) == f"{username} -> User not found."


def test_user_not_found_exception_custom_message():
    """Test UserNotFoundException with custom message."""
    username = "test_user"
    custom_message = "Custom message: User does not exist."
    with pytest.raises(UserNotFoundException) as exc_info:
        raise UserNotFoundException(username, custom_message)
    assert str(exc_info.value) == f"{username} -> {custom_message}"


def test_incorrect_password_exception_default_message():
    """Test IncorrectPasswordException with default message."""
    username = "test_user"
    with pytest.raises(IncorrectPasswordException) as exc_info:
        raise IncorrectPasswordException(username)
    assert str(exc_info.value) == f"{username} -> Incorrect password! Please try again."


def test_incorrect_password_exception_custom_message():
    """Test IncorrectPasswordException with custom message."""
    username = "test_user"
    custom_message = "Custom message: Password is invalid."
    with pytest.raises(IncorrectPasswordException) as exc_info:
        raise IncorrectPasswordException(username, custom_message)
    assert str(exc_info.value) == f"{username} -> {custom_message}"

