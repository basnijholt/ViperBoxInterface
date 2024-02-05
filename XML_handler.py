import json
from typing import Any

from lxml import etree

from VB_classes import (
    ChanSettings,
    GeneralSettings,
    HandleSettings,
    ProbeSettings,
    SUSettings,
    parse_numbers,
    printable_dtd,
)


def check_handles_exist(data, existing_handles):
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


def check_references_format(references: str) -> bool:
    """Check if references are in the correct format

    Arguments:
    - references: string of 9 digits, only 1s and 0s

    test cases:
    - references are 10 digits
    - references contains a 2
    - references contains a letter
    """
    if len(references) != 9:
        raise ValueError("References should be a 9 digit string")
    if not all([i in ["0", "1"] for i in references]):
        raise ValueError("References should only contain 0s and 1s")
    return True


def check_gain_input_format(gain: int) -> bool:
    """Check if gain or input is in the correct format

    Arguments:
    - gain or nput: integer between 1 and 4

    test cases:
    - gain is 5
    """
    gain = int(gain)
    gain += 1
    if gain not in [1, 2, 3, 4]:
        raise ValueError(
            f"Gain/input is {gain} or input should be an integer between 1 and 4"
        )
    return True


verify_params = [
    # name, step, min, max
    ("polarity", 1, 0, 1),
    # TODO deal with infinite pulses
    ("pulses", 1, 0, 255),
    ("amplitude1", 1, 0, 255),
    ("amplitude2", 1, 0, 255),
    ("duration", 100, 100, 25500),
    ("prephase", 100, 0, 25500),
    ("width1", 10, 0, 2550),
    ("interphase", 10, 10, 2550),
    ("width2", 10, 0, 2550),
    ("discharge", 100, 0, 25500),
    ("aftertrain", 100, 0, 25500),
]


def verify_step_min_max(name: str, step: int, min_val: int, max_val: int, value: int):
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}.")
    if (value - min_val) % step != 0:
        raise ValueError(f"{name} must be a multiple of {step}.")
    return True


def overwrite_settings(data: Any, local_settings: GeneralSettings):
    """Write xml data to local settings

    Arguments:
    - data: xml data of type lxml.etree._ElementTree
    - local_settings: local settings of type GeneralSettings

    """
    # TODO deal with overwriting all settings.

    for element in data.iter():
        # goes through all elements
        if element.tag in [
            "RecordingSettings",
            "StimulationWaveformsSettings",
            "StimulationMappingSettings",
        ]:
            # if element contains recording settings, add these settings
            for settings in element:
                handles = parse_numbers(
                    settings.attrib["handle"], list(local_settings.connected.keys())
                )
                for handle in handles:
                    probes = parse_numbers(
                        settings.attrib["probe"], local_settings.connected[handle]
                    )
                    for probe in probes:
                        if settings.tag == "Channel":
                            all_channels = parse_numbers(
                                settings.attrib["channel"], list(range(1, 65))
                            )
                            for channel in all_channels:
                                check_references_format(settings.attrib["references"])
                                check_gain_input_format(settings.attrib["gain"])
                                check_gain_input_format(settings.attrib["input"])
                                local_settings.handles[handle].probes[probe].channel[
                                    channel
                                ] = ChanSettings.from_dict(settings.attrib)
                        if settings.tag == "Configuration":
                            all_waveforms = parse_numbers(
                                settings.attrib["stimunit"], list(range(1, 9))
                            )
                            for waveform in all_waveforms:
                                for parameter_set in verify_params:
                                    verify_step_min_max(
                                        *parameter_set,
                                        int(settings.attrib[parameter_set[0]]),
                                    )
                                local_settings.handles[handle].probes[
                                    probe
                                ].stim_unit_sett[waveform] = SUSettings.from_dict(
                                    settings.attrib
                                )
                        if settings.tag == "Mapping":
                            all_mappings = parse_numbers(
                                settings.attrib["stimunit"], list(range(1, 9))
                            )
                            for mapping in all_mappings:
                                local_settings.handles[handle].probes[
                                    probe
                                ].stim_unit_elec[mapping] = parse_numbers(
                                    settings.attrib["electrodes"], list(range(1, 129))
                                )
    return local_settings


def add_xml_to_local_settings(xml: str, local_settings: GeneralSettings) -> dict:
    """
    Adds the xml to the local_settings dictionary.
    """
    data = etree.fromstring(xml)
    check_handles_exist(data, list(local_settings.connected.keys()))
    local_settings = overwrite_settings(data, local_settings)

    return local_settings


# Testing code:
if __name__ == "__main__":
    strixml = """<Program>
        <Settings>
            <MetaData>
                <RecordingName>Mouse22</RecordingName>
            </MetaData>
            <TTLSettings>
                <Setting handle="1" probe="1" TTL="1" trigger_function="start_recording"
                    target_handle="1" target_probe="1" target_SU="-" />
            </TTLSettings>
            <RecordingSettings>
                <Channel handle="-" probe="-" channel="1-3" references="100101000" 
                gain="1" input="0" />
                <Channel handle="1" probe="3" channel="63" references="100000000" 
                gain="1" input="0" />
            </RecordingSettings>
            <StimulationWaveformsSettings>
                <Configuration handle="1" probe="1,2,3,4" stimunit="5-8,2,1" 
                polarity="0" pulses="20"
                    prephase="0" amplitude1="5" width1="170" interphase="60" 
                    amplitude2="5" width2="170"
                    discharge="200" duration="600" aftertrain="1000" />
                <Configuration handle="2" probe="1" stimunit="1" polarity="0" 
                pulses="20" prephase="0"
                    amplitude1="5" width1="170" interphase="60" amplitude2="5" 
                    width2="170"
                    discharge="200" duration="600" aftertrain="1000" />
            </StimulationWaveformsSettings>
            <StimulationMappingSettings>
                <Mapping handle="1,2" probe="1" stimunit="1" electrodes="1,2,5,21" />
                <Mapping handle="1" probe="1" stimunit="1" electrodes="1,5,22" />
                <Mapping handle="1" probe="2" stimunit="1" electrodes="25" />
                <Mapping handle="1" probe="3" stimunit="1" electrodes="11,12,13" />
            </StimulationMappingSettings>
        </Settings>
        <StimulationSequence>
            <Instruction type="trigger_recording" data_address="1.0.0.127" />
            <StimulationSequence>
                <Instruction type="stimulus" handle="1" probe="1,2,3,4" stimunit="1" />
                <Instruction type="wait" time="20" />
                <Instruction type="stimulus" handle="1" probe="1" stimunit="1" />
                <Instruction type="wait" time="5" />
            </StimulationSequence>
        </StimulationSequence>
    </Program>"""

    data = etree.parse("defaults/instructions.xml")
    with open("defaults/settings_classes.json") as f:
        classes = json.load(f)

    connected_handles_probes = {}
    existing_handles = [int(key) for key in classes["handles"].keys()]
    for handle in existing_handles:
        try:
            connected_handles_probes[handle] = [
                int(key) for key in classes["handles"][str(handle)]["probes"].keys()
            ]
        except KeyError:
            connected_handles_probes[handle] = []
    print(
        f"""handles: {list(connected_handles_probes.keys())} and \nhandle probe 
        dict: {connected_handles_probes}"""
    )

    local_settings = GeneralSettings()
    for key in connected_handles_probes.keys():
        local_settings.handles[key] = HandleSettings()
        for probe in connected_handles_probes[key]:
            local_settings.handles[key].probes[probe] = ProbeSettings()

    add_xml_to_local_settings(strixml, local_settings)
    printable_dtd(local_settings)
