# DetectionApp

This repository contains the implementation of Damaged information Detection, a project aimed at automatically detecting
scratches on random notebooks using image processing and machine learning techniques.

## Table of Contents

- [Notebook DetectionAPP](#notebook-scratch-detection)
    - [Table of Contents](#table-of-contents)
    - [Directory Structure](#directory-structure)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Contributing](#contributing)
    - [License](#license)
    - [Contact](#contact)

## Directory Structure

### application
Contains the main application logic, including the user interface and controller class.

### documentations
Notebooks and pdfs about the project (how to train/valid model, etc,.).

### exceptions
All exceptions that would meet during detecting.

### IO
Utility scripts for handling input and output operations, such as training logic, reading images, saving results, uploading function, etc.

### models
Stores models for detecting, including logo detection model, serial number detection model, defect detection model, etc.

### tests
Test scripts.

### UI
UI interface.

### Widgets
Core function for interaction, including menubar, control panel, login, video base and video thread.

## Installation

Clone the repository:
   ```bash
   git clone https://github.com/semi-apple/DetectionApp.git
   ```
   
Run script to install libraries:
   ```bash
   ./instal.bat
   ```
   
Or manually install all libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To run the main application, click `Detection.app` or use the following command:
  ```bash
  python main.py
  ```

## Contributing
If you would like to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch: ```git checkout -b my-feature-branch.```
Make your changes and commit them: ```git commit -m 'Add some feature'```.
Push to the branch: ```git push origin my-feature-branch```.
Submit a ```pull``` request.

## Contact

For any inquiries, please contact Kun Zhou at kun.zhou@uq.edu.au.

