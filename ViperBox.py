import copy
import logging
import os
import socket
import threading
import time
from pathlib import Path
from typing import Any, Tuple

import numpy as np
import requests
from lxml import etree

import NeuraviperPy as NVP
from custom_exceptions import ViperBoxError
from defaults.defaults import OS2chip
from VB_classes import (
    GeneralSettings,
    HandleSettings,
    ProbeSettings,
    StatusTracking,
    parse_numbers,
    printable_dtd,
)
from XML_handler import (
    add_to_stimrec,
    check_xml_with_settings,
    create_empty_xml,
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

        self.local_settings = GeneralSettings()
        self.uploaded_settings = GeneralSettings()
        self.tracking = StatusTracking()
        self._handle_ptrs = {}

        self._session_datetime = _session_datetime
        self._rec_start_time: float | None = None

        log_folder = Path.cwd() / "logs"
        log_file = f"log_{self._session_datetime}.log"
        log_folder.mkdir(parents=True, exist_ok=True)
        self._log = log_folder.joinpath(log_file)
        self.stim_file_path: None | Path = None

        self._default_XML = Path.cwd() / "default_XML"
        self._default_XML.mkdir(parents=True, exist_ok=True)

        self._rec_path: Path | None = None

        self.headless = headless

        # for handler in logging.root.handlers[:]:
        #     logging.root.removeHandler(handler)

        self.logger = logging.getLogger(__name__)
        # handler = logging.StreamHandler(sys.stdout)
        # self.logger.addHandler(handler)

        if not self.headless:
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
        probe_list: str = "1,2,3,4",
        emulation: bool = False,
        boxless: bool = False,
    ) -> Tuple[bool, str]:
        """Initiates ViperBox and connects to probes. Handle is created and emulation\
        type is set.

        TODO: !!!!! all existing data is removed because the local settings are reset.
        """
        start_time = self._time()

        # Checks if the ViperBox is connected and connects if not.
        self.logger.info("Connecting to ViperBox...")
        if self.tracking.box_connected is True:
            self.disconnect()

        # check if boxless mode is enabled
        if boxless is True:
            return True, "Boxless mode, no connection to ViperBox"

        # check if probes is a list of 4 elements and only containing ints 1 or 0
        try:
            probe_list_int = parse_numbers(probe_list, [0, 1, 2, 3])
        except ValueError as e:
            return False, f"Invalid probe list: {e}"

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
                handle one device"""
            self.logger.error(err_msg)
            return False, err_msg
        elif number_of_devices == 1:
            logging.info(f"Device found: {devices[0]}")
            # TODO add handle settings and info and stuffff
            self.local_settings.handles = {0: HandleSettings()}
            pass
        else:
            raise ViperBoxError(f"Error in device list; devices list: {devices}")
        self.tracking.box_connected = True

        # Connect and set up viperbox
        # TODO handlefix: also loop over handles
        handle = 0
        tmp_handel = NVP.createHandle(devices[0].ID)
        self._handle_ptrs[handle] = tmp_handel
        # self._handle_ptrs[handle] = NVP.createHandle(devices[0].ID)
        logging.info(f"Handle created: {self._handle_ptrs[handle]}")
        NVP.openBS(self._handle_ptrs[handle])
        logging.info(f"BS opened: {self._handle_ptrs[handle]}")
        if (
            emulation is True
        ):  # Choose linear ramp emulation (1 sample shift between channels)
            NVP.setDeviceEmulatorMode(
                self._handle_ptrs[handle], NVP.DeviceEmulatorMode.LINEAR
            )
            NVP.setDeviceEmulatorType(
                self._handle_ptrs[handle], NVP.DeviceEmulatorType.EMULATED_PROBE
            )
            logging.info("Emulation mode: linear ramp")
        else:
            NVP.setDeviceEmulatorMode(
                self._handle_ptrs[handle], NVP.DeviceEmulatorMode.OFF
            )
            NVP.setDeviceEmulatorType(
                self._handle_ptrs[handle], NVP.DeviceEmulatorType.OFF
            )
            logging.info("Emulation mode: off")
        print(
            f"""{self._time()-start_time} finished setting emulation, starting \
            opening probes"""
        )
        NVP.openProbes(self._handle_ptrs[handle])
        logging.info(f"Probes opened: {self._handle_ptrs[handle]}")

        print(f"{self._time()-start_time} opened probes, starting initialization")
        # Connect and set up probes
        # TODO handlefix: also loop over handles
        for probe in probe_list_int:
            print(f"type probe: {type(probe)}")
            try:
                NVP.init(self._handle_ptrs[handle], int(probe))  # Initialize all probes
                logging.info(f"Probe {probe} initialized: {self._handle_ptrs[handle]}")
                self.local_settings.handles[0].probes[probe] = ProbeSettings()
            except Exception as error:
                logging.warning(f"!! Init() exception error, probe {probe}: {error}")
        logging.info(f"API channel opened: {devices[0]}")
        self._deviceId = devices[0].ID
        self.tracking.probe_connected = True
        print(self.local_settings)
        self.uploaded_settings = copy.deepcopy(self.local_settings)

        # TODO handlefix: also loop over handles
        continue_statement = f"""ViperBox initialized successfully with probes 
        {self.local_settings.connected}"""
        logging.info(continue_statement)
        return True, continue_statement

    def disconnect(self) -> None:
        """Disconnects from the ViperBox and closes the API channel."""

        # TODO handlefix: also loop over handles
        handle = 0
        NVP.closeProbes(self._handle_ptrs[handle])
        NVP.closeBS(self._handle_ptrs[handle])
        NVP.destroyHandle(self._handle_ptrs[handle])
        self._deviceId = 0
        self.tracking.box_connected = False
        self.tracking.probe_connected = False
        self.uploaded_settings = GeneralSettings()
        print("API channel closed")

    def shutdown(self) -> None:
        self.disconnect()
        if not self.headless:
            _ = requests.put(
                "http://localhost:37497/api/window", json={"command": "quit"}
            )
        self.logger.info("ViperBox shutdown")

    def _write_recording_settings(self, updated_tmp_settings):
        for handle in updated_tmp_settings.handles.keys():
            print(f"handle: {handle}")
            for probe in updated_tmp_settings.handles[handle].probes.keys():
                # TODO: ugly; probe should be either 0 indexed or 1 indexed
                probe = probe
                print(f"probe: {probe}")
                for channel in (
                    updated_tmp_settings.handles[handle].probes[probe].channel.keys()
                ):
                    NVP.selectElectrode(self._handle_ptrs[handle], probe, channel, 0)
                    NVP.setReference(
                        self._handle_ptrs[handle],
                        probe,
                        channel,
                        updated_tmp_settings.handles[handle]
                        .probes[probe]
                        .channel[channel]
                        .get_refs,
                    )
                    NVP.setGain(
                        self._handle_ptrs[handle],
                        probe,
                        channel,
                        updated_tmp_settings.handles[handle]
                        .probes[probe]
                        .channel[channel]
                        .gain,
                    )
                    NVP.setAZ(
                        self._handle_ptrs[handle], probe, channel, False
                    )  # see email Patrick 08/01/2024

                NVP.writeChannelConfiguration(self._handle_ptrs[handle], probe, False)

    def _write_stimulation_settings_to_viperbox(self, updated_tmp_settings):
        for handle in updated_tmp_settings.handles.keys():
            for probe in updated_tmp_settings.handles[handle].probes.keys():
                # Always set settings for entire probe at once.
                NVP.setOSimage(
                    self._handle_ptrs[handle],
                    probe,
                    updated_tmp_settings.handles[handle].probes[probe].os_data,
                )
                for OS in range(128):
                    NVP.setOSDischargeperm(self._handle_ptrs[handle], probe, OS, False)
                    NVP.setOSStimblank(self._handle_ptrs[handle], probe, OS, True)

            for SU in range(8):
                NVP.writeSUConfiguration(
                    self._handle_ptrs[handle],
                    probe,
                    SU,
                    *updated_tmp_settings.handles[handle]
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

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return False, "Recording in progress, cannot change settings"

        if default_values is True:
            XML_data = etree.parse("defaults/default_recording_settings.xml")
        else:
            try:
                XML_data = etree.fromstring(xml_string)
            except TypeError:
                return (False, "Invalid xml string. Error: {e}")

        # make temporary copy of settings
        tmp_local_settings = copy.deepcopy(self.local_settings)

        printable_dtd(f"local_settings: {self.local_settings}")
        result, feedback = check_xml_with_settings(
            XML_data, tmp_local_settings, "recording"
        )
        if result is False:
            return result, feedback

        if reset:
            tmp_local_settings.reset_recording_settings()
        updated_tmp_settings = update_checked_settings(
            XML_data, tmp_local_settings, "recording"
        )
        printable_dtd(f"updated_tmp_settings: {updated_tmp_settings}")

        try:
            # Always set settings for entire probe at once.
            # TODO handlefix
            self._write_recording_settings(updated_tmp_settings)
        except Exception as e:
            return (
                False,
                f"""Error in uploading recording settings, settings not applied and 
                reverted to previous settings. Error: {e}""",
            )
        self.tracking.recording_settings_uploaded = True
        self.local_settings = updated_tmp_settings
        self.uploaded_settings = copy.deepcopy(self.local_settings)
        return True, "Recording settings loaded"

    def _write_stimulation_settings_to_stimrec(
        self, updated_tmp_settings, start_time, dt_time
    ):
        if self.stim_file_path:
            for handle in updated_tmp_settings.handles.keys():
                for probe in updated_tmp_settings.handles[handle].probes.keys():
                    for configuration in (
                        updated_tmp_settings.handles[handle]
                        .probes[probe]
                        .stim_unit_sett.keys()
                    ):
                        add_to_stimrec(
                            self.stim_file_path,
                            "Settings",
                            "Configuration",
                            {
                                "handle": handle,
                                "probe": probe,
                                "stimunit": configuration,
                                **updated_tmp_settings.handles[handle]
                                .probes[probe]
                                .stim_unit_sett[configuration]
                                .__dict__,
                            },
                            start_time,
                            dt_time,
                        )
                    for mapping in (
                        updated_tmp_settings.handles[handle]
                        .probes[probe]
                        .stim_unit_elec.keys()
                    ):
                        add_to_stimrec(
                            self.stim_file_path,
                            "Settings",
                            "Mapping",
                            {
                                "handle": handle,
                                "probe": probe,
                                "stimunit": mapping,
                                "electrodes": updated_tmp_settings.handles[handle]
                                .probes[probe]
                                .stim_unit_elec[mapping],
                            },
                            start_time,
                            dt_time,
                        )
        return True, "Stimulation settings wrote to stimrec file"

    def stimulation_settings(
        self, xml_string: str, reset: bool = False, default_values: bool = False
    ) -> Tuple[bool, str]:
        """Loads the stimulation settings from an XML file."""

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if default_values is True:
            XML_data = etree.parse("defaults/default_stimulation_settings.xml")
        else:
            try:
                XML_data = etree.fromstring(xml_string)
            except TypeError:
                return (False, "Invalid xml string. Error: {e}")

        tmp_local_settings = copy.deepcopy(self.local_settings)

        result, feedback = check_xml_with_settings(
            XML_data, tmp_local_settings, "stimulation"
        )
        if result is False:
            return result, feedback

        if reset:
            tmp_local_settings.reset_stimulation_settings()
        updated_tmp_settings = update_checked_settings(
            XML_data, tmp_local_settings, "stimulation"
        )

        # TODO handlefix
        start_time = self._time()
        try:
            self._write_stimulation_settings_to_viperbox(updated_tmp_settings)
            self.uploaded_settings = copy.deepcopy(updated_tmp_settings)
        except Exception:
            return (
                False,
                """Error in uploading stimulation settings, settings not applied and
                reverted to previous settings""",
            )
        dt_time = self._time() - start_time

        self.tracking.stimulation_settings_uploaded = True
        self.local_settings = copy.deepcopy(updated_tmp_settings)

        # if stim_file_path doesn't exist, the recording hasn't started yet
        # settings will be written to stimrec at start
        if self.stim_file_path:
            result, feedback = self._write_stimulation_settings_to_stimrec(
                updated_tmp_settings, start_time, dt_time
            )
            if result is False:
                return result, feedback

        return True, "Stimulation settings loaded"

    def verify_xml_with_local_settings(
        self, XML_data: Any, check_topic: str = "all"
    ) -> Tuple[bool, str]:
        """API Verifies the XML string."""

        tmp_data = copy.deepcopy(self.local_settings)

        result, feedback = check_xml_with_settings(XML_data, tmp_data, check_topic)

        return result, feedback

    def default_settings(self) -> Tuple[bool, str]:
        """Loads the stimulation settings from an XML file."""

        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        XML_data = etree.parse("defaults/default_stimulation_settings.xml")

        tmp_local_settings = copy.deepcopy(self.local_settings)
        result, feedback = check_xml_with_settings(XML_data, tmp_local_settings, "all")
        if result is False:
            return result, feedback

        tmp_local_settings.reset_stimulation_settings()

        updated_tmp_settings = update_checked_settings(
            XML_data, tmp_local_settings, "recording"
        )
        updated_tmp_settings = update_checked_settings(
            XML_data, updated_tmp_settings, "stimulation"
        )

        # TODO handlefix
        start_time = self._time()
        try:
            self._write_recording_settings(updated_tmp_settings)
        except Exception:
            return (
                False,
                """Error in uploading recording settings, settings not applied and 
                reverted to previous settings""",
            )
        try:
            self._write_stimulation_settings_to_viperbox(updated_tmp_settings)
        except Exception:
            return (
                False,
                """Error in uploading stimulation settings, settings not applied and 
                reverted to previous settings""",
            )
        dt_time = self._time() - start_time

        for handle in updated_tmp_settings.handles.keys():
            for probe in updated_tmp_settings.handles[handle].probes.keys():
                for channel in (
                    self.uploaded_settings.handles[handle].probes[probe].channel.keys()
                ):
                    add_to_stimrec(
                        self.stim_file_path,
                        "Settings",
                        "Channel",
                        {
                            "handle": handle,
                            "probe": probe,
                            "channel": channel,
                            **self.uploaded_settings.handles[handle]
                            .probes[probe]
                            .channel[channel]
                            .__dict__,
                        },
                        start_time,
                        dt_time,
                    )
                for configuration in (
                    updated_tmp_settings.handles[handle]
                    .probes[probe]
                    .stim_unit_sett.keys()
                ):
                    add_to_stimrec(
                        self.stim_file_path,
                        "Settings",
                        "Configuration",
                        {
                            "handle": handle,
                            "probe": probe,
                            "stimunit": configuration,
                            **updated_tmp_settings.handles[handle]
                            .probes[probe]
                            .stim_unit_sett[configuration]
                            .__dict__,
                        },
                        start_time,
                        dt_time,
                    )
                for mapping in (
                    updated_tmp_settings.handles[handle]
                    .probes[probe]
                    .stim_unit_elec.keys()
                ):
                    add_to_stimrec(
                        self.stim_file_path,
                        "Settings",
                        "Mapping",
                        {
                            "handle": handle,
                            "probe": probe,
                            "stimunit": mapping,
                            "electrodes": updated_tmp_settings.handles[handle]
                            .probes[probe]
                            .stim_unit_elec[mapping],
                        },
                        start_time,
                        dt_time,
                    )

        self.tracking.recording_settings_uploaded = True
        self.tracking.stimulation_settings_uploaded = True
        self.local_settings = updated_tmp_settings
        self.uploaded_settings = copy.deepcopy(self.local_settings)

        return True, "Stimulation settings loaded"

    def start_recording(self, recording_name: str | None = None) -> Tuple[bool, str]:
        """Start

        Tests:
        - start recording with incomplete settings uploaded
        """
        if self.tracking.box_connected is False:
            return False, "Not connected to ViperBox"

        if self.tracking.recording is True:
            return (
                False,
                """Already recording, first stop recording to start a new 
            recording""",
            )

        # TODO this should check if recording settings are available for all
        # connected handles
        print("Check if all recording channels have settings, this is necessaru")
        for handle in self.uploaded_settings.handles.keys():
            for probe in self.uploaded_settings.handles[handle].probes.keys():
                if (
                    len(self.uploaded_settings.handles[handle].probes[probe].channel)
                    != 64
                ):
                    return (
                        False,
                        """Recording settings not available for all channels on 
                        handle {handle}, probe {probe}. Consider first uploading 
                        default settings for all channels, then upload your custom 
                        settings and then try again.""",
                    )

        # TODO: Start open ephys in separate thread
        self._recording_datetime = time.strftime("%Y%m%d_%H%M%S")

        rec_folder = Path.cwd() / "Recordings"
        rec_folder.mkdir(parents=True, exist_ok=True)
        self.recording_name = recording_name

        print("create recording filename")
        if self.recording_name is None:
            self._rec_path = rec_folder.joinpath(
                f"unnamed_recording_{self._recording_datetime}.bin"
            )
        else:
            self._rec_path = rec_folder.joinpath(
                f"{self.recording_name}_{self._recording_datetime}.bin"
            )

        print("set filestream, enable filestream and arm")
        NVP.setFileStream(self._handle_ptrs[handle], str(self._rec_path))
        print("the problem is enable filestream")
        NVP.enableFileStream(self._handle_ptrs[handle], str(self._rec_path))
        print("the problem is arm")
        NVP.arm(self._handle_ptrs[handle])

        print("set sw trigger")
        self._rec_start_time = self._time()
        NVP.setSWTrigger(self._handle_ptrs[handle])
        dt_rec_start = self._time()  # - self._rec_start_time

        print("create empty stimrec file")
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
        # TODO record: replace following with function that writes start
        # of recording with time and deltatime to stim_file

        # Create stimulation record
        print(f"initialize stimrec file: {self.stim_file_path}")
        create_empty_xml(self.stim_file_path)

        print(f"write recording settingss to stimrec: {self.uploaded_settings}")
        for handle in self.uploaded_settings.handles.keys():
            for probe in self.uploaded_settings.handles[handle].probes.keys():
                for channel in (
                    self.uploaded_settings.handles[handle].probes[probe].channel.keys()
                ):
                    add_to_stimrec(
                        self.stim_file_path,
                        "Settings",
                        "Channel",
                        {
                            "handle": handle,
                            "probe": probe,
                            "channel": channel,
                            **self.uploaded_settings.handles[handle]
                            .probes[probe]
                            .channel[channel]
                            .__dict__,
                        },
                        -1.0,
                        -1.0,
                    )

        print("write stimulation settings to stimrec")
        self._write_stimulation_settings_to_stimrec(self.local_settings, -1.0, -1.0)

        print("write recording start to stimrec")
        add_to_stimrec(
            self.stim_file_path,
            "Instructions",
            "Instruction",
            {"filename": self.recording_name, "instruction_type": "recording_start"},
            0.0,
            dt_rec_start,
        )

        print("set flag")
        self.tracking.recording = True

        # TODO: Check if this works.
        threading.Thread(target=self._start_eo_acquire, args=(True,)).start()
        # self._start_eo_acquire(True)
        # TODO fix probe number
        self.oe_socket = True
        threading.Thread(target=self._send_data_to_socket, args=(0,)).start()

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
        return folder.joinpath(file)

    def _start_eo_acquire(self, start_oe=False):
        try:
            # TODO: consider using http lib from standard library
            r = requests.get("http://localhost:37497/api/status")
            print(r.json())
            if r.json()["mode"] != "ACQUIRE":
                r = requests.put(
                    "http://localhost:37497/api/status", json={"mode": "ACQUIRE"}
                )
        except Exception:
            if start_oe:
                try:
                    print("Starting Open Ephys")
                    os.startfile("C:\Program Files\Open Ephys\open-ephys.exe")
                    r = requests.get("http://localhost:37497/api/status", timeout=5)
                    if r.json()["mode"] != "ACQUIRE":
                        try:
                            r = requests.put(
                                "http://localhost:37497/api/status",
                                json={"mode": "ACQUIRE"},
                                timeout=5,
                            )
                        except Exception as e:
                            self.logger.warning(
                                f"Can't start Open Ephys, please start it manually. \
                                    Error: {e}"
                            )
                except Exception as e2:
                    self.logger.warning(
                        f"Can't start Open Ephys, please start it manually. Error: {e2}"
                    )
            else:
                self.logger.warning(
                    """Open Ephys not detected, please start it manually if it is 
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

        print("start streamOpenFile")
        # TODO: How to handle data streams from multiple probes? align on timestamp?
        send_data_read_handle = NVP.streamOpenFile(str(self._rec_path), probe)
        print("streamOpenFile handle created")

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

            t2 = self._time()
            while (t2 - t0) < counter * bufferInterval:
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

        start_time = self._time()
        handle = 0
        NVP.arm(self._handle_ptrs[handle])
        # Close file
        NVP.setFileStream(self._handle_ptrs[handle], "")
        dt_time = self._time() - start_time
        self.oe_socket = False

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

    def _convert_SU_list(self, SU_list):
        # convert SUs to NVP format
        SU_string = "".join(["1" if i in SU_list else "0" for i in range(1, 9)])
        return int(SU_string, 2)

    def start_stimulation(
        self, handles: str, probes: str, SU_input: str
    ) -> Tuple[bool, str]:
        """Starts stimulation on the specified handle(s), probe(s) and SU(s).
        First checks if the SUs are configured for their respective handles and probes.

        Arguments:
        - handles: str - all handles to start stimulation in
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
                """No recording in progress, cannot start stimulation, please 
                start recording first""",
            )

        # SU_dict = {handle1: {probe1: [1,2,5], probe2: [3,4,6]}}
        SU_dict: Any = {}
        # Check if handles, probes and SUs are in right format and properly configured
        # i.e, have waveform configured
        # Using try/except to catch ValueError from parse_numbers
        for handle in parse_numbers(
            handles, list(self.uploaded_settings.handles.keys())
        ):
            SU_dict[handle] = {}
            for probe in parse_numbers(
                probes,
                list(self.uploaded_settings.handles[handle].probes.keys()),
            ):
                SU_dict[handle][probe] = parse_numbers(
                    SU_input,
                    list(
                        self.uploaded_settings.handles[handle]
                        .probes[probe]
                        .stim_unit_sett.keys()
                    ),
                )
        #                 except ValueError as e:
        #                     return_statement = "SU settings not available on probe "
        #                     f"{probe}, on handle {handle} are not available: {e}"
        #                     return False, return_statement
        #         except ValueError as e:
        #             return_statement
        #             return (
        #                 False,
        #                 f"""Probe {probe} on handle {handle} doesn't seem to be
        #                 connected: {e}""",
        #             )
        # except ValueError as e:
        #     return False, f"Handle {handle} doesn't seem to be connected: {e}"

        SU_dict = {
            int(handle): {
                int(probe): self._convert_SU_list(sulist)
                for probe, sulist in probes.items()
            }
            for handle, probes in SU_dict.items()
        }

        # Trigger SUs
        for handle in SU_dict.keys():
            for probe in SU_dict[handle].keys():
                tmp_counter = self._time()
                # TODO could be faster by not having to do this converstion here
                NVP.SUtrig1(
                    self._handle_ptrs[handle],
                    probe,
                    SU_dict[handle][probe],
                )
                tmp_delta = self._time() - tmp_counter

                add_to_stimrec(
                    self.stim_file_path,
                    "Instructions",
                    "Instruction",
                    {
                        "filename": self.recording_name,
                        "instruction_type": "stimulation_start",
                        "handles": SU_dict.keys(),
                        "probes": {
                            handle: probes.keys() for handle, probes in SU_dict.items()
                        },
                        "SU_dict": SU_dict,
                    },
                    tmp_counter,
                    tmp_delta,
                )

        return_statement = f"Stimulation started on handles {handles} probe "
        f"{probes} for SU's {SU_dict[handle][probe]}"
        return True, return_statement

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
