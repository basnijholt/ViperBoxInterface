from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Dict, List

import numpy as np

# from pydantic import# from pydantic.dataclasses import dataclass


# handle contains 4 probes
# each probe contains 64 channels, 8 SU's and 128 electrodes
# recording goes through the 64 channels
# stimulation goes through the 8 SU's
def dataclass_to_dict(obj: Any) -> Any:
    """
    Recursively convert dataclass instances to dictionaries.
    """
    if is_dataclass(obj):
        return {k: dataclass_to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, tuple):
        return tuple(dataclass_to_dict(item) for item in obj)
    else:
        return obj


def dict_to_dataclass(cls: Any, dict_obj: Any) -> Any:
    """
    Recursively convert dictionaries to dataclass instances.
    """
    if hasattr(cls, "__annotations__"):
        field_types = cls.__annotations__
        return cls(
            **{
                k: dict_to_dataclass(field_types[k], v)
                for k, v in dict_obj.items()
                if k in field_types
            }
        )
    else:
        return dict_obj


@dataclass
class ChanSettings:
    references: str | None = "100000000"
    gain: int | None = 0
    input: int | None = 0


@dataclass
class SUSettings:
    polarity: str | None = None
    pulses: int | None = None
    prephase: int | None = None


@dataclass
class ProbeRecordingSettings:
    channel_sett: Dict[str, ChanSettings] | None = None

    # def get_gains(self):
    #     np.zeros(64)
    #     return self.gain_vec


@dataclass
class ProbeStimulationSettings:
    stim_unit_sett: Dict[str, SUSettings] | None = None
    stim_unit_elec: Dict[str, List[int]] | None = None
    _sus: int = 8
    _elecs: int = 128

    def SUs_connected(self):
        # return binary string of SU's that have uploaded settings
        pass

    @property
    def os_data(self):
        os_data_array = np.zeros((self._sus, self._elecs))
        if self.stim_unit_elec:
            for su, elec_list in self.stim_unit_elec.items():
                for elec in elec_list:
                    os_data_array[su, elec] = 1
            return os_data_array
        # get sum over second axis of os_data_array


@dataclass
class HandleSettings:
    probes_rec: Dict[str, ProbeRecordingSettings] | None = None
    probes_stim: Dict[str, ProbeStimulationSettings] | None = None


@dataclass
class Connect:
    probe_list: None | List[int] = None
    emulation: bool = False
    boxless: bool = False


@dataclass
class SUSettings:
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
class TTLSettings:
    TTL_channel: int | None = None
    electrode_selection: HandleSettings | None = None
    TTL_trigger_function: str | None = None


@dataclass
class GeneralSettings:
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


# ########################################################333


# @dataclass
# # see test_elecset.py and testarea.ipynb
# class ElectrodeSet:
#     stim_elec: Dict[int, List[int]] | None = None
#     _os_data: bytes | None = None
#     sus: int = 8
#     elecs: int = 128

#     def __post_init__(self):
#         os_data_array = np.zeros((self.sus, self.elecs))
#         for su, elec_list in self.stim_elec.items():
#             for elec in elec_list:
#                 os_data_array[su, elec] = 1
#         print(os_data_array)

#         # get sum over second axis of os_data_array

# # The other classes remain unchanged
# @dataclass
# class ProbeStimulationSettings:
#     probe: int | None = None
#     stim_unit_sett: Dict[int, StimulationUnitSettings] | None = None
#     stim_elec: Dict[int, List[int]] | None = None
#     stim_elec_map: bytes | None = None
#     # stim_unit_electrodes: Dict[int, ElectrodeSet] | None = None


# @dataclass
# class ProbeStimulationSettings:
#     # The int in the Dict is the stimulation unit number
#     probe: int | None = None
#     stim_unit_sett: Dict[int, StimulationUnitSettings] | None = None
#     stim_unit_electrodes: Dict[int, ElectrodeSet] | None = None

#     def SUs_connected(self):
#         # return binary string of SU's that have uploaded settings
#         pass


# @dataclass
# class HandleSettings:
#     # The int in the Dict is the probe number
#     handle: str | None = None
#     probes_rec: Dict[int, ProbeRecordingSettings] | None = None
#     probes_stim: Dict[int, ProbeStimulationSettings] | None = None


# from dataclasses import dataclass
# from typing import Dict, List

# @dataclass
# class ElectrodeSet:
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
