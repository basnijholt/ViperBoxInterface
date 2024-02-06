import json
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, List

import numpy as np
from lxml import etree

# handle contains 4 probes
# each probe contains 64 channels, 8 SU's and 128 electrodes
# recording goes through the 64 channels
# stimulation goes through the 8 SU's

# Stack overflow nested data classes https://stackoverflow.com/questions/51564841/creating-nested-dataclass-objects-in-python


@dataclass
class StatusTracking:
    recording: bool = False
    recording_settings_uploaded: bool = False
    stimulation_settings_uploaded: bool = False
    test_mode: bool = False
    BIST_number: int | None = None
    box_connected: bool = False
    probe_connected: bool = False
    active_TTLs: List[bool] = field(default_factory=list)
    _SU_busy = "0" * 16


@dataclass
class ChanSettings:
    references: str = "100000000"
    gain: int = 0
    input: int = 0

    @property
    def get_refs(self):
        return int(int(self.references, 2))

    @classmethod
    def from_dict(cls, env):
        tmp_dct = {}
        for k, v in cls.__annotations__.items():
            if not isinstance(env[k], v):
                tmp_dct[k] = int(env[k])
            else:
                tmp_dct[k] = str(env[k])
        return cls(**tmp_dct)


@dataclass
class SUSettings:
    # stim_unit: int = 0
    polarity: bool = False
    pulses: int = 20
    prephase: int = 0
    amplitude1: int = 1
    width1: int = 170
    interphase: int = 60
    amplitude2: int = 1
    width2: int = 170
    discharge: int = 200
    duration: int = 600
    aftertrain: int = 0

    @classmethod
    def from_dict(cls, env):
        tmp_dct = {}
        for k, v in cls.__annotations__.items():
            if not isinstance(env[k], v):
                tmp_dct[k] = int(env[k])
            # if not isinstance(env[k], v):
            else:
                tmp_dct[k] = str(env[k])
            # else:
            #     tmp_dct[k] = bool(env[k])
        return cls(**tmp_dct)

    def SUConfig(self):
        return (
            # self.stim_unit,
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


# @dataclass
# class ProbeSettings:
#     channel_sett: Dict[str, ChanSettings] = field(
#         default_factory=dict(str, ChanSettings)
#     )
#     stim_unit_sett: Dict[str, SUSettings] = field(default_factory=dict())
#     stim_unit_elec: Dict[str, List[int]] = field(default_factory=dict())
#     _sus: int = 8
#     _elecs: int = 128


@dataclass
class ProbeSettings:
    channel: Dict[str, ChanSettings] = field(default_factory=dict)
    stim_unit_sett: Dict[str, SUSettings] = field(default_factory=dict)
    stim_unit_elec: Dict[str, List[int]] = field(default_factory=dict)
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
    TTL_probes: Dict[int, TTLSettings] = field(default_factory=dict)


@dataclass
class TTL_handels:
    TTL_handels: Dict[int, TTLSettings] = field(default_factory=dict)


# @dataclass
# class HandleSettings:
#     handle: str = ""
#     hardware_id_base_station: IDInformation = field(default_factory=IDInformation)
#     hardware_id_head_stage: IDInformation = field(default_factory=IDInformation)
#     probes: Dict[int, ProbeSettings] = field(default_factory=dict())


@dataclass
class HandleSettings:
    handle_id: str = ""
    hardware_id_base_station: IDInformation | None = None
    hardware_id_head_stage: IDInformation | None = None
    probes: Dict[int, ProbeSettings] = field(default_factory=dict)


@dataclass
class GeneralSettings:
    viperbox_software_id: str = ""
    session_starting_datetime: str = ""
    api_version_minor: str = ""
    api_version_major: str = ""
    # handle_sett: HandleSettings = field(default_factory=HandleSettings)
    handles: Dict[int, HandleSettings] = field(default_factory=dict)
    # connected: Dict[int, List[int]] = field(default_factory=dict)

    @property
    def connected(self):
        connected_hp = {}
        if self.handles:
            handle_list = list(self.handles.keys())
            for handle in handle_list:
                if self.handles[handle].probes:
                    connected_hp[handle] = list(self.handles[handle].probes.keys())
            return connected_hp
        else:
            return connected_hp

    def reset_recording_settings(self):
        connected_hp = self.connected
        for handle, probes in connected_hp.items():
            for probe in probes:
                self.handles[handle].probes[probe].channel = {}

    def reset_stimulation_settings(self):
        connected_hp = self.connected
        for handle, probes in connected_hp.items():
            for probe in probes:
                self.handles[handle].probes[probe].stim_unit_sett = {}
                self.handles[handle].probes[probe].stim_unit_elec = {}

    def reset_probe_settings(self):
        connected_hp = self.connected
        for handle, probes in connected_hp.items():
            for probe in probes:
                self.handles[handle].probes[probe].channel = {}
                self.handles[handle].probes[probe].stim_unit_sett = {}
                self.handles[handle].probes[probe].stim_unit_elec = {}


def printable_dtd(obj: Any) -> None:
    """
    Recursively convert dataclass instances to dictionaries.
    """

    print(json.dumps(dataclass_to_dict(obj), indent=4, sort_keys=True))


def readable_dtd(obj: Any) -> None:
    """
    Recursively convert dataclass instances to dictionaries.
    """

    return json.dumps(dataclass_to_dict(obj), indent=4, sort_keys=True)


def printet(obj: Any) -> None:
    """
    Readable print of an ET object.
    """
    print(etree.tostring(obj, pretty_print=True).decode())


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


def parse_numbers(numstr: str, all_values: list[int]):
    """Parse a string of numbers into a numpy array of integers. These are inputs like:
    '1,2,3,4-6,8' or '-' for all possible values.

    Arguments:
    - numstr {str} -- string of numbers to parse
    - all_values {list[int]} -- list of all possible values for the numbers

    Returns:
    - result {numpy.ndarray} -- numpy array of parsed integers

    Test cases:
    - wrong ranges: '1-2-3', '1-', '1,,2', '1--2', '-1'
    might be more.
    """

    if ",," in numstr:
        raise ValueError("Invalid input, can't put double commas")
    if "--" in numstr:
        raise ValueError("Invalid input, can't put double dashes")
    result = np.array([], dtype=int)
    if numstr == "-":
        if all_values is None:
            raise ValueError("all_values not known")
        result = np.asarray(all_values)
    elif len(numstr) == 1:
        result = np.array([int(numstr)])
    else:
        split_numstr = numstr.split(",")
        for item in split_numstr:
            if item[0] == "-":
                raise ValueError("Invalid input, can't start with a dash")
            if item[-1] == "-":
                raise ValueError("Invalid input, can't end with a dash")
            if "-" in item:
                split_item = item.split("-")
                # check if the range is valid
                if len(split_item) != 2:
                    raise ValueError("Invalid range")
                elif int(split_item[0]) > int(split_item[1]):
                    np_item = np.asarray(
                        range(int(split_item[1]), int(split_item[0]) + 1)
                    )
                else:
                    np_item = np.asarray(
                        range(int(split_item[0]), int(split_item[1]) + 1)
                    )
            else:
                np_item = np.asarray(int(item))
            result = np.append(result, np_item)
        result = np.unique(result)
    if not set(result).issubset(set(all_values)):
        raise ValueError(
            "Invalid values; following are not connected"
            ":{set(result) - set(all_values)}."
        )
    return result.tolist()


def get_handles(settings):
    """Get the handles of all settings in the settings dictionary

    Arguments:
    - settings {dict} -- dictionary of settings

    Returns:
    - handles {list} -- list of handles
    """
    handles = [int(i) for i in settings["handles"].keys()]
    if not handles:
        raise ValueError("No handles found in settings")
    return handles


def get_probes(handle: int, settings):
    """Get the probes of a handle

    Arguments:
    - handle {int} -- handle of the setting
    - settings {dict} -- dictionary of settings

    Returns:
    - probes {list} -- list of probes
    """
    probes = [int(i) for i in settings["handles"][str(handle)]["probes"].keys()]
    if not probes:
        raise ValueError(f"No probes found in handle {handle}")
    return probes


def __check_handles_exist(data, existing_handles):
    """Check if xml handles are in existing handles. If not, throw ValueError, else pass

    Arguments:
    - data: xml data of type lxml.etree._ElementTree
    - existing_handles: list of existing handles
    TODO: existing handles should be changed to something that comes from the local
    settings.

    test cases:
    - xml handle is not in existing handles

    """
    for element in data.xpath(".//*[@handle]"):
        setting_handles = element.attrib["handle"]
        _ = parse_numbers(setting_handles, existing_handles)
    return True
