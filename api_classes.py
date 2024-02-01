import xml.etree.ElementTree as ET
from typing import List

from pydantic import BaseModel, field_validator
from pydantic.dataclasses import dataclass


@dataclass
class Connect(BaseModel):
    probe_list: List[int] = [1, 0, 0, 0]
    emulation: bool = False
    boxless: bool = False

    @field_validator("probe_list")
    @classmethod
    def check_probe_list(cls, probe_list: List[int]) -> List[int]:
        if len(probe_list) != 4:
            raise ValueError("probe_list must contain exactly 4 integers")
        for i in probe_list:
            if i not in [0, 1]:
                raise ValueError("probe_list can only contain 0 or 1")
        return probe_list


@dataclass
class apiRecSettings(BaseModel):
    recording_XML: str = ""
    reset: bool = False
    default_values: bool = False

    @field_validator("recording_XML")
    @classmethod
    def check_xml(cls, recording_XML: str) -> str:
        try:
            ET.fromstring(recording_XML)
        except ET.ParseError as e:
            raise ValueError(f"recording_XML is not valid XML. Error: {e}") from e
        return recording_XML


@dataclass
class apiStimSettings(BaseModel):
    stimulation_XML: str = ""
    reset: bool = False
    default_values: bool = False

    @field_validator("stimulation_XML")
    @classmethod
    def check_xml(cls, stimulation_XML: str) -> str:
        try:
            ET.fromstring(stimulation_XML)
        except ET.ParseError as e:
            raise ValueError(f"recording_XML is not valid XML. Error: {e}") from e
        return stimulation_XML


@dataclass
class apiStartRec(BaseModel):
    recording_name: str = ""

    @field_validator("recording_name")
    @classmethod
    def check_unicode(cls, recording_name: str) -> str:
        try:
            recording_name.encode("ascii")
        except UnicodeEncodeError as e:
            raise ValueError(f"recording_name must be utf-8. Error: {e}") from e
        return recording_name


@dataclass
class apiStartStim(BaseModel):
    SU_bit_mask: list = []

    @field_validator("SU_bit_mask")
    @classmethod
    def check_SU_bit_mask(cls, SU_bit_mask: List[int]) -> List[int]:
        if len(SU_bit_mask) != 8:
            raise ValueError("SU_bit_mask must contain exactly 8 integers")
        for i in SU_bit_mask:
            if i not in [0, 1]:
                raise ValueError("SU_bit_mask can only contain 0 or 1")
        return SU_bit_mask


@dataclass
class apiTTLStart(BaseModel):
    TTL_channel: int = 0
    TTL_XML: str = ""
    SU_bit_mask: list = []

    @field_validator("TTL_channel")
    @classmethod
    def check_TTL_channel(cls, TTL_channel: int) -> int:
        if TTL_channel not in [0, 1]:
            raise ValueError("TTL_channel must be 1 or 2")
        return TTL_channel

    @field_validator("TTL_XML")
    @classmethod
    def check_xml(cls, TTL_XML: str) -> str:
        try:
            ET.fromstring(TTL_XML)
        except ET.ParseError as e:
            raise ValueError(f"TTL_XML is not valid XML. Error: {e}") from e
        return TTL_XML

    @field_validator("SU_bit_mask")
    @classmethod
    def check_SU_bit_mask(cls, SU_bit_mask: List[int]) -> List[int]:
        if len(SU_bit_mask) != 8:
            raise ValueError("SU_bit_mask must contain exactly 8 integers")
        for i in SU_bit_mask:
            if i not in [0, 1]:
                raise ValueError("SU_bit_mask can only contain 0 or 1")
        return SU_bit_mask


@dataclass
class apiVerifyXML(BaseModel):
    XML: str = ""

    @field_validator("XML")
    @classmethod
    def check_xml(cls, verify_XML: str) -> str:
        try:
            ET.fromstring(verify_XML)
        except ET.ParseError as e:
            raise ValueError(f"verify_XML is not valid XML. Error: {e}") from e
        return verify_XML
