import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)
import os
import pytest
import numpy as np
from IO.saver import ImageSaver

@pytest.fixture
def image_saver(tmp_path):
    """Fixture to initialize ImageSaver with a temporary directory."""
    return ImageSaver(save_directory=str(tmp_path))


def test_save_creates_directory(image_saver, tmp_path):
    """Test if save creates the correct directory."""
    folder_name = "test_folder"
    lot = "test_lot"
    imgs = [(np.zeros((100, 100, 3), dtype=np.uint8), 0)]  # Mock image with top camera port

    image_saver.save(folder_name, lot, imgs)

    save_directory = tmp_path / folder_name
    assert save_directory.exists(), "The save directory should be created."


def test_save_saves_images(image_saver, tmp_path):
    """Test if save writes images to disk."""
    folder_name = "test_folder"
    lot = "test_lot"
    img = np.zeros((100, 100, 3), dtype=np.uint8)  # Mock image
    imgs = [(img, 0)]  # Mock image with top camera port

    image_saver.save(folder_name, lot, imgs)

    file_path = tmp_path / folder_name / f"{lot}_top.jpg"
    assert file_path.exists(), f"The image file {file_path} should be saved."


def test_save_raw_imgs_creates_directory(image_saver, tmp_path):
    """Test if save_raw_imgs creates the correct directory."""
    folder_name = "raw_imgs"
    imgs = [(np.zeros((100, 100, 3), dtype=np.uint8), 1)]  # Mock image with bottom camera port

    image_saver.save_raw_imgs(folder_name, imgs)

    # The directory name includes the timestamp, so check for prefix
    save_directory = [p for p in tmp_path.iterdir() if p.is_dir() and folder_name in str(p)]
    assert save_directory, "The save_raw_imgs directory should be created."


def test_save_raw_imgs_saves_images(image_saver, tmp_path):
    """Test if save_raw_imgs writes images to disk."""
    folder_name = "raw_imgs"
    img = np.zeros((100, 100, 3), dtype=np.uint8)  # Mock image
    imgs = [(img, 1)]  # Mock image with bottom camera port

    image_saver.save_raw_imgs(folder_name, imgs)

    # Check if an image file is saved with the correct prefix
    save_directory = [p for p in tmp_path.iterdir() if p.is_dir() and folder_name in str(p)][0]
    saved_images = list(save_directory.glob("*.jpg"))
    assert len(saved_images) > 0, "At least one image file should be saved."


def test_save_handles_empty_images(image_saver):
    """Test if save gracefully handles empty images."""
    folder_name = "empty_folder"
    lot = "test_lot"
    imgs = [(None, 0)]  # Empty image

    image_saver.save(folder_name, lot, imgs)

    # Check that no files are created
    save_directory = os.path.join(image_saver.save_directory, folder_name)
    assert os.path.exists(save_directory), "The save directory should be created."
    assert not os.listdir(save_directory), "No files should be saved for empty images."


def test_save_raw_imgs_ensures_numpy_array(image_saver):
    """Test if save_raw_imgs asserts that images are numpy arrays."""
    folder_name = "raw_imgs"
    imgs = [("invalid_image", 0)]  # Invalid image

    with pytest.raises(AssertionError, match="Image is not a numpy array"):
        image_saver.save_raw_imgs(folder_name, imgs)
