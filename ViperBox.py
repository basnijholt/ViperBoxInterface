import logging
import os
import sys
import time
from pathlib import Path
from typing import Tuple

import NeuraviperPy as NVP
from custom_exceptions import ViperBoxError

# TODO: implement rotation of logs to not hog up memory


class ViperBox:
    """Class for interacting with the IMEC Neuraviper API."""

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

    def verify_xml(self, type: str, path: Path) -> Tuple[bool, str]:
        return False, "Not implemented yet"

    def xml2dataclass(self, xml_data) -> None:
        "Not implemented yet"
        return None

    def rec_sett(self, XML_file: str, default_values: bool = False) -> Tuple[bool, str]:
        if self._connected is False:
            return False, "Not connected to ViperBox"

        if self._recording is True:
            return False, "Recording in progress, cannot change settings"

        if default_values is True:
            xml_data = self._default_XML / "default_rec_sett.xml"
            self._logger.debug("Default recording settings loaded")
        else:
            xml_data = XML_file
            self._logger.debug(f"Recording settings loaded from input file {XML_file}")

        self._settings = self.xml2dataclass(xml_data)

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
        self, XML_file: str, default_values: bool = False
    ) -> Tuple[bool, str]:
        if self._connected is False:
            return False, "Not connected to ViperBox"

        if default_values is True:
            xml_data = self._default_XML / "default_stim_sett.xml"
            self._logger.debug("Default stimulation settings loaded")
        else:
            xml_data = XML_file
            self._logger.debug(
                f"Stimulation settings loaded from input file {XML_file}"
            )

        self._settings = self.xml2dataclass(xml_data)

        # Check if SU busy, currently not implemented

        self._settings_backup = self._settings

        for probe in self._settings.handle_sett.probe_stim.keys():
            NVP.setOSimage(
                self._handle,
                probe,
                self._settings.handle_sett.probe_stim[probe].stim_elec_map,
            )
            for OS in range(128):
                NVP.setOSDischargeperm(self._handle, probe, OS, False)
                NVP.setOSStimblank(self._handle, probe, OS, True)

        # for SU in
        # NVP.writeSUConfiguration(
        #     self._handle, self._probe, self._settings.handle_sett.probe_stim
        # )

        return True, f"Stimulation settings loaded from {XML_file}"


VB = ViperBox()
VB.connect()
