import copy
import logging
import logging.handlers
import os
import socket
import threading
import time
import traceback
from pathlib import Path
from typing import Any, List, Tuple

import numpy as np
import requests
import urllib3
from lxml import etree

import NeuraviperPy as NVP
from defaults.defaults import OS2chip
from VB_classes import (
    BoxSettings,
    ConnectedBoxes,
    ConnectedProbes,
    GeneralSettings,
    ProbeSettings,
    StatusTracking,
    parse_numbers,
)
from XML_handler import (
    add_to_stimrec,
    check_xml_boxprobes_exist_and_verify_data_with_settings,
    create_empty_xml,
    update_settings_with_XML,
    verify_params,
    verify_step_min_max,
)

# TODO: implement rotation of logs to not hog up memory


class ViperBox:
    """Class for interacting with the IMEC Neuraviper API."""

    BUFFER_SIZE = 500
    SKIP_SIZE = 20
    FREQ = 20000
    OS_WRITE_TIME = 1

    def __init__(self, _session_datetime: str, start_oe=True) -> None:
        """Initialize the ViperBox class."""
        self._working_directory = os.getcwd()

        self.local_settings = GeneralSettings()
        self.connected = ConnectedBoxes()
        self.uploaded_settings = GeneralSettings()
        self.tracking = StatusTracking()
        self._box_ptrs: Any = {}

        self._session_datetime = _session_datetime
        self._rec_start_time: float | None = None

        log_folder = Path.cwd() / "logs"
        log_file = f"log_{self._session_datetime}.log"
        log_folder.mkdir(parents=True, exist_ok=True)
        self._log = log_folder.joinpath(log_file)
        self.stim_file_path: Path | None = None

        self._rec_path: Path | None = None

        self.start_oe = start_oe
        self.boxless = False
        self.emulation = False

        # for handler in logging.root.handlers[:]:
        #     logging.root.removeHandler(handler)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        socketHandler = logging.handlers.SocketHandler(
            "localhost", logging.handlers.DEFAULT_TCP_LOGGING_PORT
        )
        self.logger.addHandler(socketHandler)

        # self.logger = logging.getLogger(__name__)
        # # handler = logging.StreamHandler(sys.stdout)
        # # self.logger.addHandler(handler)

        # TODO take out this
        # self.connect("1", True, True)

        # self.logger.info("ViperBox initialized")

        return None

    def empty_socket(self, lifetime=5) -> None:
        serverAddressPort = ("127.0.0.1", 9001)
        MULTICAST_TTL = 2
        UDPClientSocket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )

        UDPClientSocket.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL
        )
        databuffer = np.ones((60, 500), dtype="uint16")
        i = 0
        while i < 10 * lifetime:
            # global stop_threads
            UDPClientSocket.sendto(databuffer, serverAddressPort)
            time.sleep(0.1)
            i += 1
            # if stop_threads:
            #     break

    def connect(
        self,
        probe_list: str = "1",
        emulation: bool = False,
        boxless: bool = False,
    ) -> Tuple[bool, str]:
        """Initiates ViperBox and connects to probes. Box is created and emulation\
        type is set.

        TODO: !!!!! all existing data is removed because the local settings are reset.
        The solution is to mention this in the docs and GUI.
        """
        self._time()
        self.boxless = boxless
        self.emulation = emulation
        self.logger.info(
            f"ViperBox connect: probe list: {probe_list}, emulation: {emulation}, \
boxless: {boxless}."
        )

        # Checks if the ViperBox is connected and connects if not.
        if self.tracking.box_connected is True:
            self.logger.info("Already connected to ViperBox, disconnecting first.")
            self.disconnect()

        if self.boxless is False:
            self.logger.info("Connecting to ViperBox...")

        # check if boxless mode is enabled
        if self.boxless is True:
            # Boxless mode connects 1 box and 1 probe
            self.connected.boxes[0] = ConnectedProbes()
            self.connected.boxes[0].probes[0] = True
            self.recording_settings(default_values=True)
            self.stimulation_settings(default_values=True)
            self.logger.info(f"local settings: {self.local_settings}")
            self.logger.info(f"connected probes: {self.local_settings.connected}")
            return True, "Boxless mode, no connection to ViperBox"

        # check if probes is a list of 4 elements and only containing ints 1 or 0
        try:
            probe_list_int = parse_numbers(probe_list, [0, 1, 2, 3])
        except ValueError as e:
            return (
                False,
                f"Invalid probe list: {self._er(e)}",
            )

        threading.Thread(target=self.empty_socket, daemon=True).start()

        if self.start_oe:
            threading.Thread(
                target=self._start_eo_acquire, args=(True,), daemon=True
            ).start()

        # Scan for devices
        NVP.scanBS()
        devices = NVP.getDeviceList(16)
        number_of_devices = len(devices)
        if number_of_devices == 0:
            err_msg = "No device found, please check if the ViperBox is connected"
            self.logger.error(err_msg)
            return False, err_msg
        elif number_of_devices > 1:
            err_msg = """More than one device found, currently this software can only \
                box one device"""
            self.logger.error(err_msg)
            return False, err_msg
        elif number_of_devices == 1:
            self.logger.info(f"Device found: {devices[0]}")
            # TODO add box settings and info and stuffff
            self.local_settings.boxes[0] = BoxSettings()
            self.connected.boxes[0] = ConnectedProbes()
            pass
        else:
            self.logger.info(
                "Unknown error, please restart the ViperBox or check the \
                logs for more information"
            )
            return False, "Unknown error, please check the logs for more information"
        self.tracking.box_connected = True

        # Connect and set up viperbox
        # TODO boxfix: also loop over boxes
        box = 0
        tmp_handel = NVP.createHandle(devices[0].ID)
        self._box_ptrs[box] = tmp_handel
        # self._box_ptrs[box] = NVP.createHandle(devices[0].ID)
        self.logger.info(f"Box handle created: {self._box_ptrs[box]}")
        NVP.openBS(self._box_ptrs[box])
        self.logger.info(f"BS opened: {self._box_ptrs[box]}")
        if (
            emulation is True
        ):  # Choose linear ramp emulation (1 sample shift between channels)
            NVP.setDeviceEmulatorMode(
                self._box_ptrs[box], NVP.DeviceEmulatorMode.LINEAR
            )
            NVP.setDeviceEmulatorType(
                self._box_ptrs[box], NVP.DeviceEmulatorType.EMULATED_PROBE
            )
            self.logger.info("Emulation mode: linear ramp")
        else:
            NVP.setDeviceEmulatorMode(self._box_ptrs[box], NVP.DeviceEmulatorMode.OFF)
            NVP.setDeviceEmulatorType(self._box_ptrs[box], NVP.DeviceEmulatorType.OFF)
            self.logger.info("Emulation mode: off")
        # print(
        #     f"""{self._time()-start_time} finished setting emulation, starting \
        #     opening probes"""
        # )
        try:
            NVP.openProbes(self._box_ptrs[box])
        except Exception as e:
            self.logger.warning(f"!! openProbes() exception error: {self._er(e)}")
            self.disconnect()
            return False, "Please connect asic to ViperBox and try again."
        self.logger.info(f"Probes opened: {self._box_ptrs[box]}")

        # print(f"{self._time()-start_time} opened probes, starting initialization")
        # Connect and set up probes
        # TODO boxfix: also loop over boxes
        for probe in probe_list_int:
            try:
                NVP.init(self._box_ptrs[box], int(probe))  # Initialize all probes
                self.logger.info(f"Probe {probe} initialized: {self._box_ptrs[box]}")
                self.local_settings.boxes[0].probes[probe] = ProbeSettings()
                self.connected.boxes[0].probes[probe] = True
            except Exception as error:
                self.logger.warning(
                    f"!! Init() exception error, probe {probe}: {self._er(error)}"
                )
        self.logger.info(f"API channel opened: {devices[0]}")
        self._deviceId = devices[0].ID
        # print(self.local_settings)

        self.uploaded_settings = copy.deepcopy(self.local_settings)

        # TODO boxfix: also loop over boxes
        return (
            True,
            f"""ViperBox initialized successfully with probes \
{self.local_settings.connected}""",
        )

    def disconnect(self) -> Tuple[bool, str]:
        """Disconnects from the ViperBox and closes the API channel."""

        if self.boxless is True:
            return True, "Boxless mode, no connection to ViperBox"
        elif self.tracking.box_connected is False:
            return True, "Not connected to ViperBox"

        # TODO boxfix: also loop over boxes
        try:
            box = 0
            NVP.closeProbes(self._box_ptrs[box])
            NVP.closeBS(self._box_ptrs[box])
            NVP.destroyHandle(self._box_ptrs[box])
            self._deviceId = 0
            self.tracking.box_connected = False
            self.uploaded_settings = GeneralSettings()
        except KeyError as e:
            self.logger.debug(
                f"Can't disconnect from ViperBox, no ViperBox connection. \
Error: {self._er(e)}"
            )
            return (
                False,
                "Can't disconnect from ViperBox, no ViperBox connection. \
Please restart the ViperBox and the software and try again.",
            )

        return True, "ViperBox disconnected"

    def shutdown(self) -> Tuple[bool, str]:
        self.disconnect()
        # if not self.headless:
        # try:
        #     _ = requests.put(
        #         "http://localhost:37497/api/status",
        #         json={"mode": "ACQUIRE"},
        #         timeout=2,
        #     )
        # except Exception as e:
        #     pass
        # try:
        #     _ = requests.put(
        #         "http://localhost:37497/api/window",
        #         json={"command": "quit"},
        #         timeout=5,
        #     )
        # except Exception as e:
        #     pass
        return True, "ViperBox shutdown"

    def _upload_recording_settings(self, updated_tmp_settings):
        if self.boxless is True:
            self.logger.info(
                "No box connected, skipping uploading recording settings \
to ViperBox"
            )
            return
        for box in updated_tmp_settings.boxes.keys():
            for probe in updated_tmp_settings.boxes[box].probes.keys():
                for channel in (
                    updated_tmp_settings.boxes[box].probes[probe].channel.keys()
                ):
                    NVP.selectElectrode(self._box_ptrs[box], probe, channel, 0)
                    NVP.setReference(
                        self._box_ptrs[box],
                        probe,
                        channel,
                        updated_tmp_settings.boxes[box]
                        .probes[probe]
                        .channel[channel]
                        .get_refs,
                    )
                    NVP.setGain(
                        self._box_ptrs[box],
                        probe,
                        channel,
                        updated_tmp_settings.boxes[box]
                        .probes[probe]
                        .channel[channel]
                        .gain,
                    )
                    NVP.setAZ(
                        self._box_ptrs[box], probe, channel, False
                    )  # see email Patrick 08/01/2024

                self.logger.debug(
                    f"Writing Channel config: \
{updated_tmp_settings.boxes[box].probes[probe]}"
                )
                NVP.writeChannelConfiguration(self._box_ptrs[box], probe, False)

    def _upload_stimulation_settings(self, updated_tmp_settings: GeneralSettings):
        self.logger.info(
            f"Writing stimulation settings to ViperBox: {updated_tmp_settings}"
        )
        if self.boxless is True:
            self.logger.info(
                "No box connected, skipping uploading stimulation \
settings to ViperBox"
            )
            return
        for box in updated_tmp_settings.boxes.keys():
            for probe in updated_tmp_settings.boxes[box].probes.keys():
                # Always set settings for entire probe at once.
                NVP.setOSimage(
                    self._box_ptrs[box],
                    probe,
                    updated_tmp_settings.boxes[box].probes[probe].os_data,
                )
                for OS in range(128):
                    NVP.setOSDischargeperm(self._box_ptrs[box], probe, OS, False)
                    NVP.setOSStimblank(self._box_ptrs[box], probe, OS, True)

            for SU in range(8):
                NVP.writeSUConfiguration(
                    self._box_ptrs[box],
                    probe,
                    SU,
                    *updated_tmp_settings.boxes[box]
                    .probes[probe]
                    .stim_unit_sett[SU]
                    .SUConfig(),
                )

    def recording_settings(
        self,
        xml_string: str | None = None,
        reset: bool = False,
        default_values: bool = False,
    ) -> Tuple[bool, str]:
        """Loads the recording settings from an XML string or default file."""

        if self.boxless is True:
            pass
        elif self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return (
                False,
                "Recording in progress, cannot change settings. To verify \
custom XML settings, use the verify_xml API call.",
            )

        if default_values is True:
            XML_data = etree.parse("defaults/default_recording_settings.xml")
        else:
            try:
                XML_data = etree.fromstring(xml_string)
            except TypeError as e:
                return (
                    False,
                    f"Invalid xml string. Error: {self._er(e)}",
                )

        # make temporary copy of settings
        tmp_local_settings = copy.deepcopy(self.local_settings)

        self.logger.debug(f"Checking XML with settings: {tmp_local_settings}")
        result, feedback = check_xml_boxprobes_exist_and_verify_data_with_settings(
            XML_data, tmp_local_settings, self.connected, "recording"
        )
        # result, feedback = check_xml_with_settings(
        #     XML_data, tmp_local_settings, "recording"
        # )
        if result is False:
            return result, feedback

        if reset:
            self.logger.info("Resetting recording settings")
            tmp_local_settings.reset_recording_settings()
        self.logger.info("Updating supplied settings to local settings")
        # add connected boxes and probes to tmp_local_settings

        updated_tmp_settings = update_settings_with_XML(
            XML_data, tmp_local_settings, "recording"
        )

        try:
            # Always set settings for entire probe at once.
            # TODO boxfix: also loop over boxes
            self._upload_recording_settings(updated_tmp_settings)
        except Exception as e:
            return (
                False,
                f"Error in uploading recording settings, settings not applied and \
reverted to previous settings. Error: {self._er(e)}",
            )

        self.local_settings = updated_tmp_settings  # Why not deepcopy??
        self.logger.info("uploaded_settings = local_settings")
        self.uploaded_settings = copy.deepcopy(self.local_settings)
        return True, "Recording settings loaded"

    def _stimrec_write_recording_settings(self, settings_to_write, start_time, dt_time):
        self.logger.info(
            f"Writing recording settings to stimrec file: {settings_to_write}"
        )

        # for box in updated_tmp_settings.boxes.keys():
        #     for probe in updated_tmp_settings.boxes[box].probes.keys():
        #         if self.stim_file_path is not None:
        #             for channel in (
        #                 self.uploaded_settings.boxes[box].probes[probe].channel.keys()
        #             ):
        #                 add_to_stimrec(
        #                     self.stim_file_path,
        #                     "Settings",
        #                     "Channel",
        #                     {
        #                         "box": box,
        #                         "probe": probe,
        #                         "channel": channel,
        #                         **self.uploaded_settings.boxes[box]
        #                         .probes[probe]
        #                         .channel[channel]
        #                         .__dict__,
        #                     },
        #                     start_time,
        #                     dt_time,
        #                 )

    def _stimrec_write_stimulation_settings(
        self, updated_tmp_settings, start_time, dt_time
    ):
        self.logger.info(
            f"Writing stimulation settings to stimrec file: {updated_tmp_settings}"
        )
        if self.stim_file_path:
            for box in updated_tmp_settings.boxes.keys():
                for probe in updated_tmp_settings.boxes[box].probes.keys():
                    for configuration in (
                        updated_tmp_settings.boxes[box]
                        .probes[probe]
                        .stim_unit_sett.keys()
                    ):
                        add_to_stimrec(
                            self.stim_file_path,
                            "Settings",
                            "Configuration",
                            {
                                "box": box,
                                "probe": probe,
                                "stimunit": configuration,
                                **updated_tmp_settings.boxes[box]
                                .probes[probe]
                                .stim_unit_sett[configuration]
                                .__dict__,
                            },
                            start_time,
                            dt_time,
                        )
                    for mapping in (
                        updated_tmp_settings.boxes[box]
                        .probes[probe]
                        .stim_unit_elec.keys()
                    ):
                        add_to_stimrec(
                            self.stim_file_path,
                            "Settings",
                            "Mapping",
                            {
                                "box": box,
                                "probe": probe,
                                "stimunit": mapping,
                                "electrodes": updated_tmp_settings.boxes[box]
                                .probes[probe]
                                .stim_unit_elec[mapping],
                            },
                            start_time,
                            dt_time,
                        )
        return True, "Stimulation settings wrote to stimrec file"

    def stimulation_settings(
        self,
        xml_string: str | None = None,
        reset: bool = False,
        default_values: bool = True,
    ) -> Tuple[bool, str]:
        """Loads the stimulation settings from an XML file."""

        if self.boxless is True:
            pass
        elif self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if default_values is True:
            XML_data = etree.parse("defaults/default_stimulation_settings.xml")
        else:
            try:
                XML_data = etree.fromstring(xml_string)
            except TypeError as e:
                return (
                    False,
                    f"Invalid xml string. Error: {self._er(e)}",
                )

        tmp_local_settings = copy.deepcopy(self.local_settings)

        result, feedback = check_xml_boxprobes_exist_and_verify_data_with_settings(
            XML_data, tmp_local_settings, self.connected, "stimulation"
        )
        # result, feedback = check_xml_with_settings(
        #     XML_data, tmp_local_settings, "stimulation"
        # )

        if result is False:
            return result, feedback

        if reset:
            tmp_local_settings.reset_stimulation_settings()

        updated_tmp_settings = update_settings_with_XML(
            XML_data, tmp_local_settings, "stimulation"
        )

        # TODO boxfix: also loop over boxes
        start_time = self._time()
        try:
            self._upload_stimulation_settings(updated_tmp_settings)
            self.uploaded_settings = copy.deepcopy(updated_tmp_settings)
            self.tracking.stimulation_settings_uploaded = True
            self.tracking.stimulation_settings_written_to_stimrec = False
        except Exception as e:
            return (
                False,
                f"Error in uploading stimulation settings, settings not applied and \
reverted to previous settings. Error: {self._er(e)}",
            )
        dt_time = self._time() - start_time

        self.tracking.stimset_upload_times = (start_time, dt_time)
        self.local_settings = copy.deepcopy(updated_tmp_settings)

        # # if stim_file_path doesn't exist, the recording hasn't started yet
        # # settings will be written to stimrec at recording start
        # if self.stim_file_path:
        #     result, feedback = self._stimrec_write_stimulation_settings(
        #         updated_tmp_settings, start_time, dt_time
        #     )
        #     if result is False:
        #         return result, feedback

        return True, "Stimulation settings loaded"

    def verify_xml_with_local_settings(
        self, XML_dictionary: dict, XML_data: Any, check_topic: str = "all"
    ) -> Tuple[bool, str]:
        """API Verifies the XML string."""

        tmp_data = copy.deepcopy(self.local_settings)

        if XML_dictionary != {}:
            params = [
                tuple
                for tuple in verify_params
                if list(XML_dictionary.keys())[0] in tuple
            ]
            try:
                int(list(XML_dictionary.values())[0])
            except ValueError:
                return (
                    False,
                    "Input value should be an integer",
                )
            verify_step_min_max(*params[0], int(list(XML_dictionary.values())[0]))
            return True, f"Verify xml call with dictionary: {XML_dictionary}"
        elif XML_data != "":
            result, feedback = check_xml_boxprobes_exist_and_verify_data_with_settings(
                XML_data, tmp_data, self.connected, "all"
            )
            # result, feedback = check_xml_with_settings(
            #     XML_data, tmp_data, check_topic, self.boxless
            # )
        else:
            return False, "No XML data found"

        # TODO:
        return result, feedback

    def default_settings(self) -> Tuple[bool, str]:
        """Loads the default settings from an XML file."""

        if self.boxless is True:
            pass
        elif self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return (
                False,
                """Recording in progress, cannot change settings. First stop recording \
to load default settings""",
            )

        XML_data = etree.parse("defaults/default_settings.xml")

        tmp_local_settings = copy.deepcopy(self.local_settings)

        result, feedback = check_xml_boxprobes_exist_and_verify_data_with_settings(
            XML_data, tmp_local_settings, self.connected, "all"
        )
        # result, feedback =
        # check_xml_with_settings(XML_data, tmp_local_settings, "all")

        if result is False:
            return result, feedback

        tmp_local_settings.reset_probe_settings()

        updated_tmp_settings = update_settings_with_XML(
            XML_data, tmp_local_settings, "recording"
        )
        updated_tmp_settings = update_settings_with_XML(
            XML_data, updated_tmp_settings, "stimulation"
        )

        # TODO boxfix: also loop over boxes
        try:
            self._upload_recording_settings(updated_tmp_settings)
        except Exception as e:
            if e == KeyError and self.boxless is True:
                self.logger.info("No box connected, skipping recording settings")
            else:
                return (
                    False,
                    f"Error in uploading recording settings, settings not applied and \
    reverted to previous settings. Error: {self._er(e)}",
                )

        start_time = self._time()
        try:
            self._upload_stimulation_settings(updated_tmp_settings)
            self.tracking.stimulation_settings_uploaded = True
            self.tracking.stimulation_settings_written_to_stimrec = False
        except Exception as e:
            return (
                False,
                f"Error in uploading stimulation settings, settings not applied and \
reverted to previous settings. Error: {self._er(e)}",
            )

        dt_time = self._time() - start_time
        self.tracking.stimset_upload_times = (start_time, dt_time)

        self.local_settings = updated_tmp_settings
        self.uploaded_settings = copy.deepcopy(self.local_settings)

        return True, "Default recording and stimulation settings loaded"

    def start_recording(self, recording_name: str = "") -> Tuple[bool, str]:
        """Start recording.

        Arguments:
        - recording_name: str | None - the name of the recording, it will be
        saved in the Recordings folder. This can also be a folder path or a
        file path. If it is a folder path, the recording will be saved as
        unnamed_recording in that folder. In case of a file path, the recording will be
        named as the filepath. If no name is given, the recording will be saved as
        unnamed_recording in the Recordings folder.

        Tests:
        - start recording with incomplete settings uploaded
        """
        if self.boxless is True or self.emulation is True:
            pass
        elif self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return (
                False,
                """Already recording, first stop recording to start a new \
                    recording""",
            )

        # TODO this should check if recording settings are available for all
        # connected boxes
        if not self.emulation:
            self.logger.debug("Check if uploaded settings has all recording settings")
            for box in self.uploaded_settings.boxes.keys():
                for probe in self.uploaded_settings.boxes[box].probes.keys():
                    if (
                        len(self.uploaded_settings.boxes[box].probes[probe].channel)
                        != 64
                    ):
                        return (
                            False,
                            f"""No recording settings available for all channels on box\
 {box}, probe {probe}. First upload default settings for all channels, then \
upload your custom settings and then try again.""",
                        )

        self._recording_datetime = time.strftime("%Y%m%d_%H%M%S")

        rec_folder = Path.cwd() / "Recordings"
        rec_folder.mkdir(parents=True, exist_ok=True)
        self.recording_name = recording_name

        # The options are: no input, input fname, input bs, input full path
        if not ("\\" in self.recording_name or "/" in self.recording_name):
            # this is a filename
            self._rec_path = rec_folder.joinpath(
                f"{self.recording_name}_{self._recording_datetime}.bin"
            )
        elif "\\" in self.recording_name or "/" in self.recording_name:
            tmp_rec_path = Path(self.recording_name)
            # this is a path
            # the last folder is used with unnamed recording
            # the file is used as is
            if tmp_rec_path.exists():
                if tmp_rec_path.is_dir():
                    self._rec_path = tmp_rec_path.joinpath(
                        f"unnamed_recording_{self._recording_datetime}.bin"
                    )
                elif tmp_rec_path.is_file():
                    self._rec_path = tmp_rec_path.with_suffix(".bin")
        else:
            self._rec_path = rec_folder.joinpath(
                f"unnamed_recording_{self._recording_datetime}.bin"
            )

        self.logger.debug(self._box_ptrs)
        self.logger.debug("NVP.setFileStream")
        box = 0
        NVP.setFileStream(self._box_ptrs[box], str(self._rec_path))
        self.logger.debug("NVP.enableFileStream")
        NVP.enableFileStream(self._box_ptrs[box], str(self._rec_path))
        self.logger.debug("NVP.arm")
        NVP.arm(self._box_ptrs[box])

        self.logger.debug("NVP.setSWTrigger")
        self._rec_start_time = self._time()
        NVP.setSWTrigger(self._box_ptrs[box])
        dt_rec_start = self._time()

        if self.recording_name:
            stimrec_name = self.recording_name
        else:
            stimrec_name = "unnamed_stimulation_record"
        self.stim_file_path = self._create_file_folder(
            "Stimulations",
            stimrec_name,
            "xml",
            f"{time.strftime('%Y%m%d_%H%M%S')}",
        )

        # Create stimulation record
        create_empty_xml(self.stim_file_path)

        self.logger.info(
            f"Writing recording settings to stimrec file: {self.uploaded_settings}"
        )

        self.logger.debug("Write recording settings to stimrec")
        # Write recording settings to stimrec
        for box in self.uploaded_settings.boxes.keys():
            for probe in self.uploaded_settings.boxes[box].probes.keys():
                for channel in (
                    self.uploaded_settings.boxes[box].probes[probe].channel.keys()
                ):
                    add_to_stimrec(
                        self.stim_file_path,
                        "Settings",
                        "Channel",
                        {
                            "box": box,
                            "probe": probe,
                            "channel": channel,
                            **self.uploaded_settings.boxes[box]
                            .probes[probe]
                            .channel[channel]
                            .__dict__,
                        },
                        -1.0,
                        -1.0,
                    )

        # Not necessary because will be written at stimulation start
        # # Try to write stimulation settings to stimrec if they are available.
        # self._stimrec_write_stimulation_settings(self.local_settings, -1.0, -1.0)
        self.logger.debug("Write recording start to stimrec")
        add_to_stimrec(
            self.stim_file_path,
            "Instructions",
            "Instruction",
            {"filename": self.recording_name, "instruction_type": "recording_start"},
            0.0,
            dt_rec_start,
        )

        self.tracking.recording = True

        # TODO fix probe number
        # probably add a que for all data streams and be able to let open ephys
        # switch between them
        self.oe_socket = True
        probe = 0
        self.logger.debug("Start sending data")
        threading.Thread(
            target=self._send_data_to_socket, args=(probe,), daemon=True
        ).start()

        if self.start_oe:
            threading.Thread(
                target=self._start_eo_acquire, args=(True,), daemon=True
            ).start()

        self.logger.info(f"Recording started: {recording_name}")
        return True, f"Recording started: {recording_name}"

    def _time(self) -> float:
        """Returns the current time in seconds.
        If start_time_program is given, it will be subtracted from the current time.

        TODO: year 2262 this will wrap.
        """
        if self._rec_start_time:
            return time.time_ns() / 1e9 - self._rec_start_time
        else:
            return time.time_ns() / 1e9

    def _create_file_folder(
        self,
        folder_name: str,
        file_name: str,
        extension: str,
        custom_datetime: None | str = None,
        create_empty_file: bool = False,
    ) -> Path:
        folder = Path.cwd() / folder_name
        if custom_datetime:
            file = f"{file_name}_{custom_datetime}.{extension}"
        else:
            file = f"{file_name}_{time.strftime('%Y%m%d_%H%M%S')}.{extension}"
        folder.mkdir(parents=True, exist_ok=True)
        if create_empty_file:
            open(folder.joinpath(file), "w").close()
        self.logger.info(f"Created file: {folder.joinpath(file)}")
        return folder.joinpath(file)

    def _start_eo_acquire(self, startup_oe=False):
        # time.sleep(0.5)
        self.logger.info(
            "Try to switch open ephys to acquire mode, otherwise start it."
        )
        acquiring = False
        # check if open ephys is running
        try:
            r = requests.get("http://localhost:37497/api/status", timeout=0.1)
            if r.json()["mode"] != "ACQUIRE":
                r = requests.put(
                    "http://localhost:37497/api/status",
                    json={"mode": "ACQUIRE"},
                    timeout=1,
                )
        except (
            TimeoutError,
            requests.exceptions.Timeout,
            urllib3.exceptions.ConnectTimeoutError,
            urllib3.exceptions.MaxRetryError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.RequestException,
        ):
            self.logger.info("Couldn't get OE status")
            if startup_oe:
                try:
                    print("Starting Open Ephys")
                    os.startfile("C:\Program Files\Open Ephys\open-ephys.exe")
                    r = requests.get("http://localhost:37497/api/status", timeout=1)
                    _ = requests.put(
                        "http://localhost:37497/api/recording",
                        json={
                            "parent_directory": os.path.abspath("setup\\oesettings.xml")
                        },
                        timeout=1,
                    )
                    if r.json()["mode"] != "ACQUIRE":
                        while not acquiring:
                            try:
                                r = requests.put(
                                    "http://localhost:37497/api/status",
                                    json={"mode": "ACQUIRE"},
                                    timeout=1,
                                )
                                acquiring = True
                            except Exception as e:
                                self.logger.warning(
                                    f"Can't start Open Ephys, please start it \
manually. Error: {self._er(e)}"
                                )
                except Exception as e2:
                    self.logger.warning(
                        f"Can't start Open Ephys, please start it manually. \
Error: {e2}"
                    )
            else:
                self.logger.warning(
                    """Open Ephys not detected, please start it manually if it is \
                        not running"""
                )

    def _send_data_to_socket(self, probe: int) -> None:
        """Send data packets to a UDP socket, such that Open Ephys and other systems
        can receive the raw data."""

        bufferInterval: float = self.BUFFER_SIZE / self.FREQ

        serverAddressPort: Tuple[str, int] = ("127.0.0.1", 9001)
        # TODO: update settings of socket
        MULTICAST_TTL = 2
        UDPClientSocket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )

        UDPClientSocket.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL
        )

        # TODO: check if this is necessary
        time.sleep(0.1)

        # TODO: How to handle data streams from multiple probes? align on timestamp?
        send_data_read_handle = NVP.streamOpenFile(str(self._rec_path), probe)

        # TODO: remove packages with wrong session
        # status = NVP.readDiagStats(self._box)
        # skip_packages = status.session_mismatch
        # print('skip_packages: ', skip_packages)
        # dump_count = 0
        # while dump_count < skip_packages:
        #     _ = NVP.streamReadData(self._read_handle, self.SKIP_SIZE)
        #     dump_count += self.SKIP_SIZE
        # print('dump_count: ', dump_count)

        self.logger.info("Started sending data to Open Ephys")
        mtx = self._os2chip_mat()
        counter = 0
        # t0 = time.time_ns() // 1e9
        t0 = self._time()
        while self.oe_socket is True:
            counter += 1

            packets = NVP.streamReadData(send_data_read_handle, self.BUFFER_SIZE)
            count = len(packets)

            if count < self.BUFFER_SIZE:
                self.logger.warning("Out of packets")
                break

            # TODO: Rearrange data depening on selected gain
            databuffer = np.asarray(
                [packets[i].data for i in range(self.BUFFER_SIZE)], dtype="uint16"
            )
            databuffer = (databuffer @ mtx).T
            databuffer = databuffer.copy(order="C")
            UDPClientSocket.sendto(databuffer, serverAddressPort)

            # t2 = time.time_ns() // 1e9
            t2 = self._time()
            while (t2 - t0) < counter * bufferInterval:
                # t2 = time.time_ns() // 1e9
                t2 = self._time()

        NVP.streamClose(send_data_read_handle)

    def _os2chip_mat(self):
        mtx = np.zeros((64, 60), dtype="uint16")
        for k, v in OS2chip.items():
            mtx[k - 1][v - 1] = 1
        return mtx

    def stop_recording(self) -> Tuple[bool, str]:
        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is False:
            return False, "Recording not started"

        self.logger.info("Stopping recording")
        start_time = self._time()
        box = 0
        self.logger.debug("Run NVP.arm")
        NVP.arm(self._box_ptrs[box])
        # Close file
        self.logger.debug("Run NVP.setFileStream to no name")
        NVP.setFileStream(self._box_ptrs[box], "")
        dt_time = self._time() - start_time
        self.oe_socket = False

        self.logger.debug("Write to stimrec")
        add_to_stimrec(
            self.stim_file_path,
            "Instructions",
            "Instruction",
            {"filename": self.recording_name, "instruction_type": "recording_stop"},
            start_time,
            dt_time,
        )

        self.tracking.recording = False
        self._rec_start_time = None

        # TODO: combine stim history and recording into some file format
        # self._convert_recording()

        return True, "Recording stopped"

    def _convert_recording(
        self,
    ) -> None:
        """
        Converts the raw recording into a numpy format.
        """
        # TODO: not implemented

        # convert_recording_read_handle = NVP.streamOpenFile(
        #     str(self._rec_path), self._probe
        # )

        # mtx = self._os2chip_mat()
        # while True:
        #     # TODO: implement skipping of packages by checking:
        #     # time = 0
        #     # NAND
        #     # session id is wrong

        #     packets = NVP.streamReadData(
        #         conver_recording_read_handle,
        #         self.BUFFER_SIZE
        #         )
        #     count = len(packets)

        #     if count < self.BUFFER_SIZE:
        #         self.logger.warning("Out of packets")
        #         break

        #     # TODO: Rearrange data depening on selected gain
        #     databuffer = np.asarray(
        #         [packets[i].data for i in range(self.BUFFER_SIZE)], dtype="uint16"
        #     )
        #     databuffer = (databuffer @ mtx).T
        #     databuffer = np.multiply(databuffer, self._settings.gain_vec[:, None])
        #     self._add_to_zarr(databuffer)
        pass

    def _add_to_zarr(self, databuffer: np.ndarray) -> None:
        """Adds the data to the zarr file."""
        # TODO: not implemented
        pass

    def _SU_list_to_bitmask(self, SU_list: List[int]) -> int:
        # convert SUs to NVP format
        SU_string = "".join(["1" if i in SU_list else "0" for i in range(8)])
        return int(SU_string, 2)

    def start_stimulation(
        self, boxes: str, probes: str, SU_input: str
    ) -> Tuple[bool, str]:
        """Starts stimulation on the specified box(s), probe(s) and SU(s).
        First checks if the SUs are configured for their respective boxes and probes.

        Arguments:
        - boxes: str - all boxes to start stimulation in
        - probes: str - all probes to start stimulation in
        - SU_input: str - the SUs to start stimulation in

        Test:
        - Check if this also works if sus are half configured
        """

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is False:
            return (
                False,
                """No recording in progress, cannot start stimulation, please \
                    start recording first""",
            )

        if self.tracking.stimulation_settings_uploaded is False:
            return (
                False,
                """Stimulation settings not uploaded, please upload stimulation \
settings first""",
            )

        # Create a trigger dict
        # fill the trigger dict with values that are configured
        # trigger SUs and store time and dt
        # write stim settings to stimrec if not changed since last time
        # write triggers to stimrec

        # SU_dict = {0: {0: [0,1,2], 1: [3,4,6]}}
        SU_dict: Any = {}
        # Check if boxes, probes and SUs are in right format and properly configured
        # i.e, have waveform configured
        # Using try/except to catch ValueError from parse_numbers
        self.logger.info("Check if boxes, probes and SUs exist and are configured")
        for box in parse_numbers(boxes, list(self.uploaded_settings.boxes.keys())):
            SU_dict[box] = {}
            for probe in parse_numbers(
                probes,
                list(self.uploaded_settings.boxes[box].probes.keys()),
            ):
                SU_dict[box][probe] = self._SU_list_to_bitmask(
                    parse_numbers(
                        SU_input,
                        list(
                            self.uploaded_settings.boxes[box]
                            .probes[probe]
                            .stim_unit_sett.keys()
                        ),
                    )
                )

        #                 except ValueError as e:
        #                     return_statement = "SU settings not available on probe "
        #                     f"{probe}, on box {box} are not available:
        # {self._er(e)}"
        #                     return False, return_statement
        #         except ValueError as e:
        #             return_statement
        #             return (
        #                 False,
        #                 f"""Probe {probe} on box {box} doesn't seem to be
        #                 connected:
        # {self._er(e)}""",
        #             )
        # except ValueError as e:
        #     return False, f"Box {box} doesn't seem to be connected:
        # {self._er(e)}"

        # # Convert SU list into bitmask
        # SU_dict = {
        #     int(box): {
        #         int(probe): self._SU_list_to_bitmask(sulist)
        #         for probe, sulist in probes.items()
        #     }
        #     for box, probes in SU_dict.items()
        # }

        start_dt_times: Any = {}

        # Trigger SUs
        self.logger.info(f"Triggering SUs: {SU_dict}")
        for box in SU_dict.keys():
            start_dt_times[box] = {}
            for probe in SU_dict[box].keys():
                tmp_counter = self._time()
                # TODO could be faster by not having to do this converstion here
                NVP.SUtrig1(
                    self._box_ptrs[box],
                    probe,
                    SU_dict[box][probe],
                )
                tmp_delta = self._time() - tmp_counter
                start_dt_times[box][probe] = (tmp_counter, tmp_delta)

        # Write stimulation settings to stimrec if not changed since last upload
        if self.tracking.stimulation_settings_written_to_stimrec is False:
            self._stimrec_write_stimulation_settings(
                self.uploaded_settings,
                self.tracking.stimset_upload_times[0],
                self.tracking.stimset_upload_times[1],
            )
            self.tracking.stimulation_settings_written_to_stimrec = True

        for box in start_dt_times.keys():
            for probe in start_dt_times[box].keys():
                add_to_stimrec(
                    self.stim_file_path,
                    "Instructions",
                    "Instruction",
                    {
                        "filename": self.recording_name,
                        "instruction_type": "stimulation_start",
                        "box": box,
                        "probe": probe,
                        "SU_bitmask": SU_dict[box][probe],
                    },
                    start_dt_times[box][probe][0],
                    start_dt_times[box][probe][1],
                )

        return_statement = f"Stimulation started on boxes {boxes} probe {probes} \
            for SU's {SU_dict}"
        return True, return_statement

    def _er(self, error):
        return "".join(traceback.TracebackException.from_exception(error).format())

    # def TTL_start(
    #     self, probe: str, TTL_channel: str, SU_input: str
    # ) -> Tuple[bool, str]:
    #     """Starts TTL on the specified channel."""
    #     if TTL_channel not in [1, 2]:
    #         return False, "TTL channel should be 1 or 2"

    #     # Check SU_input format
    #     SU_list = parse_numbers(SU_input, [1, 2, 3, 4, 5, 6, 7, 8])

    #     # convert SUs to NVP format
    #     SU_string = "".join(["1" if i in SU_list else "0" for i in range(1, 9)])
    #     SU_bit_mask = int(SU_string, 2)

    #     if self.tracking.box_connected is False:
    #         return False, "Not connected to ViperBox"

    #     if self.tracking.recording is True:
    #         return False, "Recording in progress, cannot start stimulation"

    #     all_configured, not_configured = self._check_SUs_configured(SU_bit_mask)
    #     if not all_configured:
    #         return False, f"Can't trigger SUs {not_configured}"

    #     threading.Thread(
    #         target=self._start_TTL_tracker_thread,
    #         args=(probe, TTL_channel, SU_bit_mask),
    #     ).start()
    #     # self._start_TTL_tracker_thread(probe, TTL_channel, SU_bit_mask)

    #     self._add_stimulation_record(
    #         "TTL_start",
    #         self._time() - self._rec_start_time,
    #         0,
    #         f"TTL channel: {TTL_channel}",
    #     )

    #     return (
    #         True,
    #         f"""TTL tracking started on channel {TTL_channel} with SU's
    #         {SU_bit_mask} on probe {probe}""",
    #     )

    # def _start_TTL_tracker_thread(
    #     self, probe: int, TTL_channel: int, SU_bit_mask: str
    # ) -> None:
    #     """Converts the raw recording into a numpy format."""
    #     # TODO: this can be reduced to one function that listens to both TTL channels

    #     # note this should be probe specific, not self._probe, that needs to
    #     # be checked anyway
    #     TTL_read_handle = NVP.streamOpenFile(self._rec_path, probe)

    #     self._active_TTLs[TTL_channel] = True

    #     # mtx = self._os2chip_mat()
    #     while self._active_TTLs[TTL_channel] is True:
    #         # TODO: implement skipping of packages by checking:
    #         # time = 0
    #         # NAND
    #         # session id is wrong

    #         packets = NVP.streamReadData(TTL_read_handle, self.BUFFER_SIZE)
    #         count = len(packets)

    #         if count < self.BUFFER_SIZE:
    #             self.logger.warning("Out of packets")
    #             break

    #         # TODO: Rearrange data depending on selected gain
    #         databuffer = np.asarray(
    #             [
    #                 [
    #                     int(str(bin(packets[0].status))[3:-1][0]),
    #                     int(str(bin(packets[0].status))[3:-1][1]),
    #                 ]
    #                 for i in range(self.BUFFER_SIZE)
    #             ],
    #             dtype="uint16",
    #         )
    #         if databuffer[:, TTL_channel].any():
    #             ret_val, text = self.start_stimulation(probe, SU_bit_mask)

    #         if ret_val is False:
    #             # tell the user that the stimulation was not started
    #             raise ThreadingError(ret_val, text)

    # def TTL_stop(self, TTL_channel: int) -> Tuple[bool, str]:
    #     """Stops the TTL tracker thread."""
    #     if self._active_TTLs[TTL_channel] is False:
    #         return False, f"TTL {TTL_channel} not running."

    #     self._active_TTLs[TTL_channel] = False

    #     return True, f"Tracking of TTL {TTL_channel} stopped."

    # TODO: get session id from somewhere and store it as recording self parameter
    # TODO: handle stimulation mappings (SU->input->mzipa->probe) and
    # recording (probe->MZIPA->OS->chan)
    # TODO: implement gain_vec in vb classes for usage in recording settings


# if __name__ == "__main__":
#     VB = ViperBox(start_oe=False, _session_datetime="20210812_123456")
#     VB.connect()
#     # VB.shutdown()
