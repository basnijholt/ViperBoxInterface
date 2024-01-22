from dataclasses import dataclass
from typing import Dict

# handle contains 4 probes
# each probe contains 64 channels, 8 SU's and 128 electrodes
# recording goes through the 64 channels
# stimulation goes through the 8 SU's


@dataclass
class GeneralSettings:
    viperbox_software_id: str = None
    session_starting_datetime: str = None
    api_version: str = None
    basestation_id: str = None
    boot_code_version: str = None
    head_stage_id: str = None
    mezzanine_id_1: str = None
    mezzanine_id_2: str = None
    mezzanine_id_3: str = None
    mezzanine_id_4: str = None
    probe_id_1: str = None
    probe_id_2: str = None
    probe_id_3: str = None
    probe_id_4: str = None


@dataclass
class StimulationUnitSettings:
    stimulation_unit: int = None
    polarity: bool = None
    pulses: int = None
    prephase: int = None
    amplitude1: int = None
    width1: int = None
    interphase: int = None
    amplitude2: int = None
    width2: int = None
    discharge: int = None
    duration: int = None
    aftertrain: int = None


@dataclass
class ElectrodeSet:
    stimulation_unit: int = None
    electrode_set: list = None


@dataclass
class ChannelSettings:
    channel: int = None
    body_reference: bool = None
    shank_references: str = None
    gain: int = None
    input: int = None


@dataclass
class ProbeRecordingSettings:
    # The int in the Dict is the channel number
    probe: int = None
    channel_settings: Dict[int, ChannelSettings] = [None]


@dataclass
class ProbeStimulationSettings:
    # The int in the Dict is the stimulation unit number
    probe: int = None
    stimulation_unit_settings: Dict[int, StimulationUnitSettings] = [None]
    stimulation_unit_electrodes: Dict[int, ElectrodeSet] = [None]


@dataclass
class HandleSettings:
    # The int in the Dict is the probe number
    general_settings: GeneralSettings = None
    handle: str = None
    probes_recording: Dict[int, ProbeRecordingSettings] = [None]
    probes_stimulation: Dict[int, ProbeStimulationSettings] = [None]


@dataclass
class TTLSettings:
    TTL_channel: int = None
    probes: int = None
    stimulation_unit_settings: StimulationUnitSettings = None
    electrode_selection: ElectrodeSet = None
