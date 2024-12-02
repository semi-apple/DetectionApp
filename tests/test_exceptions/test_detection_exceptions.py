import pytest
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)
from exceptions.detection_exceptions import (
    BarcodeNotFoundException,
    LotNumberNotFoundException,
    SerialNumberNotFoundException,
    LogoNotFoundException,
    DetectionException,
)


def test_barcode_not_found_exception():
    """Test BarcodeNotFoundException behavior."""
    with pytest.raises(BarcodeNotFoundException) as exc_info:
        raise BarcodeNotFoundException()
    assert str(exc_info.value) == "Barcode Not Found."


def test_barcode_not_found_exception_custom_message():
    """Test BarcodeNotFoundException with a custom message."""
    custom_message = "Custom Barcode Error Message."
    with pytest.raises(BarcodeNotFoundException) as exc_info:
        raise BarcodeNotFoundException(custom_message)
    assert str(exc_info.value) == custom_message


def test_lot_number_not_found_exception():
    """Test LotNumberNotFoundException behavior."""
    with pytest.raises(LotNumberNotFoundException) as exc_info:
        raise LotNumberNotFoundException()
    assert str(exc_info.value) == "Lot Number Not Found."


def test_lot_number_not_found_exception_custom_message():
    """Test LotNumberNotFoundException with a custom message."""
    custom_message = "Custom Lot Number Error Message."
    with pytest.raises(LotNumberNotFoundException) as exc_info:
        raise LotNumberNotFoundException(custom_message)
    assert str(exc_info.value) == custom_message


def test_serial_number_not_found_exception():
    """Test SerialNumberNotFoundException behavior."""
    with pytest.raises(SerialNumberNotFoundException) as exc_info:
        raise SerialNumberNotFoundException()
    assert str(exc_info.value) == "Serial Number Not Found."


def test_serial_number_not_found_exception_custom_message():
    """Test SerialNumberNotFoundException with a custom message."""
    custom_message = "Custom Serial Number Error Message."
    with pytest.raises(SerialNumberNotFoundException) as exc_info:
        raise SerialNumberNotFoundException(custom_message)
    assert str(exc_info.value) == custom_message


def test_logo_not_found_exception():
    """Test LogoNotFoundException behavior."""
    with pytest.raises(LogoNotFoundException) as exc_info:
        raise LogoNotFoundException()
    assert str(exc_info.value) == "Logo Not Found."


def test_logo_not_found_exception_custom_message():
    """Test LogoNotFoundException with a custom message."""
    custom_message = "Custom Logo Error Message."
    with pytest.raises(LogoNotFoundException) as exc_info:
        raise LogoNotFoundException(custom_message)
    assert str(exc_info.value) == custom_message


def test_detection_exception():
    """Test DetectionException behavior."""
    with pytest.raises(DetectionException) as exc_info:
        raise DetectionException()
    assert str(exc_info.value) == "Detection Error."


def test_detection_exception_custom_message():
    """Test DetectionException with a custom message."""
    custom_message = "Custom Detection Error Message."
    with pytest.raises(DetectionException) as exc_info:
        raise DetectionException(custom_message)
    assert str(exc_info.value) == custom_message
