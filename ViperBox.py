import copy
import logging
import os
import socket
import threading
import time
from pathlib import Path
from typing import Any, List, Tuple

import numpy as np
import requests
from lxml import etree

import NeuraviperPy as NVP
from custom_exceptions import ThreadingError, ViperBoxError
from defaults.defaults import OS2chip
from VB_classes import GeneralSettings, HandleSettings, ProbeSettings, StatusTracking
from XML_handler import (
    check_xml_with_settings,
    update_checked_settings,
)

# TODO: implement rotation of logs to not hog up memory


class ViperBox:
    """Class for interacting with the IMEC Neuraviper API."""

    BUFFER_SIZE = 500
    SKIP_SIZE = 20
    FREQ = 20000
    OS_WRITE_TIME = 1

    def __init__(self, _session_datetime: str, headless=True) -> None:
        """Initialize the ViperBox class."""
        self._working_directory = os.getcwd()

        # ASDFASDF
        self.local_settings = GeneralSettings()
        self.uploaded_settings = GeneralSettings()
        self.tracking = StatusTracking()

        self._session_datetime = _session_datetime

        log_folder = Path.cwd() / "logs"
        log_file = f"log_{self._session_datetime}.log"
        log_folder.mkdir(parents=True, exist_ok=True)
        self._log = log_folder.joinpath(log_file)

        self._default_XML = Path.cwd() / "default_XML"
        self._default_XML.mkdir(parents=True, exist_ok=True)

        self._rec_path: Path | None = None

        # for handler in logging.root.handlers[:]:
        #     logging.root.removeHandler(handler)

        self.logger = logging.getLogger(__name__)
        # handler = logging.StreamHandler(sys.stdout)
        # self.logger.addHandler(handler)

        # self._probe = 0
        # self._probe_recognized = [0, 0, 0, 0]

        if not headless:
            try:
                os.startfile("C:\Program Files\Open Ephys\open-ephys.exe")
            except Exception as e:
                self.logger.warning(
                    f"Can't start Open Ephys, please start it manually. Error: {e}"
                )

        self.logger.info("ViperBox initialized")
        return None

    def connect(
        self,
        probe_list_1: None | List[int] | int = None,
        emulation: bool = False,
        boxless: bool = False,
    ) -> Tuple[bool, str]:
        """Initiates ViperBox and connects to probes. Handle is created and emulation
        type is set.

        TODO: !!!!! all existing data is removed because the local settings are reset.
        """

        # Checks if the ViperBox is connected and connects if not.
        self.logger.info("Connecting to ViperBox...")
        if self.tracking.box_connected is True:
            self.disconnect()

        # check if boxless mode is enabled
        if boxless is True:
            return True, "Boxless mode, no connection to ViperBox"

        # check if probes is a list of 4 elements and only containing ints 1 or 0
        if probe_list_1 is not None:
            if isinstance(probe_list_1, int):
                probe_list_1 = [probe_list_1]
            elif (
                (not all(isinstance(x, int) for x in probe_list_1))
                | (not all(x in [1, 2, 3, 4] for x in probe_list_1))
                | (len(set(probe_list_1)) != len(probe_list_1))
            ):
                err_msg = "Probes should be a list of max 4 integers that are either "
                "1, 2, 3 or 4. No double numbers are allowed."
                self.logger.error(err_msg)
                return False, err_msg
            else:
                pass
        else:
            probe_list_1 = [1]

        # Scan for devices
        NVP.scanBS()
        devices = NVP.getDeviceList(16)
        number_of_devices = len(devices)
        if number_of_devices == 0:
            err_msg = "No device found, please check if the ViperBox is connected"
            self.logger.error(err_msg)
            return False, err_msg
        elif number_of_devices > 1:
            err_msg = """More than one device found, currently this software can only 
                handle one device"""
            self.logger.error(err_msg)
            return False, err_msg
        elif number_of_devices == 1:
            logging.info(f"Device found: {devices[0]}")
            # TODO add handle settings and info and stuffff
            self.local_settings.handles = {1: HandleSettings()}
            pass
        else:
            raise ViperBoxError(f"Error in device list; devices list: {devices}")
        self.tracking.box_connected = True

        # Connect and set up viperbox
        # TODO handlefix: also loop over handles
        self._handle = NVP.createHandle(devices[0].ID)
        self.local_settings.handles[1].handle_id = self._handle
        logging.info(f"Handle created: {self._handle}")
        NVP.openBS(self._handle)
        logging.info(f"BS opened: {self._handle}")
        if (
            emulation is True
        ):  # Choose linear ramp emulation (1 sample shift between channels)
            NVP.setDeviceEmulatorMode(self._handle, NVP.DeviceEmulatorMode.LINEAR)
            NVP.setDeviceEmulatorType(
                self._handle, NVP.DeviceEmulatorType.EMULATED_PROBE
            )
            logging.info("Emulation mode: linear ramp")
        else:
            NVP.setDeviceEmulatorMode(self._handle, NVP.DeviceEmulatorMode.OFF)
            NVP.setDeviceEmulatorType(self._handle, NVP.DeviceEmulatorType.OFF)
            logging.info("Emulation mode: off")
        NVP.openProbes(self._handle)
        logging.info(f"Probes opened: {self._handle}")

        # Connect and set up probes
        # TODO handlefix: also loop over handles
        for probe_1 in probe_list_1:
            try:
                NVP.init(self._handle, probe_1 - 1)  # Initialize all probes
                logging.info(f"Probe {probe_1} initialized: {self._handle}")
                self.local_settings.handles[1].probes[probe_1] = ProbeSettings()
            except Exception as error:
                logging.warning(f"!! Init() exception error, probe {probe_1}: {error}")
                # self._probe_recognized[probe_1-1] = 0
        logging.info(f"API channel opened: {devices[0]}")
        self._deviceId = devices[0].ID
        self.tracking.probe_connected = True

        # TODO handlefix: also loop over handles ASDFASDF
        continue_statement = "ViperBox initialized successfully with probes "
        "{self.local_settings.handles[1].probes.keys()}"
        logging.info(continue_statement)
        return True, continue_statement

    def disconnect(self) -> None:
        NVP.closeProbes(self._handle)
        NVP.closeBS(self._handle)
        NVP.destroyHandle(self._handle)
        self._deviceId = 0
        self.tracking.box_connected = False
        self.tracking.probe_connected = False
        print("API channel closed")

    def shutdown(self) -> None:
        self.disconnect()
        _ = requests.put("http://localhost:37497/api/window", json={"command": "quit"})
        self.logger.info("ViperBox shutdown")

    def verify_xml(self, XML_data: Any, check_topic: str = "all") -> Tuple[bool, str]:
        """Verifies the XML string."""

        tmp_data = copy.deepcopy(self.local_settings)

        result, feedback = check_xml_with_settings(XML_data, tmp_data, check_topic)

        return result, feedback

    # def _set_settings(self, XML_data: Any, reset: bool = False) -> None:
    #     """
    #     Not implemented yet.
    #     reset means that the settings will be reset instead of updated.
    #     """

    #     result, feedback = check_xml_with_settings(XML_data, self.local_settings)
    #     settings_copy = self.local_settings.copy()
    #     add_xml_to_local_settings(XML_data, settings_copy)

    #     # TODO implement XML_file_path and reset
    #     # settings = xml_interpreter(XML_file_path)
    #     settings = [1]
    #     self._settings = settings
    #     # reset means that the settings will be reset instead of updated
    #     # return None

    def recording_settings(
        self,
        xml_string: str | None = None,
        reset: bool = False,
    ) -> Tuple[bool, str]:
        """Loads the recording settings from an XML string or default file."""

        if xml_string == "default":
            # if default_values is True:
            XML_data = etree.parse("defaults/default_recording_settings.xml")
        else:
            try:
                XML_data = etree.fromstring(xml_string)
            except TypeError:
                return (False, "Invalid xml string. Error: {e}")

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return False, "Recording in progress, cannot change settings"

        result, feedback = self.verify_xml(XML_data)
        if result is False:
            return result, feedback

        tmp_settings = copy.deepcopy(self.local_settings)
        if reset:
            tmp_settings.reset_recording_settings()
        updated_tmp_settings = update_checked_settings(
            XML_data, tmp_settings, "recording"
        )

        # Always set settings for entire probe at once.
        for handle in updated_tmp_settings.handles.keys():
            for probe in update_checked_settings.handles[handle].probes.keys():
                for channel in (
                    update_checked_settings.handles[handle].probes[probe].channel.keys()
                ):
                    NVP.selectElectrode(self._handle, probe, channel, 0)
                    NVP.setReference(
                        self._handle,
                        probe,
                        channel,
                        updated_tmp_settings.handles[handle]
                        .probes[probe]
                        .channel[channel]
                        .get_refs,
                    )
                    NVP.setGain(
                        self._handle,
                        probe,
                        channel,
                        updated_tmp_settings.handles[handle]
                        .probes[probe]
                        .channel[channel]
                        .gain,
                    )
                    NVP.setAZ(
                        self._handle, probe, channel, False
                    )  # see email Patrick 08/01/2024

                NVP.writeChannelConfiguration(self._handle, probe, False)

        self.local_settings = updated_tmp_settings
        return True, "Recording settings loaded"

    def stimulation_settings(
        self, XML_file_path: str, reset: bool = False, default_values: bool = False
    ) -> Tuple[bool, str]:
        """Loads the stimulation settings from an XML file."""

        if default_values is True:
            XML_file_path = self._default_XML / "default_stimulation_settings.xml"
            self.logger.debug("Default stimulation settings loaded")
        else:
            try:
                XML_file_path = Path(XML_file_path)
            except TypeError:
                return (
                    False,
                    """Invalid XML file, should be a Path object. Error: {e}""",
                )

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self._settings:
            self._settings_backup = self._settings
        self._settings = self._set_settings(XML_file_path, reset=reset)

        try:
            # Always set settings for entire probe at once.
            for probe in self._settings.handle_sett.probe_stim.keys():
                NVP.setOSimage(
                    self._handle,
                    probe,
                    self._settings.handle_sett.probe_stim[probe].os_data,
                )
                for OS in range(128):
                    NVP.setOSDischargeperm(self._handle, probe, OS, False)
                    NVP.setOSStimblank(self._handle, probe, OS, True)

            for SU in range(8):
                NVP.writeSUConfiguration(
                    self._handle,
                    self._probe,
                    self._settings.handle_sett.stim_unit_sett[SU].SUConfig(),
                )

            self._stimulation_settings = True
        except Exception as e:
            # TODO:
            print(e)
            self._settings = self._settings_backup
            return (
                False,
                """Error in stimulation settings, settings not applied and 
                reverted to previous settings""",
            )

        return True, f"Stimulation settings loaded from {XML_file_path}"

    def start_recording(self, recording_name: str | None = None) -> Tuple[bool, str]:
        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return (
                False,
                """Already recording, first stop recording to start a new 
            recording""",
            )

        if self._recording_settings is False:
            return False, "Recording settings not available"

        # TODO: Start open ephys in separate thread
        self._recording_datetime = time.strftime("%Y%m%d_%H%M%S")

        rec_folder = Path.cwd() / "Recordings"
        recording_name = f"unnamed_recording_{self._recording_datetime}.bin"
        rec_folder.mkdir(parents=True, exist_ok=True)

        if recording_name is None:
            self._rec_path = rec_folder.joinpath(
                f"unnamed_recording_{self._recording_datetime}.bin"
            )
        else:
            self._rec_path = rec_folder.joinpath(
                f"{recording_name}_{self._recording_datetime}.bin"
            )

        NVP.setFileStream(self._handle, str(self._rec_path))
        NVP.enableFileStream(self._handle, str(self._rec_path))
        NVP.arm(self._handle)

        self._rec_start_time = self._time()
        NVP.setSWTrigger(self._handle)
        dt_rec_start = self._time() - self._rec_start_time

        self.stim_file = self._create_file_folder(
            "Stimulations",
            "stimulation_record",
            "xml",
            f"{self._rec_start_time, True}",
        )
        # TODO: replace following with function that writes start of recording with time
        # and deltatime to stim_file
        self._add_stimulation_record(
            "recording_start", self._rec_start_time, dt_rec_start, None
        )

        self.tracking.recording = True

        # TODO: Start thread that sends data to open ephys

        self.logger.info(f"Recording started: {recording_name}")
        return True, f"Recording started: {recording_name}"

    def _time(self) -> float:
        return time.time_ns() / 1e9

    def _add_stimulation_record(
        self,
        type: str,
        start_time: float,
        delta_time: float,
        message: str | None = None,
    ) -> None:
        if start_time is None:
            start_time = time.strftime("%Y%m%d_%H%M%S")
        with open(self.stim_file, "a") as file:
            message = f"Furthermore: {message}."
            file.write(
                f"""{type} at {start_time} s with delta {delta_time} s. 
                {message}"""
            )

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
        return folder.joinpath(file)

    def _start_eo_acquire(self, start_oe=False):
        try:
            # TODO: consider using http lib from standard library
            r = requests.get("http://localhost:37497/api/status")
            if r.json()["mode"] != "ACQUIRE":
                r = requests.put(
                    "http://localhost:37497/api/status", json={"mode": "ACQUIRE"}
                )
        except Exception:
            if start_oe:
                try:
                    os.startfile("C:\Program Files\Open Ephys\open-ephys.exe")
                except Exception as e2:
                    self.logger.warning(
                        f"Can't start Open Ephys, please start it manually. Error: {e2}"
                    )
            else:
                self.logger.warning(
                    """Open Ephys not detected, please start it manually if it is 
                    not running"""
                )

    def _send_data_to_socket(self) -> None:
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
        send_data_read_handle = NVP.streamOpenFile(self._rec_path, self._probe)

        # TODO: remove packages with wrong session
        # status = NVP.readDiagStats(self._handle)
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
        t0 = self._time()
        while True:
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

            t2 = self._time()
            while (t2 - t0) < counter * bufferInterval:
                t2 = self._time()

        NVP.streamClose(self._read_handle)

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

        NVP.arm(self._handle)
        # Close file
        NVP.setFileStream(self._handle, "")

        self.tracking.recording = False

        self._convert_recording()
        # TODO: combine stim history and recording into some file format

        return True, "Recording stopped"

    def _convert_recording(self) -> None:
        """Converts the raw recording into a numpy format."""

        conver_recording_read_handle = NVP.streamOpenFile(self._rec_path, self._probe)

        mtx = self._os2chip_mat()
        while True:
            # TODO: implement skipping of packages by checking:
            # time = 0
            # NAND
            # session id is wrong

            packets = NVP.streamReadData(conver_recording_read_handle, self.BUFFER_SIZE)
            count = len(packets)

            if count < self.BUFFER_SIZE:
                self.logger.warning("Out of packets")
                break

            # TODO: Rearrange data depening on selected gain
            databuffer = np.asarray(
                [packets[i].data for i in range(self.BUFFER_SIZE)], dtype="uint16"
            )
            databuffer = (databuffer @ mtx).T
            databuffer = np.multiply(databuffer, self._settings.gain_vec[:, None])
            self._add_to_zarr(databuffer)

    def _add_to_zarr(self, databuffer: np.ndarray) -> None:
        """Adds the data to the zarr file."""
        # TODO: not_implemented
        pass

    def start_stimulation(self, probe: int, SU_bit_mask: str) -> Tuple[bool, str]:
        """Starts stimulation on the specified probe and SU's."""
        try:
            SU_bit_mask = bin(int(SU_bit_mask, 2))
        except ValueError:
            return (
                False,
                """Invalid SU bitmask, should be 8 bit 
            string. Error: {e}""",
            )

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return False, "Recording in progress, cannot start stimulation"

        # check if settings are uploaded for all the SU's

        tmp_counter = self._time()
        NVP.SUtrig1(self._handle, probe, (SU_bit_mask))
        tmp_delta = self._time() - tmp_counter

        self._add_stimulation_record(
            "stim_start",
            tmp_counter - self._rec_start_time,
            tmp_delta,
            f"probe: {probe}, SU: {SU_bit_mask}",
        )

        return True, f"Stimulation started on probe {probe} for SU's {SU_bit_mask}"

    def TTL_start(
        self, probe: int, TTL_channel: int, SU_bit_mask: str
    ) -> Tuple[bool, str]:
        """Starts TTL on the specified channel."""
        if TTL_channel not in [1, 2]:
            return False, "TTL channel should be 1 or 2"

        try:
            SU_bit_mask = bin(int(SU_bit_mask, 2))
        except ValueError:
            return (
                False,
                """Invalid SU bitmask, should be 8 bit 
            string. Error: {e}""",
            )

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return False, "Recording in progress, cannot start stimulation"

        all_configured, not_configured = self._check_SUs_configured(SU_bit_mask)
        if not all_configured:
            return False, f"Can't trigger SUs {not_configured}"

        threading.Thread(
            target=self._start_TTL_tracker_thread,
            args=(probe, TTL_channel, SU_bit_mask),
        ).start()
        # self._start_TTL_tracker_thread(probe, TTL_channel, SU_bit_mask)

        self._add_stimulation_record(
            "TTL_start",
            self._time() - self._rec_start_time,
            0,
            f"TTL channel: {TTL_channel}",
        )

        return (
            True,
            f"""TTL tracking started on channel {TTL_channel} with SU's 
            {SU_bit_mask} on probe {probe}""",
        )

    def _start_TTL_tracker_thread(
        self, probe: int, TTL_channel: int, SU_bit_mask: str
    ) -> None:
        """Converts the raw recording into a numpy format."""
        # TODO: this can be reduced to one function that listens to both TTL channels

        # note this should be probe specific, not self._probe, that needs to
        # be checked anyway
        TTL_read_handle = NVP.streamOpenFile(self._rec_path, probe)

        self._active_TTLs[TTL_channel] = True

        # mtx = self._os2chip_mat()
        while self._active_TTLs[TTL_channel] is True:
            # TODO: implement skipping of packages by checking:
            # time = 0
            # NAND
            # session id is wrong

            packets = NVP.streamReadData(TTL_read_handle, self.BUFFER_SIZE)
            count = len(packets)

            if count < self.BUFFER_SIZE:
                self.logger.warning("Out of packets")
                break

            # TODO: Rearrange data depending on selected gain
            databuffer = np.asarray(
                [
                    [
                        int(str(bin(packets[0].status))[3:-1][0]),
                        int(str(bin(packets[0].status))[3:-1][1]),
                    ]
                    for i in range(self.BUFFER_SIZE)
                ],
                dtype="uint16",
            )
            if databuffer[:, TTL_channel].any():
                ret_val, text = self.start_stimulation(probe, SU_bit_mask)

            if ret_val is False:
                # tell the user that the stimulation was not started
                raise ThreadingError(ret_val, text)

    def TTL_stop(self, TTL_channel: int) -> Tuple[bool, str]:
        """Stops the TTL tracker thread."""
        if self._active_TTLs[TTL_channel] is False:
            return False, f"TTL {TTL_channel} not running."

        self._active_TTLs[TTL_channel] = False

        return True, f"Tracking of TTL {TTL_channel} stopped."

    # TODO: implement xml_interpreter
    # TODO: Change self._probe everywhere because it doesn't make sense in a mulit
    # probe setup
    # TODO: _check_SUs_configured, returns non configured SUs
    # TODO: add to zarr
    # TODO: get session id from somewhere and store it as recording self parameter
    # TODO: implement start stim
    # TODO: when inputting XML file, probably electrode numbers will be targeted
    # these should be converted to os numbers in stim and rec settings
    # TODO: implement gain_vec in vb classes


if __name__ == "__main__":
    VB = ViperBox(headless=True, _session_datetime="20210812_123456")
    VB.connect()
    # VB.shutdown()
