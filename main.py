import logging
import time

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from api_classes import (
    Connect,
    apiRecSettings,
    apiStartRec,
    apiStartStim,
    apiStimSettings,
    apiVerifyXML,
)
from VB_logger import _init_logging
from ViperBox import ViperBox

# TODO: all return values should be caught and logged

session_datetime = time.strftime("%Y%m%d_%H%M%S")
_init_logging(session_datetime=session_datetime)
logger = logging.getLogger(__name__)


docs = """
# Short tutorial

To start using the the API, first connect the viperbox to the computer and switch it on.
To start using it, you need to
- /connect (click the dropdown > Try it out > Execute). Wait until you can read \
    result: true, feedback: Viperbox initialized successfully with ...
- /recording_settings, upload recording settings, by default this is set to true.
- /start_recording, first change the recording name to your desired name, then click \
    Execute.
- [OPTIONAL] /stimulation_settings, upload stimulation settings, by default this is \
    set to false.
- [OPTIONAL] /start_stimulation, start the stimulation, by default this is set to false.
- /stop_recording, to stop the recording.

Recording files will show up in the /Recordings folder.
Stimulation records will show up in the /Stimulations folder.
"""
# tags_metadata = [
#     {
#         "name": "connect",
#         "description": "Connect to the ViperBox. This is the first step to "
#         "stimulating and recording 🧠",
#     },
#     {
#         "name": "disconnect",
#         "description": "Disconnect from the ViperBox.",
#     },
# ]
app = FastAPI(
    title="ViperBox API",
    description=docs,
    summary="API to manage stimulation and recording of the ViperBox, built for \
    NeuraViPeR.",
    version="0.0.1",
    contact={
        "name": "Stijn Balk",
        "email": "stijn@phosphoenix.nl",
    },
    license_info={
        "name": "GPL-2.0 license",
        "url": "https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html",
    },
)
VB = ViperBox(_session_datetime=session_datetime, headless=True)
# multiprocessing.Process(target=gui).start()


# @app.get("/test", tags=["test"])
# async def test():
#     return {"result": True, "feedback": "test"}


@app.post("/connect", tags=["connect"])
async def init(connect: Connect):
    """
    Initializes the ViperBoxInterface.

    Args:
    - probes (default: "1") list of connected ASIC's (also called probes). "1" for
    only one probe, "1,2" for two probes, etc. Max 4 probes.
    - emulation (default: false): whether data should be emulated (true) or real data
    should be sent (false).
    - boxless (default: false): only for testing the software without a box connected
    to the computer.

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info(f"API /connect called with {Connect}")
    result, feedback = VB.connect(
        probe_list=connect.probes,
        emulation=connect.emulation,
        boxless=connect.boxless,
    )
    return {"result": result, "feedback": feedback}


@app.post("/disconnect", tags=["disconnect"])
async def disconnect():
    """
    Disconnects from the ViperBox.

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info("API /disconnect called")
    result, feedback = VB.disconnect()
    return {"result": result, "feedback": feedback}


@app.post("/shutdown", tags=["shutdown"])
async def shutdown():
    """
    Shuts down the ViperBoxInterface, apart from disconnect, it also tries to close
    Open Ephys.

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info("API /shutdown called")
    result, feedback = VB.shutdown()
    return {"result": result, "feedback": feedback}


@app.post("/verify_xml/", tags=["verify_xml"])
async def verify_xml(api_verify_xml: apiVerifyXML):
    """
    Verify XML in string format (plain text). The settings that are in the uploaded
    XML are also checked with the existing settings. For example, if they contain
    settings for probes that are not connected, an error will be thrown.

    Args:
    - XML: Settings XML to be checked.
    - check_topic: must be one of 'all', 'recording' or 'stimulation'. This says
    something about which part of the settings will be checked. If 'stimulation'
    is selected, both the settings in StimulationWaveformsSettings and in
    StimulationMappingSettings will be checked.

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info(f"API /verify_xml called with {api_verify_xml}")
    result, feedback = VB.verify_xml_with_local_settings(
        api_verify_xml.XML, api_verify_xml.check_topic
    )
    return {"result": result, "feedback": feedback}


@app.post("/recording_settings/", tags=["recording_settings"])
async def recording_settings(api_rec_settings: apiRecSettings):
    """
    Upload recording settings.

    Parameters:
    - recording_XML (string): Recording settings XML.
    - reset (boolean): To do a reset of all settings and start with a clean slate;
    select true, else select false (default).
    - default_values (boolean): if this is 'true', the input from recording_XML will
    be ignored and default recording settings will be uploaded from
    /defaults/default_recording_settings.xml

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info(f"API /recording_settings called with {api_rec_settings}")
    result, feedback = VB.recording_settings(
        xml_string=api_rec_settings.recording_XML,
        reset=api_rec_settings.reset,
        default_values=api_rec_settings.default_values,
    )
    return {"result": result, "feedback": feedback}


@app.post("/stimulation_settings/", tags=["stimulation_settings"])
async def stimulation_settings(api_stim_settings: apiStimSettings):
    """
    Upload stimulation settings.

    Parameters:
    - stimulation_XML (string): Stimulation settings XML.
    - reset (boolean): To do a reset of all settings and start with a clean slate;
    select true, else select false (default).
    - default_values (boolean): if this is 'true', the input from stimulation_XML will
    be ignored and default stimulation settings will be uploaded from
    /defaults/default_stimulation_settings.xml

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info(f"API /stimulation_settings called with {api_stim_settings}")
    result, feedback = VB.stimulation_settings(
        xml_string=api_stim_settings.stimulation_XML,
        reset=api_stim_settings.reset,
        default_values=api_stim_settings.default_values,
    )
    return {"result": result, "feedback": feedback}


@app.post("/start_recording", tags=["start_recording"])
async def start_recording(api_start_rec: apiStartRec):
    """
    Starts recording with the specified recording name. Recording is saved in
    /Recordings. Also creates a record of all the actions and stimulations that have
    been performed by the user in /Stimulations.

    Parameters:
    - recording_name (string): Recording name.

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info(f"API /start_recording called with {api_start_rec}")
    result, feedback = VB.start_recording(recording_name=api_start_rec.recording_name)
    return {"result": result, "feedback": feedback}


@app.post("/stop_recording", tags=["stop_recording"])
async def stop_recording():
    """
    Stops the recording.

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info("API /stop_recording called")
    result, feedback = VB.stop_recording()
    return {"result": result, "feedback": feedback}


@app.post("/start_stimulation/", tags=["start_stimulation"])
async def start_stimulation(api_start_stim: apiStartStim):
    """
    Triggers the selected stimulation units.

    Args:
    - handles (string) (default: "1", only implemented for 1): All ViperBoxes on
    which stimulation should occur. "1" for only one ViperBox, "1,2" for two boxes,
    etc. Max 3 boxes.
    - probes (string) (default: "1"): All ASIC's/probes on which stimulation should
    occur. Max 4 probes.
    - SU_input (string) (default: "1,2,3,4,5,6,7,8"): All Stimulation Units (SU's) on
    which stimulation should occur. Max 8 SU's.

    Returns:
    - boolean: true if correctly executed, otherwise false.
    - feedback: More information on execution.
    """
    logging.info(f"API /start_stimulation called with {api_start_stim}")
    result, feedback = VB.start_stimulation(
        handles=api_start_stim.handles,
        probes=api_start_stim.probes,
        SU_input=api_start_stim.SU_input,
    )
    return {"result": result, "feedback": feedback}


# @app.post("/TTL_start/", tags=["TTL_start"])
# async def TTL_start(api_TTL_start: apiTTLStart):
#     result, feedback = VB.TTL_start(
#         api_TTL_start.TTL_channel,
#         api_TTL_start.TTL_XML,
#         api_TTL_start.SU_bit_mask,
#     )
#     return {"result": result, "feedback": feedback}


# @app.post("/TTL_stop/", tags=["TTL_stop"])
# async def TTL_stop(api_TTL_stop: apiTTLStop):
#     result, feedback = VB.TTL_stop(apiTTLStop.TTL_channel)
#     return {"result": result, "feedback": feedback}


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
    # return RedirectResponse(url="/redoc")
