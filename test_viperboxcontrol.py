from viperboxcontrol import ViperBoxControl
import time
from parameters import (
    ConfigurationParameters,
    PulseShapeParameters,
    PulseTrainParameters,
    ViperBoxConfiguration,
)

# write test to check if pulse_duration = sum of parts


# Test workflow
def test_pure_recording():
    controller = ViperBoxControl("test", probe=0)
    controller.control_rec_setup(emulated=True)
    controller.control_rec_start(recording_time=1)
    print(controller)


def test_infinite_recording():
    controller = ViperBoxControl("test", probe=0)
    controller.control_rec_setup(emulated=True)
    controller.control_rec_start()
    controller.control_rec_stop()
    print(controller)


def test_stim_record_defined_session():
    pulse_shape = PulseShapeParameters()
    pulse_train = PulseTrainParameters()
    electrodes = [1, 2, 3]
    viperbox = ViperBoxConfiguration(0)
    config = ConfigurationParameters(pulse_shape, pulse_train, electrodes, viperbox)

    controller = ViperBoxControl("test", 0)
    controller.control_rec_setup(emulated=True)
    controller.control_send_parameters(config_params=config)
    controller.stimulation_trigger(1)


def test_record_stim_train():
    # start recording
    controller = ViperBoxControl("test", probe=0)
    controller.control_rec_setup(emulated=True)
    controller.control_rec_start()
    time.sleep(1)
    # set up
    pulse_shape = PulseShapeParameters()
    pulse_train = PulseTrainParameters()
    electrodes = [1, 2, 3]
    viperbox = ViperBoxConfiguration(0)
    config = ConfigurationParameters(pulse_shape, pulse_train, electrodes, viperbox)
    # stimulate
    controller.control_send_parameters(config_params=config)
    controller.stimulation_trigger()
    # stop recording
    time.sleep(10)
    controller.control_rec_stop()


def test_recording_path():
    controller = ViperBoxControl()
    controller._recording_file_name = "test_file"
    controller._recording_file_location = "./data/"
    assert controller._recording_path == "./data/"
    +f"test_file{time.strftime('_%Y-%m-%d_%H-%M-%S') + '.bin'}"


# def test_control_rec_setup_valid_input():
#     controller = ViperBoxControl()
#     result = controller.control_rec_setup(
#         file_name="test",
#         file_location="./",
#         probe=0,
#         reference_electrode=2,
#         emulated=True,
#     )
#     assert result is True


# def test_control_rec_setup_invalid_probe():
#     controller = ViperBoxControl()
#     with pytest.raises(ValueError):
#         controller.control_rec_setup(
#             file_name="test", file_location="./", probe=4, reference_electrode=2
#         )


# def test_control_rec_setup_invalid_ref_electrode():
#     controller = ViperBoxControl()
#     with pytest.raises(ValueError):
#         controller.control_rec_setup(
#             file_name="test.bin", file_location="./", probe=0, reference_electrode=9
#         )


# def test_control_rec_start_already_recording():
#     controller = ViperBoxControl()
#     controller._recording = True
#     controller._recording_file_name = "already_recording.bin"
#     with patch("viperboxcontrol.logging.info") as mock_log:
#         controller.control_rec_start()
#     mock_log.assert_called_with(
#         "Already recording under the name: already_recording.bin"
#     )


# def test_control_rec_stop_not_recording():
#     controller = ViperBoxControl()
#     with patch("viperboxcontrol.logging.info") as mock_log:
#         controller.control_rec_stop()
#     mock_log.assert_called_with("No recording in progress.")


# def test_control_rec_status_recording():
#     controller = ViperBoxControl()
#     controller._recording = True
#     assert controller.control_rec_status() is True


# def test_control_rec_status_not_recording():
#     controller = ViperBoxControl()
#     controller._recording = False
#     assert controller.control_rec_status() is False


# def test_str_recording():
#     controller = ViperBoxControl()
#     controller._recording = True
#     controller._recording_file_name = "recording.bin"
#     assert str(controller) == "Status: Recording, Recording Name: recording.bin"


# def test_str_not_recording():
#     controller = ViperBoxControl()
#     controller._recording = False
#     assert str(controller) == "Status: Not Recording, Recording Name: None"
