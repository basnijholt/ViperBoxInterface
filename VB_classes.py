from dataclasses import dataclass
from typing import Dict

# handle contains 4 probes
# each probe contains 64 channels, 8 SU's and 128 electrodes
# recording goes through the 64 channels
# stimulation goes through the 8 SU's


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


@dataclass
class StimulationUnitSettings:
    stimulation_unit: int | None = None
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


@dataclass
class ElectrodeSet:
    stimulation_unit: int | None = None
    electrode_set: list | None = None


@dataclass
class ChannelSettings:
    channel: int | None = None
    body_reference: bool | None = None
    shank_references: str | None = None
    gain: int | None = None
    input: int | None = None


@dataclass
class ProbeRecordingSettings:
    # The int in the Dict is the channel number
    probe: int | None = None
    channel_settings: Dict[int, ChannelSettings] | None = None


@dataclass
class ProbeStimulationSettings:
    # The int in the Dict is the stimulation unit number
    probe: int | None = None
    stimulation_unit_settings: Dict[int, StimulationUnitSettings] | None = None
    stimulation_unit_electrodes: Dict[int, ElectrodeSet] | None = None


@dataclass
class HandleSettings:
    # The int in the Dict is the probe number
    general_settings: GeneralSettings | None = None
    handle: str | None = None
    probes_recording: Dict[int, ProbeRecordingSettings] | None = None
    probes_stimulation: Dict[int, ProbeStimulationSettings] | None = None


@dataclass
class TTLSettings:
    TTL_channel: int | None = None
    probes: int | None = None
    stimulation_unit_settings: StimulationUnitSettings | None = None
    electrode_selection: ElectrodeSet | None = None
