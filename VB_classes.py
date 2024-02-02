import inspect
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, List

import numpy as np

# handle contains 4 probes
# each probe contains 64 channels, 8 SU's and 128 electrodes
# recording goes through the 64 channels
# stimulation goes through the 8 SU's


@dataclass
class ChanSettings:
    references: str = ""
    gain: int = 0
    input: int = 0

    @classmethod
    def from_dict(cls, env):
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )


@dataclass
class SUSettings:
    stim_unit: int = 0
    polarity: bool = False
    pulses: int = 0
    prephase: int = 0
    amplitude1: int = 0
    width1: int = 0
    interphase: int = 0
    amplitude2: int = 0
    width2: int = 0
    discharge: int = 0
    duration: int = 0
    aftertrain: int = 0

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
class ProbeSettings:
    channel_sett: Dict[str, ChanSettings] = field(
        default_factory=dict(str, ChanSettings)
    )
    stim_unit_sett: Dict[str, SUSettings] = field(default_factory=dict(str, SUSettings))
    stim_unit_elec: Dict[str, List[int]] = field(default_factory=dict(str, list[int]))
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

    # def get_gains(self):
    #     np.zeros(64)
    #     return self.gain_vec


class IDInformation:
    serial_number: int = 0
    version_major: int = 0
    version_minor: int = 0
    headstage_id: str = ""


@dataclass
class TTLSettings:
    trigger_function: str = ""
    target_handle: str = ""
    target_probe: str = ""
    target_SU: str = ""


@dataclass
class TTL_probes:
    TTL_probes: Dict[int, TTLSettings] = field(default_factory=dict(int, TTLSettings))


@dataclass
class TTL_handels:
    TTL_handels: Dict[int, TTLSettings] = field(default_factory=dict(int, TTLSettings))


@dataclass
class HandleSettings:
    handle: str = ""
    hardware_id_base_station: IDInformation = field(default_factory=IDInformation)
    hardware_id_head_stage: IDInformation = field(default_factory=IDInformation)
    probes: Dict[int, ProbeSettings] = field(default_factory=dict(int, ProbeSettings))


@dataclass
class GeneralSettings:
    viperbox_software_id: str = ""
    session_starting_datetime: str = ""
    api_version_minor: str = ""
    api_version_major: str = ""
    handle_sett: HandleSettings = field(default_factory=HandleSettings)


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

    Arguments:
    - cls: The given dataclass type to convert to.
    - dict_obj: The dictionary to convert.
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
