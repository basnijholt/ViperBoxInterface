from time import strftime
from uuid import uuid4

import numpy as np
from hdmf.data_utils import DataChunkIterator
from pynwb import NWBHDF5IO, NWBFile, TimeSeries

import NeuraviperPy as NVP

# import os

# os.add_dll_directory("PATH_TO_DLL")

BUFFER_SIZE = 500
SKIP_SIZE = 20
FREQ = 20000


def write_test_file(filename, data, close_io=True):
    """

    Simple helper function to write an NWBFile with a single timeseries containing data
    :param filename: String with the name of the output file
    :param data: The data of the timeseries
    :param close_io: Close and destroy the NWBHDF5IO object used for writing
    (default=True)

    :returns: None if close_io==True otherwise return NWBHDF5IO object used for write
    """

    # Create a test NWBfile
    start_time = strftime("%Y-%m-%d_%H-%M-%S")
    nwbfile = NWBFile(
        session_description="demonstrate continuous write",
        identifier=str(uuid4()),
        session_start_time=start_time,
    )

    # Create our time series
    test_ts = TimeSeries(
        name="viperbox_emulated_data",
        data=data,
        unit="n/a",
        rate=1.0,
    )
    nwbfile.add_acquisition(test_ts)

    # Write the data to file
    io = NWBHDF5IO(filename, "w")
    io.write(nwbfile)
    if close_io:
        io.close()
        del io
        io = None
    return io


def iter_data(probe=0, recording_path="./exp1.bin") -> None:
    handle = NVP.streamOpenFile(recording_path, probe)

    while True:
        packets = NVP.streamReadData(handle, BUFFER_SIZE)
        count = len(packets)

        if count < BUFFER_SIZE:
            break

        databuffer = np.asarray(
            [packets[i].data for i in range(BUFFER_SIZE)], dtype="uint16"
        ).T
        databuffer = databuffer.copy(order="C")
        yield databuffer

    NVP.streamClose(handle)


data = DataChunkIterator(data=iter_data())

write_test_file(filename="basic_iterwrite_example.nwb", data=data)

print(
    "maxshape=%s, recommended_data_shape=%s, dtype=%s"
    % (str(data.maxshape), str(data.recommended_data_shape()), str(data.dtype))
)
