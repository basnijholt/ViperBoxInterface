# from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

# handle contains 4 probes
# each probe contains 64 channels, 8 SU's and 128 electrodes
# recording goes through the 64 channels
# stimulation goes through the 8 SU's


@dataclass
class Connect(BaseModel):
    probe_list: None | List[int] = None
    emulation: bool = False
    boxless: bool = False


@dataclass
class ChannelSettings(BaseModel):
    channel: int | None = None
    references: str | None = None
    gain: int | None = None
    input: int | None = None


@dataclass
class ProbeRecordingSettings(BaseModel):
    # The int in the Dict is the channel number
    probe: int | None = None
    channel_sett: Dict[int, ChannelSettings] | None = None

    def get_gains(self):
        np.zeros(64)
        return self.gain_vec


@dataclass
class StimulationUnitSettings(BaseModel):
    stim_unit: int | None = None
    polarity: bool | None = None
    pulses: int | None = None
    prephase: int | None = None
    amplitude1: int | None = None
    width1: int | None = None
    interphase: int | None = None
    amplitude2: int | None = None
    width2: int | None = None
    discharge: int | None = None
    duration: int | None = None
    aftertrain: int | None = None

    def SUConfig(self):
        return (
            self.stim_unit,
            self.polarity,
            self.pulses,
            self.amplitude1,
            self.amplitude2,
            self.duration,
            self.prephase,
            self.width1,
            self.interphase,
            self.width2,
            self.discharge,
            self.aftertrain,
        )


@dataclass
class ElectrodeSet(BaseModel):
    # electrodes can only occur once in any of the dicts.
    stim_elec: Dict[int, List[int]] | None = None
    stim_elec_map: bytes | None = None


@dataclass
# see test_elecset.py and testarea.ipynb
class ElectrodeSet2(BaseModel):
    stim_elec: Dict[int, List[int]] | None = None
    _os_data: bytes | None = None
    sus: int = 6
    elecs: int = 12

    def __post_init__(self):
        os_data_array = np.zeros((self.sus, self.elecs))
        for su, elec_list in self.stim_elec.items():
            for elec in elec_list:
                os_data_array[su, elec] = 1
        print(os_data_array)

        # get sum over second axis of os_data_array


# # The other classes remain unchanged
# @dataclass
# class ProbeStimulationSettings(BaseModel):
#     probe: int | None = None
#     stim_unit_sett: Dict[int, StimulationUnitSettings] | None = None
#     stim_elec: Dict[int, List[int]] | None = None
#     stim_elec_map: bytes | None = None
#     # stim_unit_electrodes: Dict[int, ElectrodeSet] | None = None


@dataclass
class ProbeStimulationSettings(BaseModel):
    # The int in the Dict is the stimulation unit number
    probe: int | None = None
    stim_unit_sett: Dict[int, StimulationUnitSettings] | None = None
    stim_unit_electrodes: Dict[int, ElectrodeSet] | None = None

    def SUs_connected(self):
        # return binary string of SU's that have uploaded settings
        pass


@dataclass
class HandleSettings(BaseModel):
    # The int in the Dict is the probe number
    handle: str | None = None
    probes_rec: Dict[int, ProbeRecordingSettings] | None = None
    probes_stim: Dict[int, ProbeStimulationSettings] | None = None


@dataclass
class TTLSettings(BaseModel):
    TTL_channel: int | None = None
    probes: int | None = None
    stim_unit_sett: StimulationUnitSettings | None = None
    electrode_selection: ElectrodeSet | None = None


@dataclass
class GeneralSettings(BaseModel):
    viperbox_software_id: str | None = None
    session_starting_datetime: str | None = None
    api_version: str | None = None
    basestation_id: str | None = None
    boot_code_version: str | None = None
    head_stage_id: str | None = None
    mezzanine_id_1: str | None = None
    mezzanine_id_2: str | None = None
    mezzanine_id_3: str | None = None
    mezzanine_id_4: str | None = None
    probe_id_1: str | None = None
    probe_id_2: str | None = None
    probe_id_3: str | None = None
    probe_id_4: str | None = None
    handle_sett: HandleSettings | None = None


# from dataclasses import dataclass
# from typing import Dict, List

# @dataclass
# class ElectrodeSet(BaseModel):
#     stim_elec: Dict[int, List[int]] | None = None
#     _os_data: bytes | None = None

#     def __post_init__(self):
#         if self.stim_elec is not None:
#             self.update_os_data()

#     def update_stim_elec(self, new_stim_elec: Dict[int, List[int]]):
#         self.stim_elec = new_stim_elec
#         self.update_os_data()

#     def update_os_data(self):
#         # Create a list of 128 elements, each set to 0
#         electrode_data = [0] * 128

#         # Update the list based on the stim_elec dictionary
#         for unit, electrodes in self.stim_elec.items():
#             for electrode in electrodes:
#                 electrode_data[electrode] = unit

#         # Convert to 4-bit representations and pack into bytes
#         bytes_list = []
#         for i in range(0, 128, 2):
#             # Combine two 4-bit numbers into one byte
#             byte = (electrode_data[i] << 4) | electrode_data[i+1]
#             bytes_list.append(byte)

#         self._os_data = bytes(bytes_list)

# # Example usage
# es = ElectrodeSet({0: [0, 1], 1: [2, 3]})
# print(es._os_data)  # This will print the bytes object

# # Updating stim_elec
# es.update_stim_elec({2: [4, 5], 3: [6, 7]})
# print(es._os_data)  # Updated bytes object
