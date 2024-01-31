from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class Connect:
    probe_list: List[int] = [1, 2, 3, 4]
    emulation: bool = False
    boxless: bool = False


@dataclass
class apiRecSettings:
    recording_XML: str = ""
    reset: bool = False
    default_values: bool = False


@dataclass
class apiStimSettings:
    stimulation_XML: str = ""
    reset: bool = False
    default_values: bool = False


@dataclass
class apiStartRec:
    recording_name: str = ""


@dataclass
class apiStartStim:
    SU_bit_mask: str = ""


@dataclass
class apiTTLStart:
    TTL_channel: int = 0
    TTL_XML: str = ""
    SU_bit_mask: str = ""


@dataclass
class apiVerifyXML:
    XML: str = ""
