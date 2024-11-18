# """
# Model Name: test_video_thread.py
# Description: Automated tests for VideoThread.py
# Author: Kun
# Last Modified: 18 Nov 2024
# """
#
# import unittest
# from unittest.mock import patch
# from widgets.video_thread import VideoThread
# import cv2 as cv
# import numpy as np
#
#
# class TestVideoThread(unittest.TestCase):
#     @patch('cv2.VideoCapture')
#     def test_camera_init_successful(self, mock_video_capture):
#         mock_video_capture.return_value.isOpened.return_value = True
#         video_thread = VideoThread(camera_port=0)
#         video_thread.run()
#
#         mock_video_capture.assert_called_once_with(0, cv.CAP_DSHOW)
#         self.assertTrue(video_thread.running)
#         video_thread.stop()
#
#     @patch('cv2.VideoCapture')
#     def test_camera_init_failure(self, mock_video_capture):
#         """Test camera initialization failure."""
#         mock_video_capture.return_value.isOpened.return_value = False
#         video_thread = VideoThread(camera_port=1)
#         video_thread.run()
#         mock_video_capture.assert_called_once_with(1, cv.CAP_DSHOW)
#         self.assertFalse(video_thread.running)
#         video_thread.stop()
#
#     @patch('cv2.VideoCapture')
#     def test_signal_emission(self, mock_video_capture):
#         """Test if the change_pixmap_signal is emitted with correct data"""
#         mock_video_capture.return_value.isOpened.return_value = True
#         mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)  # black frame
#         mock_video_capture.return_value.read.return_value = (True, mock_frame)
#
#         video_thread = VideoThread(camera_port=0)
