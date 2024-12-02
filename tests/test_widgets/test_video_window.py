# import pytest
# from unittest.mock import MagicMock, patch
# import numpy as np
# from PyQt5.QtGui import QPixmap, QImage
# from PyQt5.QtWidgets import QPushButton, QLabel
# import os
# import sys
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.abspath(os.path.join(current_dir, '../../'))
# sys.path.append(project_root)
# from widgets.video_window import VideoBase
#
# @pytest.fixture
# def setup_videobase():
#     thread_labels = [MagicMock(spec=QLabel) for _ in range(6)]
#     buttons = {
#         'detect_button': MagicMock(spec=QPushButton),
#         'capture_button': MagicMock(spec=QPushButton),
#         'stop_button': MagicMock(spec=QPushButton),
#     }
#
#     models = {
#         'top_bottom': MagicMock(),
#         'logo': MagicMock(),
#         'lot': MagicMock(),
#         'serial_region': MagicMock(),
#         'serial': MagicMock(),
#         'barcode': MagicMock(),
#         'keyboard': MagicMock(),
#         'screen': MagicMock(),
#     }
#
#     vb = VideoBase(thread_labels=thread_labels, buttons=buttons, models=models)
#     return vb, thread_labels, buttons, models
#
# def test_start_detection(setup_videobase):
#     vb, thread_labels, buttons, models = setup_videobase
#
#     with patch('main.VideoWindow.VideoThread') as MockVideoThread:
#         mock_thread = MagicMock()
#         MockVideoThread.return_value = mock_thread
#
#         vb.start_detection()
#
#         # assert len(vb.threads) == 6
#         # assert MockVideoThread.call_count == 6
#         for i, thread in enumerate(vb.threads):
#             thread.start.assert_called_once()
#             thread.change_pixmap_signal.connect.assert_called_with(getattr(vb, f'set_image{i}'))
#
# def test_stop_detection(setup_videobase):
#     vb, thread_labels, buttons, models = setup_videobase
#
#     mock_thread = MagicMock()
#     vb.threads = [mock_thread for _ in range(6)]
#
#     vb.stop_detection()
#
#     for thread in vb.threads:
#         thread.stop.assert_called_once()
#
#     assert vb.threads == []
#
#     for label in thread_labels:
#         label.clear.assert_called_once()
#
# def test_display_image_on_label(setup_videobase):
#     vb, thread_labels, buttons, models = setup_videobase
#
#     mock_image_path = 'test_image.jpg'
#     mock_label = MagicMock(spec=QLabel)
#
#     fake_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#     with patch('cv2.imread', return_value=fake_image), patch('cv2.cvtColor', return_value=fake_image):
#         vb.display_image_on_label(mock_image_path, mock_label)
#
#     mock_label.setPixmap.assert_called_once()
#
# def test_detect_images(setup_videobase):
#     vb, thread_labels, buttons, models = setup_videobase
#
#     fake_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#     original_imgs = [(fake_image, 0), (fake_image, 1)]
#
#     with patch('main.VideoWindow.detect_logo', return_value='MockLogo') as mock_detect_logo, \
#          patch('main.VideoWindow.detect_lot', return_value='MockLot') as mock_detect_lot, \
#          patch('main.VideoWindow.detect_serial', return_value='MockSerial') as mock_detect_serial, \
#          patch('main.VideoWindow.detect_keyboard', return_value=(fake_image, {'keyboard_defects': 1})), \
#          patch('main.VideoWindow.segment_with_sahi', return_value=(fake_image, {'defects': 1})):
#
#         detected_imgs, detected_features = vb.detect_images(original_imgs)
#
#         assert len(detected_imgs) == len(original_imgs)
#         assert 'logo' in detected_features
#         assert detected_features['logo'] == 'MockLogo'
#         assert detected_features['lot'] == 'MockLot'
#         assert detected_features['serial'] == 'MockSerial'
#
# def test_capture_images(setup_videobase):
#     vb, thread_labels, buttons, models = setup_videobase
#
#     fake_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
#     mock_thread = MagicMock()
#     mock_thread.running = True
#     mock_thread.capture.return_value = fake_image
#     vb.threads = [mock_thread]
#
#     with patch.object(vb, 'detect_images', return_value=([], {})) as mock_detect_images:
#         vb.capture_images()
#
#         mock_thread.capture.assert_called_once()
#         mock_detect_images.assert_called_once()
#
#
