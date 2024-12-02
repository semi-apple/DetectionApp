import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)
import os
import pytest
import csv
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QLineEdit, QPushButton
from IO.defect import Defect
from widgets.panel import save_to_pdf, PanelBase
import numpy as np
import shutil
from pathlib import Path
import cv2 as cv


@pytest.fixture
def panel_base_setup():
    """Fixture to set up PanelBase with mocked input lines and buttons."""
    input_lines = {
        'model_input': MagicMock(spec=QLineEdit),
        'lot_number_input': MagicMock(spec=QLineEdit),
        'serial_number_input': MagicMock(spec=QLineEdit),
        'scratch_input': MagicMock(spec=QLineEdit),
        'stain_input': MagicMock(spec=QLineEdit),
        'grade_input': MagicMock(spec=QLineEdit),
    }

    panel_buttons = {
        'save_button': MagicMock(spec=QPushButton),
        'clear_button': MagicMock(spec=QPushButton),
    }

    dataset_dir = os.path.join(project_root, 'dataset')
    if os.path.exists(dataset_dir):
        # Remove all files and subdirectories in the dataset directory
        shutil.rmtree(dataset_dir)

    # Recreate an empty dataset directory
    os.makedirs(dataset_dir, exist_ok=True)
    panel = PanelBase(input_lines, panel_buttons)
    panel.save_directory = str(dataset_dir)

    return panel, input_lines, panel_buttons, dataset_dir


def test_save_to_dataset(panel_base_setup):
    """Test that save_to_dataset writes correct data to CSV."""
    panel, input_lines, _, dataset_dir = panel_base_setup

    # Mock input text
    input_lines['model_input'].text.return_value = "TestModel"
    input_lines['lot_number_input'].text.return_value = "Lot123"
    input_lines['serial_number_input'].text.return_value = "Serial456"
    input_lines['scratch_input'].text.return_value = "5"
    input_lines['stain_input'].text.return_value = "3"
    input_lines['grade_input'].text.return_value = "A"

    # Save data
    panel.save_to_dataset()

    # Verify CSV content
    dataset_file = os.path.join(dataset_dir, 'dataset.csv')
    assert os.path.exists(dataset_file), "Dataset CSV file should exist."

    with open(dataset_file, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    assert len(rows) == 1, "CSV should contain one row."
    assert rows[0] == {
        'model': "TestModel",
        'lot number': "Lot123",
        'serial number': "Serial456",
        'scratch': "5",
        'stain': "3",
        'grade': "A"
    }, "CSV row data does not match expected values."


def test_clear_all_inputs(panel_base_setup):
    """Test that clear_all_inputs clears all input fields."""
    panel, input_lines, _, _ = panel_base_setup

    # Call clear_all_inputs
    panel.clear_all_inputs()

    # Check that all input lines are cleared
    for input_line in input_lines.values():
        input_line.clear.assert_called_once()


def test_set_detected_features(panel_base_setup):
    """Test set_detected_features updates input fields correctly."""
    panel, input_lines, _, _ = panel_base_setup

    detected_features = {
        'logo': "TestLogo",
        'lot': "TestLot\n",
        'serial': "TestSerial\n",
        'defects': [
            ((3, 2), 0),  # 3 scratches, 2 stains
            ((1, 4), 1),  # 1 scratch, 4 stains
        ]
    }

    panel.set_detected_features(detected_features)

    # Check input values
    input_lines['model_input'].setText.assert_called_with("TestLogo")
    input_lines['lot_number_input'].setText.assert_called_with("TestLot")
    input_lines['serial_number_input'].setText.assert_called_with("TestSerial")
    input_lines['scratch_input'].setText.assert_called_with("4")
    input_lines['stain_input'].setText.assert_called_with("6")
    input_lines['grade_input'].setText.assert_called_with("C")


def test_save_to_pdf():
    """Test save_to_pdf generates a PDF with defect information."""
    pdf_dir = Path(project_root) / 'dataset'
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_name = pdf_dir / "test.pdf"

    # Create mock defect data
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    defect = Defect(image=image, cls="stain", xyxy=(10, 10, 50, 50))

    # Call save_to_pdf
    save_to_pdf([defect], str(pdf_name.stem))

    # Verify PDF file is created
    assert pdf_name.exists(), "PDF file should be created."

    # You can use a library like PyPDF2 to parse and validate PDF contents if needed.


def test_save_handles_empty_images(panel_base_setup):
    """Test save gracefully handles empty images."""
    panel, input_lines, _, dataset_dir = panel_base_setup

    # Mock all input lines to return an empty string
    for input_line in input_lines.values():
        input_line.text.return_value = ""

    # Call save_to_dataset
    panel.save_to_dataset()

    # Verify the CSV file exists but contains only the header
    dataset_file = os.path.join(dataset_dir, 'dataset.csv')
    assert os.path.exists(dataset_file), "Dataset CSV file should exist."

    with open(dataset_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Expect only one line (header row) in the CSV file
    assert len(lines) == 1, "No data should be saved for empty input fields."
