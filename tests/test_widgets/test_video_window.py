import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)

from unittest.mock import patch, MagicMock
import numpy as np
from widgets.video_window import save_to_pdf, VideoBase
from interfaces.classes import Defect


def test_save_to_pdf():
    """Test that save_to_pdf generates a PDF correctly."""
    defects_list = [
        ([Defect(image=np.zeros((100, 100, 3), dtype=np.uint8), cls="scratch", xyxy=(10, 10, 50, 50))], 0)
    ]
    name = "test_pdf"

    with patch("widgets.video_window.canvas.Canvas") as MockCanvas:
        mock_canvas_instance = MockCanvas.return_value

        save_to_pdf(defects_list, name)

        # Assert that canvas methods are called
        mock_canvas_instance.drawString.assert_called()  # Verify text was written
        mock_canvas_instance.drawImage.assert_called()  # Verify image was added
        mock_canvas_instance.save.assert_called_once()  # Verify PDF was saved


def test_start_detection(mocker):
    """Test that start_detection initializes video capture threads."""
    mock_labels = [MagicMock() for _ in range(6)]
    mock_buttons = {
        "detect_button": MagicMock(),
        "capture_button": MagicMock(),
        "stop_button": MagicMock(),
    }

    # Mock all required models
    mock_models = {
        "top_bottom": MagicMock(),
        "lot_asset_barcode": MagicMock(),
        "logo": MagicMock(),
        "lot": MagicMock(),
        "serial_region": MagicMock(),
        "serial": MagicMock(),
        "barcode": MagicMock(),
        "keyboard": MagicMock(),
        "screen": MagicMock(),
    }

    # Mock VideoCapture
    mock_video_capture_instance = MagicMock()
    mock_video_capture_instance.start = MagicMock()
    mocker.patch(
        "widgets.video_window.VideoCapture",
        side_effect=lambda *args, **kwargs: MagicMock(start=MagicMock())
    )

    # Initialize VideoBase with mock models
    video_base = VideoBase(thread_labels=mock_labels, buttons=mock_buttons, models=mock_models)

    video_base.start_detection()

    # Assert that threads are initialized
    assert len(video_base.threads) == len(mock_labels)
    for thread in video_base.threads:
        thread.start.assert_called_once()


def test_detect_images(mocker):
    """Test that detect_images processes input correctly."""
    mock_model = MagicMock()
    mock_model.names = {0: 'asset', 1: 'lot', 2: 'barcode'}
    mock_model.return_value = MagicMock()

    mock_models = {
        "top_bottom": MagicMock(),
        "lot_asset_barcode": mock_model,
        "logo": MagicMock(),
        "lot": MagicMock(),
        "serial_region": MagicMock(),
        "serial": MagicMock(),
        "barcode": MagicMock(),
        "keyboard": MagicMock(),
        "screen": MagicMock(),
    }

    mock_buttons = {
        "detect_button": MagicMock(),
        "capture_button": MagicMock(),
        "stop_button": MagicMock(),
    }

    mocker.patch("interfaces.detection_functions.segment_with_sahi", return_value=(None, [1, 0], [MagicMock()]))

    video_base = VideoBase(thread_labels=[], buttons=mock_buttons, models=mock_models)

    original_imgs = [(np.zeros((480, 640, 3), dtype=np.uint8), 0)]
    detected_imgs, detected_features, defects_list = video_base.detect_images(original_imgs)

    assert len(detected_imgs) == 1
    assert detected_features["detected_info"] == [[1, 0]]
    assert len(defects_list) == 1
#
#
# def test_capture_images(mocker):
#     """Test that capture_images captures and processes images correctly."""
#     mock_labels = [MagicMock() for _ in range(6)]
#     mock_buttons = {
#         "detect_button": MagicMock(),
#         "capture_button": MagicMock(),
#         "stop_button": MagicMock(),
#     }
#
#     video_base = VideoBase(thread_labels=mock_labels, buttons=mock_buttons, models={})
#
#     # Mock threads
#     mock_thread = MagicMock()
#     mock_thread.capture.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
#     video_base.threads = [mock_thread for _ in range(6)]
#
#     # Mock detect_images and save_to_pdf
#     mocker.patch("your_module.VideoBase.detect_images", return_value=([], {}, []))
#     mocker.patch("your_module.save_to_pdf")
#
#     video_base.capture_images()
#
#     # Assert that capture is called for each thread
#     for thread in video_base.threads:
#         thread.capture.assert_called_once()
#
#     # Assert that save_to_pdf was called
#     save_to_pdf = mocker.patch("your_module.save_to_pdf")
#     save_to_pdf.assert_called_once()
#
#
# def test_stop_detection():
#     """Test that stop_detection stops threads and clears labels."""
#     mock_labels = [MagicMock() for _ in range(6)]
#     mock_buttons = {
#         "detect_button": MagicMock(),
#         "capture_button": MagicMock(),
#         "stop_button": MagicMock(),
#     }
#
#     video_base = VideoBase(thread_labels=mock_labels, buttons=mock_buttons, models={})
#
#     # Mock threads
#     mock_thread = MagicMock()
#     video_base.threads = [mock_thread for _ in range(6)]
#
#     video_base.stop_detection()
#
#     # Assert that threads are stopped
#     for thread in video_base.threads:
#         thread.stop.assert_called_once()
#
#     # Assert that labels are cleared
#     for label in mock_labels:
#         label.clear.assert_called_once()
#
#     # Ensure threads list is empty
#     assert len(video_base.threads) == 0
#
#
#
