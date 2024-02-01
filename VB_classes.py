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
        default_factory=Dict[str, ChanSettings]
    )
    stim_unit_sett: Dict[str, SUSettings] = field(default_factory=Dict[str, SUSettings])
    stim_unit_elec: Dict[str, List[int]] = field(default_factory=Dict[str, List[int]])
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


@dataclass
class HandleSettings:
    handle: str = ""
    all_probes: Dict[str, ProbeSettings] = field(
        default_factory=Dict[str, ProbeSettings]
    )


@dataclass
class TTLSettings:
    TTL_channel: int = 0
    electrode_selection: HandleSettings = field(default_factory=HandleSettings)
    TTL_trigger_function: str = ""


@dataclass
class GeneralSettings:
    viperbox_software_id: str = ""
    session_starting_datetime: str = ""
    api_version: str = ""
    basestation_id: str = ""
    boot_code_version: str = ""
    head_stage_id: str = ""
    mezzanine_id_1: str = ""
    mezzanine_id_2: str = ""
    mezzanine_id_3: str = ""
    mezzanine_id_4: str = ""
    probe_id_1: str = ""
    probe_id_2: str = ""
    probe_id_3: str = ""
    probe_id_4: str = ""
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
