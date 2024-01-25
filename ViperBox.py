import logging
import os
import socket
import sys
import time
from pathlib import Path
from typing import Tuple

import numpy as np
import requests

import NeuraviperPy as NVP
from custom_exceptions import ViperBoxError
from defaults.defaults import OS2chip
from VB_classes import GeneralSettings

# TODO: implement rotation of logs to not hog up memory


class ViperBox:
    """Class for interacting with the IMEC Neuraviper API."""

    BUFFER_SIZE = 500
    SKIP_SIZE = 20
    FREQ = 20000
    OS_WRITE_TIME = 1

    def __init__(self) -> None:
        """Initialize the ViperBox class."""
        self._working_directory = os.getcwd()
        self._session_datetime = time.strftime("%Y%m%d_%H%M%S")

        log_folder = Path.cwd() / "logs"
        log_file = f"log_{self._session_datetime}.log"
        log_folder.mkdir(parents=True, exist_ok=True)
        self._log = log_folder.joinpath(log_file)

        self._default_XML = Path.cwd() / "default_XML"
        self._default_XML.mkdir(parents=True, exist_ok=True)

        self._rec_path: Path | None = None

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)-8s - %(asctime)s - %(name)s - %(message)s",
            datefmt="%H:%M:%S",
            handlers=[
                logging.FileHandler(self._log),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self._logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        self._logger.addHandler(handler)

        self._connected = False
        # self._settings = Dict()
        self._probe = 0
        self._probe_recognized = [0, 0, 0, 0]

        self._recording = False
        self._recording_settings = False
        self._stimulation_settings = False

        self._SU_busy = "0" * 16
        self._test_mode = False
        self._BIST_number = None
        self._TTL_1 = False
        self._TTL_2 = False
        self._box_connected = False

        try:
            os.startfile("C:\Program Files\Open Ephys\open-ephys.exe")
        except Exception as e:
            self._logger.warning(
                f"Can't start Open Ephys, please start it manually. Error: {e}"
            )

        return None

    def connect(self, emulation=False) -> Tuple[bool, str]:
        self._logger.info("Connecting to ViperBox...")
        if self._connected is True:
            self.disconnect()

        NVP.scanBS()
        devices = NVP.getDeviceList(16)

        number_of_devices = len(devices)
        if number_of_devices == 0:
            err_msg = "No device found, please check if the ViperBox is connected"
            self._logger.error(err_msg)
            return False, err_msg
        elif number_of_devices > 1:
            err_msg = """More than one device found, currently this software can only 
                handle one device"""
            self._logger.error(err_msg)
            return False, err_msg
        elif number_of_devices == 1:
            logging.info(f"Device found: {devices[0]}")
            pass
        else:
            raise ViperBoxError(f"Error in device list; devices list: {devices}")

        # Connect to first device available
        self._handle = NVP.createHandle(devices[0].ID)
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

        for i in range(4):  # For all 4 probes...
            self._probe_recognized[i] = 1
            try:
                NVP.init(self._handle, i)  # Initialize all probes
                logging.info(f"Probe {i} initialized: {self._handle}")
            except Exception as error:
                logging.warning(f"!! Init() exception error, probe {i}: {error}")
                self._probe_recognized[i] = 0
        logging.info(f"API channel opened: {devices[0]}")
        self._deviceId = devices[0].ID
        self._connected = True
        continue_statement = (
            f"ViperBox initialized successfully with probes {self._probe_recognized}"
        )
        logging.info(continue_statement)

        return True, continue_statement

    def disconnect(self) -> None:
        NVP.closeProbes(self._handle)
        NVP.closeBS(self._handle)
        NVP.destroyHandle(self._handle)
        self._deviceId = 0
        self._connected = False
        print("API channel closed")

    def shutdown(self) -> None:
        self.disconnect()
        _ = requests.put("http://localhost:37497/api/window", json={"command": "quit"})
        self._logger.info("ViperBox shutdown")

    def verify_xml(self, type: str, path: Path) -> Tuple[bool, str]:
        return False, "Not implemented yet"

    def xml2dataclass(self, xml_data: Path, reinitiate=False) -> None:
        """
        Not implemented yet.
        re-initiate means that the settings will be re-initiated instead of updated.
        """
        # TODO implement xml_data and reinitiate
        self._settings = GeneralSettings(xml_data)
        # re-initiate means that the settings will be re-initiated instead of updated
        # return None

    def rec_sett(
        self, XML_file: Path, reinitiate: bool = False, default_values: bool = False
    ) -> Tuple[bool, str]:
        if self._connected is False:
            return False, "Not connected to ViperBox"

        if self._recording is True:
            return False, "Recording in progress, cannot change settings"

        if default_values is True:
            xml_data = self._default_XML / "default_rec_sett.xml"
            self._logger.debug("Default recording settings loaded")
        else:
            # TODO: fix xml standard file
            # xml_data = "XML_file"
            self._logger.debug(f"Recording settings loaded from input file {XML_file}")

        self.xml2dataclass(xml_data, reinitiate=reinitiate)

        # Always set settings for entire probe at once.
        for probe in self._settings.handle_sett.probe_rec.keys():
            for channel in range(64):
                NVP.selectElectrode(self._handle, probe, channel, 0)
                NVP.setReference(
                    self._handle,
                    probe,
                    channel,
                    self._settings.handle_sett.probe_rec[probe][channel].references,
                )
                NVP.setGain(
                    self._handle,
                    probe,
                    channel,
                    self._settings.handle_sett.probe_rec[probe][channel].gain,
                )
                NVP.setAZ(
                    self._handle, probe, channel, False
                )  # see email Patrick 08/01/2024

            NVP.writeChannelConfiguration(self._handle, self._probe, False)

        return True, f"Recording settings loaded from {XML_file}"

    def stim_sett(
        self, XML_file: str, reinitiate: bool = False, default_values: bool = False
    ) -> Tuple[bool, str]:
        if self._connected is False:
            return False, "Not connected to ViperBox"

        if default_values is True:
            self._default_XML / "default_stim_sett.xml"
            self._logger.debug("Default stimulation settings loaded")
        else:
            self._logger.debug(
                f"Stimulation settings loaded from input file {XML_file}"
            )

        self._settings_backup = self._settings
        # self._settings = self.xml2dataclass(xml_data, reinitiate=reinitiate)

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

        return True, f"Stimulation settings loaded from {XML_file}"

    def start_recording(self, recording_name: str | None = None) -> Tuple[bool, str]:
        if self._connected is False:
            return False, "Not connected to ViperBox"

        if self._recording is False:
            return False, "Recording not started"

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

        self.stim_file = self.create_file_folder(
            "Stimulations",
            "stimulation_record",
            "xml",
            f"{self._rec_start_time, True}",
        )
        # TODO: replace following with function that writes start of recording with time
        # and deltatime to stim_file
        self._add_stimulation_record(
            "recording_start", self._rec_start_time, dt_rec_start, None, None
        )

        self._recording = True

        # TODO: Start thread that sends data to open ephys

        self._logger.info(f"Recording started: {recording_name}")
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

    def create_file_folder(
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

    def start_eo_acquire(self, start_oe=False):
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
                    self._logger.warning(
                        f"Can't start Open Ephys, please start it manually. Error: {e2}"
                    )
            else:
                self._logger.warning(
                    """Open Ephys not detected, please start it manually if it is 
                    not running"""
                )

    def send_data_to_socket(self) -> None:
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
        self._read_handle = NVP.streamOpenFile(self._rec_path, self._probe)

        # TODO: remove packages with wrong session
        # status = NVP.readDiagStats(self._handle)
        # skip_packages = status.session_mismatch
        # print('skip_packages: ', skip_packages)
        # dump_count = 0
        # while dump_count < skip_packages:
        #     _ = NVP.streamReadData(self._read_handle, self.SKIP_SIZE)
        #     dump_count += self.SKIP_SIZE
        # print('dump_count: ', dump_count)

        self._logger.info("Started sending data to Open Ephys")
        mtx = self.os2chip_mat()
        counter = 0
        t0 = self._time()
        while True:
            counter += 1

            packets = NVP.streamReadData(self._read_handle, self.BUFFER_SIZE)
            count = len(packets)

            if count < self.BUFFER_SIZE:
                self._logger.warning("Out of packets")
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

    def os2chip_mat(self):
        mtx = np.zeros((64, 60), dtype="uint16")
        for k, v in OS2chip.items():
            mtx[k - 1][v - 1] = 1
        return mtx

    def stop_recording(self) -> Tuple[bool, str]:
        if self._connected is False:
            return False, "Not connected to ViperBox"

        if self._recording is False:
            return False, "Recording not started"

        NVP.arm(self._handle)
        # Close file
        NVP.setFileStream(self._handle, "")

        self._recording = False

        self.convert_recording()
        # TODO: combine stim history and recording into some file format

        return True, "Recording stopped"

    def convert_recording(self) -> None:
        """Converts the raw recording into a numpy format."""

        self._read_handle_conversion = NVP.streamOpenFile(self._rec_path, self._probe)

        mtx = self.os2chip_mat()
        while True:
            # TODO: implement skipping of packages by checking:
            # time = 0
            # NAND
            # session id is wrong

            packets = NVP.streamReadData(self._read_handle, self.BUFFER_SIZE)
            count = len(packets)

            if count < self.BUFFER_SIZE:
                self._logger.warning("Out of packets")
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

        if self._connected is False:
            return False, "Not connected to ViperBox"

        if self._recording is True:
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

    # TODO: not_implemented
    # TODO: get session id from somewhere and store it as recording self parameter
    # TODO: implement start stim
    # TODO: when inputting XML file, probably electrode numbers will be targeted
    # these should be converted to os numbers in stim and rec settings
    # TODO: implement gain_vec in vb classes


VB = ViperBox()
VB.connect()
