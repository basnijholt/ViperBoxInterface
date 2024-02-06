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
    apiTTLStart,
    apiVerifyXML,
)
from VB_logger import _init_logging
from ViperBox import ViperBox

# TODO: all return values should be caught and logged

session_datetime = time.strftime("%Y%m%d_%H%M%S")
_init_logging(session_datetime=session_datetime)
logger = logging.getLogger(__name__)


docs = """
ViperBox API helps you stimulate and record with the ViperBox 🧠.  
"""
tags_metadata = [
    {
        "name": "connect",
        "description": "Connect to the ViperBox. This is the first step to "
        "stimulating and recording.",
    },
    {
        "name": "disconnect",
        "description": "Disconnect from the ViperBox.",
    },
]
app = FastAPI(
    title="ViperBox API",
    description=docs,
    summary="ViperBox API for stimulation and recording",
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


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/test", tags=["test"])
async def test():
    return {"result": True, "feedback": "test"}


@app.post("/connect", tags=["connect"])
async def init(connect: Connect):
    result, feedback = VB.connect(
        probe_list=connect.probe_list,
        emulation=connect.emulation,
        boxless=connect.boxless,
    )
    return {"result": result, "feedback": feedback}


@app.post("/disconnect", tags=["disconnect"])
async def disconnect():
    result, feedback = VB.disconnect()
    return {"result": result, "feedback": feedback}


@app.post("/shutdown", tags=["shutdown"])
async def shutdown():
    result, feedback = VB.shutdown()
    return {"result": result, "feedback": feedback}


@app.post("/verify_xml/", tags=["verify_xml"])
async def verify_xml(api_verify_xml: apiVerifyXML):
    result, feedback = VB.verify_xml(api_verify_xml.XML)
    return {"result": result, "feedback": feedback}


@app.post("/recording_settings/", tags=["recording_settings"])
async def recording_settings(api_rec_settings: apiRecSettings):
    result, feedback = VB.recording_settings(
        recording_settings=api_rec_settings.recording_XML,
        reset=api_rec_settings.reset,
        default_values=api_rec_settings.default_values,
    )
    return {"result": result, "feedback": feedback}


@app.post("/stimulation_settings/", tags=["stimulation_settings"])
async def stimulation_settings(api_stim_settings: apiStimSettings):
    result, feedback = VB.stimulation_settings(
        recording_settings=api_stim_settings.recording_XML,
        reset=api_stim_settings.reset,
        default_values=api_stim_settings.default_values,
    )
    return {"result": result, "feedback": feedback}


@app.post("/start_recording", tags=["start_recording"])
async def start_recording(api_start_rec: apiStartRec):
    result, feedback = VB.start_recording(recording_name=api_start_rec.recording_name)
    return {"result": result, "feedback": feedback}


@app.post("/stop_recording", tags=["stop_recording"])
async def stop_recording():
    result, feedback = VB.stop_recording()
    return {"result": result, "feedback": feedback}


@app.post("/start_stimulation/", tags=["start_stimulation"])
async def start_stimulation(api_start_stim: apiStartStim):
    result, feedback = VB.start_stimulation(api_start_stim.SU_bit_mask)
    return {"result": result, "feedback": feedback}


@app.post("/TTL_start/", tags=["TTL_start"])
async def TTL_start(api_TTL_start: apiTTLStart):
    result, feedback = VB.TTL_start(
        api_TTL_start.TTL_channel,
        api_TTL_start.TTL_XML,
        api_TTL_start.SU_bit_mask,
    )
    return {"result": result, "feedback": feedback}
