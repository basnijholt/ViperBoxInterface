import NeuraviperPy as NVP
import threading
import time
import numpy as np
import socket
import logging

logging.basicConfig(level=logging.INFO)


class ViperBoxControl:
    BUFFER_SIZE = 500
    SKIP_SIZE = 20
    FREQ = 20000

    def __init__(self):
        self._recording = False
        self._recording_file_name = None
        self._recording_file_location = None
        self._metadata_stream = None
        self._handle = None
        self._probe = 0

    @property
    def _recording_path(self):
        if self._recording_file_name and self._recording_file_location:
            return self._recording_file_location + self._recording_file_name
        return None

    @staticmethod
    def _currentTime():
        return time.time_ns() / (10**9)

    def control_rec_setup(
        self,
        file_name: str,
        file_location: str,
        probe: int,
        reference_electrode: int,
        electrode_mapping: bytes = None,
        metadata_stream: list = None,
        emulated: bool = False,
    ) -> bool:
        if not (0 <= probe <= 3):
            raise ValueError(
                "Error: Invalid probe value. Expected a value between 0 and 3."
            )
        if not (0 <= reference_electrode <= 8):
            raise ValueError(
                "Error: Invalid reference electrode value. Expected a value between 0 and 8."
            )

        self._metadata_stream = metadata_stream

        try:
            self._handle = NVP.createHandle(0)
            NVP.openBS(self._handle)
        except Exception as e:
            logging.error(f"Error while setting up handle: {e}")
            return False

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
        # if electrode_mapping:
        #     for channel, electrode in enumerate(electrode_mapping):
        #         NVP.selectElectrode(self._handle, probe, channel, electrode)

        # NVP.setReference(self._handle, probe, 0, reference_electrode)
        # NVP.writeChannelConfiguration(self._handle, probe)

        return True

    def combine(self, metadata_stream):
        # Placeholder for metadata stream processing
        pass

    def send_data_to_socket(self):
        bufferInterval = self.BUFFER_SIZE / self.FREQ

        serverAddressPort = ("127.0.0.1", 9001)
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        read_handle = NVP.streamOpenFile("exp1.bin", self._probe)

        # reads one packet to get session id of last fifo, then skip all packets with that session id.
        idpacket = NVP.streamReadData(read_handle, 1)  # 1 packet
        id = idpacket[0].sessionID
        if id != 3:
            # print("id: ", id)
            subid = id
            while id == subid:
                packets = NVP.streamReadData(read_handle, self.SKIP_SIZE)
                subid = packets[0].sessionID
                # print("subid: ", subid)
        else:
            logging.error("Error: restart recording")
            # NVP.streamClose(read_handle)

        while True:
            t1 = self._currentTime()

            packets = NVP.streamReadData(read_handle, self.BUFFER_SIZE)
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

        NVP.streamClose(read_handle)

    def control_rec_start(self, sleep_time: int = 2, store_NWB: bool = True):
        if self._recording:
            logging.info(
                f"Already recording under the name: {self._recording_file_name}"
            )
            return

        if store_NWB:
            threading.Thread(target=self.combine, args=(self._metadata_stream,)).start()

        NVP.setSWTrigger(self._handle)
        self._recording = True
        logging.info(f"Started recording: {self._recording_file_name}")
        threading.Thread(target=self.send_data_to_socket).start()
        time.sleep(sleep_time)
        print("slept enough")
        self.control_rec_stop()

    def control_rec_stop(self):
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
        return self._recording

    def __str__(self) -> str:
        status = "Recording" if self._recording else "Not Recording"
        return f"Status: {status}, Recording Name: {self._recording_file_name}"


# Example usage:
controller = ViperBoxControl()
controller.control_rec_setup(
    file_name="exp1.bin",
    file_location="./",
    probe=0,
    reference_electrode=2,
    emulated=True,
)
controller.control_rec_start()
print(controller)
controller.control_rec_stop()
print(controller)
