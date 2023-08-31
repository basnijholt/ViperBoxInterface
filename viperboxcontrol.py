from typing import List, Optional, Type, Any, Tuple
from time import strftime

import NeuraviperPy as NVP
import threading
import time
import numpy as np
import os
import socket
import logging
from parameters import (
    ConfigurationParameters,
)

logging.basicConfig(level=logging.INFO)


class ViperBoxControl:
    """
    Controller class for handling recordings from the ViperBox device.
    """

    BUFFER_SIZE = 500
    SKIP_SIZE = 20
    FREQ = 20000

    def __init__(
        self,
        recording_file_name: str,
        probe: int,
        recording_file_location: str = os.getcwd(),
        metadata_stream: Optional[List[Any]] = None,
    ) -> None:
        """Initializes the ViperBoxControl object."""
        # TODO: check which other parameters logically are part of self and init.
        self._recording = False
        self._recording_file_name = (
            recording_file_name + strftime("_%Y-%m-%d_%H-%M-%S") + ".bin"
        )
        self._recording_file_location = recording_file_location
        self._metadata_stream: Optional[List[Any]] = metadata_stream
        self._probe = probe
        try:
            self._handle: Type[Any] = NVP.createHandle(0)
            NVP.openBS(self._handle)
        except Exception as e:
            logging.error(f"Error while setting up handle: {e}")
            return None

    @property
    def _recording_path(self) -> Optional[str]:
        """Return the combined path of the recording file location and name."""
        if self._recording_file_name and self._recording_file_location:
            return self._recording_file_location + self._recording_file_name
        return None

    @staticmethod
    def _currentTime() -> float:
        """Return the current time in seconds since the epoch."""
        return time.time_ns() / (10**9)

    def control_rec_setup(
        self,
        file_name: str,
        file_location: str,
        probe: int,
        reference_electrode: Optional[int] = None,
        electrode_mapping: Optional[bytes] = None,
        metadata_stream: Optional[List[Any]] = None,
        emulated: bool = False,
    ) -> bool:
        """
        Set up the recording controller.

        :param file_name: Name of the recording file.
        :param file_location: Directory location to save the recording file.
        :param probe: Probe number.
        :param reference_electrode: (Optional) Reference electrode number.
        :param electrode_mapping: (Optional) Electrode mapping as bytes.
        :param metadata_stream: (Optional) Metadata stream.
        :param emulated: (Optional) Flag to set the device up in emulation mode.

        :return: True if setup was successful, False otherwise.
        """

        if not (0 <= probe <= 3):
            raise ValueError(
                "Error: Invalid probe value. Expected a value between 0 and 3."
            )
        if not (0 <= reference_electrode <= 8):
            raise ValueError(
                "Error: Invalid reference electrode. Expected a value between 0 and 8."
            )

        self._metadata_stream = metadata_stream

        if emulated:
            NVP.setDeviceEmulatorMode(self._handle, NVP.DeviceEmulatorMode.LINEAR)
            NVP.setDeviceEmulatorType(
                self._handle, NVP.DeviceEmulatorType.EMULATED_PROBE
            )

        NVP.openProbes(self._handle)
        NVP.init(self._handle, probe)

        self._recording_file_name = file_name
        self._recording_file_location = file_location
        NVP.setFileStream(self._handle, self._recording_path)
        NVP.enableFileStream(self._handle, True)

        NVP.arm(self._handle)

        # Uncommented and included the setup as needed:
        if electrode_mapping:
            for channel, electrode in enumerate(electrode_mapping):
                NVP.selectElectrode(self._handle, probe, channel, electrode)

            # NVP.setReference(self._handle, probe, 0, reference_electrode)
            NVP.writeChannelConfiguration(self._handle, probe)

        return True

    def combine(self, metadata_stream: List[Any]) -> None:
        """
        Placeholder method for processing metadata stream.

        :param metadata_stream: Metadata stream to process.
        """
        pass

    def send_data_to_socket(self) -> None:
        """Send data packets to a UDP socket, such that Open Ephys and other systems
        can receive the raw data."""

        bufferInterval: float = self.BUFFER_SIZE / self.FREQ

        serverAddressPort: Tuple[str, int] = ("127.0.0.1", 9001)
        UDPClientSocket: socket.socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )

        self._read_handle = NVP.streamOpenFile(self._recording_path, self._probe)

        status = NVP.readDiagStats(self._handle)
        skip_packages = status.session_mismatch
        dump_count = 0
        while dump_count < skip_packages:
            _ = NVP.streamReadData(self._read_handle, self.SKIP_SIZE)
            dump_count += self.SKIP_SIZE

        # # reads one packet to get session id of last fifo,
        # # then skip all packets with that session id.
        # idpacket = NVP.streamReadData(self._read_handle, 1)  # 1 packet
        # id = idpacket[0].sessionID
        # # TODO: Maybe these packets shouldn't be skipped but just the session number
        # # should be part of the data so that the researchers can delete it themselves.

        # if id != 0:
        #     subid = id
        #     while id == subid:
        #         packets = NVP.streamReadData(self._read_handle, self.SKIP_SIZE)
        #         subid = packets[0].sessionID
        # else:
        #     logging.error("Error: restart recording")
        #     NVP.streamClose(self._read_handle)

        while True:
            t1 = self._currentTime()

            packets = NVP.streamReadData(self._read_handle, self.BUFFER_SIZE)
            count = len(packets)

            if count < self.BUFFER_SIZE:
                logging.warning("Out of packets")
                break

            databuffer = np.asarray(
                [packets[i].data for i in range(self.BUFFER_SIZE)], dtype="uint16"
            ).T
            databuffer = databuffer.copy(order="C")
            UDPClientSocket.sendto(databuffer, serverAddressPort)

            t2 = self._currentTime()
            while (t2 - t1) < bufferInterval:
                t2 = self._currentTime()

        NVP.streamClose(self._read_handle)

    def control_rec_start(
        self,
        recording_time: Optional[int] = 1,
        store_NWB: bool = True,
    ) -> None:
        """
        Start the recording.

        :param infinite_rec: (Optional) Flag to determine if the recoding will continue
        indefinitely or until control_rec_stop is called.
        :param recording_time: (Optional) Time in seconds that a recording will take if
        there is a defined end time.
        :param store_NWB: (Optional) Flag to determine if data should stored as NWB.
        """

        if self._recording:
            logging.info(
                f"Already recording under the name: {self._recording_file_name}"
            )
            return None

        if store_NWB:
            threading.Thread(target=self.combine, args=(self._metadata_stream,)).start()

        NVP.setSWTrigger(self._handle)
        self._recording = True
        logging.info(f"Started recording: {self._recording_file_name}")
        threading.Thread(target=self.send_data_to_socket).start()
        if recording_time:
            time.sleep(recording_time)
            self.control_rec_stop()

    def control_rec_stop(self) -> None:
        """Stop the ongoing recording."""

        if not self._recording:
            logging.info("No recording in progress.")
            return

        NVP.arm(self._handle)
        NVP.setFileStream(self._handle, "")
        NVP.closeBS(self._handle)
        NVP.destroyHandle(self._handle)
        self._recording = False
        logging.info(f"Stopped recording: {self._recording_file_name}")
        self._recording_file_name = None

    def control_rec_status(self) -> bool:
        """
        Check the recording status.

        :return: True if currently recording, False otherwise.
        """

        return self._recording

    def __str__(self) -> str:
        """
        Return a string representation of the recording status and name.

        :return: Status of recording and name of the recording file.
        """

        status = "Recording" if self._recording else "Not Recording"
        return f"Status: {status}, Recording Name: {self._recording_file_name}"

    def control_send_parameters(
        self,
        stimunit: int = 0,
        polarity: int = 0,
        config_params: ConfigurationParameters = None,
    ) -> None:
        # Configure SU 0
        NVP.writeSUConfiguration(
            config_params.get_SUConfig_pars(
                self._handle, self._probe, stimunit, polarity
            )
        )
        # enable all OSes and connects them to SU 0
        NVP.setOSimage(self._handle, self._probe, bytes(128 * [8]))
        NVP.writeOSConfiguration(self._handle, self._probe, False)

    def stimulation_trigger(self, start_recording: bool = True) -> None:
        if self._recording is False and start_recording is True:
            self.control_rec_start(recording_time=None)
        NVP.SUtrig1(self._handle, self._probe, bytes([8]))


if __name__ == "__main__":
    # Example usage:
    controller = ViperBoxControl("test", 0)
    # pulse_shape = PulseShapeParameters()
    # pulse_train = PulseTrainParameters()
    # electrodes = [1, 2, 3]
    # viperbox = ViperBoxConfiguration(0)
    # config = ConfigurationParameters(pulse_shape, pulse_train, electrodes, viperbox)

    # print(config.get_SUConfig_pars())

    # controller.control_send_parameters()
    # controller.control_rec_setup(
    #     file_name="exp1.bin",
    #     file_location="./",
    #     probe=0,
    #     reference_electrode=2,
    #     emulated=True,
    # )
    # controller.control_rec_start()
    # print(controller)
    # controller.control_rec_stop()
    # print(controller)
