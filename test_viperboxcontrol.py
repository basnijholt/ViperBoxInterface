import pytest
from unittest.mock import patch
from viperboxcontrol import ViperBoxControl


def test_recording_path():
    controller = ViperBoxControl()
    controller._recording_file_name = "test_file.bin"
    controller._recording_file_location = "./data/"
    assert controller._recording_path == "./data/test_file.bin"


def test_control_rec_setup_valid_input():
    controller = ViperBoxControl()
    result = controller.control_rec_setup(
        file_name="test.bin",
        file_location="./",
        probe=0,
        reference_electrode=2,
        emulated=True,
    )
    assert result is True


def test_control_rec_setup_invalid_probe():
    controller = ViperBoxControl()
    with pytest.raises(ValueError):
        controller.control_rec_setup(
            file_name="test.bin", file_location="./", probe=4, reference_electrode=2
        )


def test_control_rec_setup_invalid_ref_electrode():
    controller = ViperBoxControl()
    with pytest.raises(ValueError):
        controller.control_rec_setup(
            file_name="test.bin", file_location="./", probe=0, reference_electrode=9
        )


def test_control_rec_start_already_recording():
    controller = ViperBoxControl()
    controller._recording = True
    controller._recording_file_name = "already_recording.bin"
    with patch("viperboxcontrol.logging.info") as mock_log:
        controller.control_rec_start()
    mock_log.assert_called_with(
        "Already recording under the name: already_recording.bin"
    )


def test_control_rec_stop_not_recording():
    controller = ViperBoxControl()
    with patch("viperboxcontrol.logging.info") as mock_log:
        controller.control_rec_stop()
    mock_log.assert_called_with("No recording in progress.")


def test_control_rec_status_recording():
    controller = ViperBoxControl()
    controller._recording = True
    assert controller.control_rec_status() is True


def test_control_rec_status_not_recording():
    controller = ViperBoxControl()
    controller._recording = False
    assert controller.control_rec_status() is False


def test_str_recording():
    controller = ViperBoxControl()
    controller._recording = True
    controller._recording_file_name = "recording.bin"
    assert str(controller) == "Status: Recording, Recording Name: recording.bin"


def test_str_not_recording():
    controller = ViperBoxControl()
    controller._recording = False
    assert str(controller) == "Status: Not Recording, Recording Name: None"
