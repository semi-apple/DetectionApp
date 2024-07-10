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

### App
Contains the main application logic, including the user interface and core functionality.

### DataAnnotation
Includes tools and scripts for annotating the dataset, helping in marking scratches on notebook images.

### Dataset
Holds the dataset of notebook images, including both annotated and raw images used for training and testing.

### IO
Utility scripts for handling input and output operations, such as reading images and saving results.

### Widget
Components and widgets used in the application interface.

### images
Sample images used in the project for testing and demonstration purposes.

## Installation
Caution: You may need to run the code on pycharm since there might be some library dependency problem.

1. Clone the repository:
   ```bash
   git clone https://github.com/semi-apple/DetectionApp.git
   ```
   
2. Install libraries:
   ```bash
   pip install numpy
   pip install plantcv
   pip install opencv-python
   pip install pyqt5
   pip install ultralytics
   pip install easyocr
   ```
   
## Usage
To run the main application, use the following command:
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

