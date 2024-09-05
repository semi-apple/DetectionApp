"""
Google Drive Uploader

This script provides functionalities to interact with Google Drive using PyDrive.
It includes a class `GoogleDriveUploader` for handling authentication, folder creation,
and file uploading to Google Drive.

Classes:
- GoogleDriveUploader: Manages authentication and file operations with Google Drive.

Author: Kun
Last Modified: 05 Sep 2024
"""
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

currentPath = os.path.dirname(os.path.abspath(__file__))


class GoogleDriveUploader:
    """
    Handles authentication and file operations with Google Drive using PyDrive.

    Attributes:
    - gauth: GoogleAuth instance for authentication.
    - drive: GoogleDrive instance for accessing Google Drive.

    Methods:
    - __init__(): Initializes GoogleAuth and authenticates user credentials.
    - authenticate(): Authenticates Google credentials and saves them to a file.
    - create_folder(folder_name, parent_folder_id='1K6Fj11F46BZMFj7R4KLsew5E0v7499l-'):
      Creates a folder on Google Drive if it doesn't already exist.
    - upload_folder(folder_name, local_folder, parent_folder_id='1K6Fj11F46BZMFj7R4KLsew5E0v7499l-'):
      Uploads a local folder to Google Drive, creating necessary folders as needed.
    - upload_file(file_path, parent_folder_id=None): Uploads a file to a specified folder on Google Drive.
    """
    def __init__(self):
        """
        Initializes GoogleAuth and authenticates user credentials.
        """
        self.gauth = GoogleAuth()
        self.authenticate()
        self.drive = GoogleDrive(self.gauth)

    def authenticate(self):
        """
        Authenticates Google credentials and saves them to a file.
        """
        # Try to load saved credentials
        gauth_file = os.path.join(currentPath, "mycreds.txt")
        if os.path.exists(gauth_file):
            self.gauth.LoadCredentialsFile(gauth_file)

        # Check if credentials are valid
        if self.gauth.credentials is None:
            # Authenticate if not loaded
            self.gauth.LocalWebserverAuth()

        elif self.gauth.access_token_expired:
            # Refresh token if expired
            self.gauth.Refresh()
        else:
            # Initialize from existing credentials
            self.gauth.Authorize()

        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile(gauth_file)

    def create_folder(self, folder_name, parent_folder_id='1K6Fj11F46BZMFj7R4KLsew5E0v7499l-'):
        """
        Creates a folder on Google Drive if it doesn't already exist.

        Args:
        - folder_name (str): Name of the folder to create.
        - parent_folder_id (str): ID of the parent folder where new folder will be created.

        Returns:
        - tuple: (bool, str) indicating success (True/False) and folder ID.
        """
        # Check if the folder already exists
        query = (f"title='{folder_name}' and '{parent_folder_id}' in parents and trashed=false and "
                 f"mimeType='application/vnd.google-apps.folder'")
        existing_folders = self.drive.ListFile({'q': query}).GetList()

        if existing_folders:
            print(f'Folder "{folder_name}" already exists in parent folder with ID: {parent_folder_id}')
            return False, existing_folders[0]['id']

        # If folder does not exist, create it
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_folder_id}]
        }

        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()
        print(f'Folder "{folder_name}" created with ID: {folder["id"]}')
        return True, folder['id']

    def upload_folder(self, folder_name, local_folder, parent_folder_id='1K6Fj11F46BZMFj7R4KLsew5E0v7499l-'):
        """
        Uploads a local folder to Google Drive, creating necessary folders as needed.

        Args:
        - folder_name (str): Name of the folder to create/upload.
        - local_folder (str): Local path of the folder to upload.
        - parent_folder_id (str): ID of the parent folder where new folder will be created/uploaded.
        """
        for root, dirs, files in os.walk(local_folder):
            flag, current_folder_id = self.create_folder(folder_name, parent_folder_id)
            if not flag:
                return
            for filename in files:
                local_path = os.path.join(root, filename)
                self.upload_file(local_path, current_folder_id)

    def upload_file(self, file_path, parent_folder_id=None):
        """
        Uploads a file to a specified folder on Google Drive.

        Args:
        - file_path (str): Local path of the file to upload.
        - parent_folder_id (str): ID of the parent folder where file will be uploaded.
        """
        filename = os.path.basename(file_path)
        gfile = self.drive.CreateFile({'parents': [{'id': parent_folder_id}]})
        gfile.SetContentFile(file_path)
        gfile['title'] = filename
        gfile.Upload()
        print(f'Uploaded {filename} to Google Drive')
        print(f'File location in Google Drive: {gfile["alternateLink"]}')


if __name__ == "__main__":
    uploader = GoogleDriveUploader()
