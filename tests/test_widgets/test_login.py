"""
Model name: test_login.py
Description: Automated tests for Login
Last Modified: 18 Nov 2024
"""

import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from unittest.mock import patch

from Widgets.Login import LoginWindow


class TestLoginWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.login = LoginWindow()
        self.login.accepted.connect(self.on_login_accepted)
        self.login_success = False
        self.username_received = None
        self.user_level_received = None

    def on_login_accepted(self, username, user_level):
        """capture the emitted signal for login"""
        self.login_success = True
        self.username_received = username
        self.user_level_received = user_level

    def test_ui_element_exist(self):
        """Test if all UI elements are present"""
        self.assertIsNotNone(self.login.label_username, 'Username label should exist.')
        self.assertIsNotNone(self.login.label_password, 'Password label should exist.')
        self.assertIsNotNone(self.login.text_username, 'Username text should exist.')
        self.assertIsNotNone(self.login.text_password, 'Password text should exist.')
        self.assertIsNotNone(self.login.button_login, 'Login button should exist.')

    def test_login_successful(self):
        """Test a successful login scenario"""
        QTest.keyClicks(self.login.text_username, 'Admin')
        QTest.keyClicks(self.login.text_password, '123456')
        QTest.mouseClick(self.login.button_login, Qt.LeftButton)

        self.assertTrue(self.login_success, 'Login should be successful')
        self.assertEqual(self.username_received, 'Admin', 'Username should match input')
        self.assertEqual(self.user_level_received, 0, "User level should match Admin's level")

    @patch('Widgets.Login.QMessageBox.warning')
    def test_login_failed_wrong_password(self, mock_warning):
        """Test login failure due to incorrect password"""
        QTest.keyClicks(self.login.text_username, 'Admin')
        QTest.keyClicks(self.login.text_password, 'wrong_password')
        QTest.mouseClick(self.login.button_login, Qt.LeftButton)

        self.assertFalse(self.login_success, 'Login should fail with incorrect password')
        mock_warning.assert_called_once_with(self.login, 'Login', 'Admin -> Incorrect password! Please try again.')

    @patch('Widgets.Login.QMessageBox.warning')
    def test_login_failed_user_not_found(self, mock_warning):
        """Test login failure due to incorrect password"""
        QTest.keyClicks(self.login.text_username, 'UnknownUser')
        QTest.keyClicks(self.login.text_password, '123456')
        QTest.mouseClick(self.login.button_login, Qt.LeftButton)

        self.assertFalse(self.login_success, 'Login should fail with unknown user')
        mock_warning.assert_called_once_with(self.login, 'Login', 'UnknownUser -> User not found.')

    def tearDown(self):
        self.login.close()

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()


if __name__ == '__main__':
    unittest.main()
