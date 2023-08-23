import NeuraviperPy as NVP
import threading
import time
import numpy as np
import socket

class ViperBoxControl:
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

    def control_rec_setup(self, file_name:str, file_location:str, probe:int, 
                          reference_electrode:int, electrode_mapping:bytes = None, 
                          metadata_stream:list = None, emulated:bool=False) -> bool:
        if not (0 <= probe <= 3): # throw a error
            print("Invalid probe value.")
        if not (0 <= reference_electrode <= 8): # throw a error
            print("Invalid reference electrode value.")

        self._metadata_stream = metadata_stream
        self._handle = NVP.createHandle(0)
        NVP.openBS(self._handle)
        
        if emulated:
            NVP.setDeviceEmulatorMode(self._handle, NVP.DeviceEmulatorMode.LINEAR)
            NVP.setDeviceEmulatorType(self._handle, NVP.DeviceEmulatorType.EMULATED_PROBE)

        NVP.openProbes(self._handle)
        NVP.init(self._handle, probe)
        
        self._recording_file_name = file_name
        self._recording_file_location = file_location
        NVP.setFileStream(self._handle, self._recording_path)
        NVP.enableFileStream(self._handle, True)
        
        NVP.arm(self._handle)
        
        # if electrode_mapping:
        #     for channel, electrode in enumerate(electrode_mapping):
        #         NVP.selectElectrode(self._handle, probe, channel, electrode)

        # NVP.setReference(self._handle, probe, 0, reference_electrode)
        # NVP.writeChannelConfiguration(self._handle, probe)

        return True

    def combine(self, metadata_stream):
        # Do something with metadata_stream
        pass

    def send_data_to_socket(self):
        bufferSize = 500
        skipsize = 20
        Freq = 20000
        buffersPerSecond = Freq / bufferSize
        bufferInterval = 1 / buffersPerSecond

        serverAddressPort = ("127.0.0.1", 9001)
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        def currentTime():
            return time.time_ns() / (10 ** 9)

        # read_handle = NVP.streamOpenFile(self._recording_file_location, self.probe)
        read_handle = NVP.streamOpenFile("exp1.bin", self._probe)
        
        
        # reads one packet to get session id of last fifo, then skip all packets with that session id.
        idpacket = NVP.streamReadData(read_handle, 1) # 1 packet
        id = idpacket[0].sessionID
        if id != 3:
            print("id: ", id)
            subid = id
            while (id == subid):
                packets = NVP.streamReadData(read_handle, skipsize)
                subid = packets[0].sessionID
                print("subid: ", subid)
        else:
            print('Error: restart recording')
            # NVP.streamClose(read_handle)
        
        while True:            
            t1 = currentTime()
            
            packets = NVP.streamReadData(read_handle, bufferSize)
            count = len(packets)            

            if count < bufferSize:
                print("out of packets")
                break

            databuffer = np.asarray([packets[i].data for i in range(bufferSize)],dtype='uint16').T
            databuffer = databuffer.copy(order='C')
            UDPClientSocket.sendto(databuffer, serverAddressPort)

            t2 = currentTime()
            while ((t2 - t1) < bufferInterval):
                t2 = currentTime()
        
        NVP.streamClose(read_handle)

    def control_rec_start(self, sleep_time:int=2, store_NWB:bool = True):
        if self._recording:
            print(f"Already recording under the name: {self._recording_file_name}")
            return
        
        if store_NWB:
            threading.Thread(target=self.combine, args=(self._metadata_stream,)).start()

        NVP.setSWTrigger(self._handle)
        # self.send_data_to_socket()
        time.sleep(sleep_time)
        self._recording = True
        print(f"Started recording: {self._recording_file_name}")

    def control_rec_stop(self):
        if not self._recording:
            print("No recording in progress.")
            return

        NVP.arm(self._handle)
        NVP.setFileStream(self._handle, "")
        NVP.closeBS(self._handle)
        NVP.destroyHandle(self._handle)
        self._recording = False
        print(f"Stopped recording: {self._recording_file_name}")
        self._recording_file_name = None

    def control_rec_status(self):
        return self._recording

    def __str__(self):
        status = "Recording" if self._recording else "Not Recording"
        return f"Status: {status}, Recording Name: {self._recording_file_name}"

# Example usage:
controller = ViperBoxControl()
# controller.control_rec_setup(file_name="exp1.bin", file_location="./", probe=0, reference_electrode=2, emulated=True)
# controller.control_rec_start()
# print(controller)
# controller.control_rec_stop()
controller.send_data_to_socket()
print(controller)
