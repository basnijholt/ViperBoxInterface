import logging
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from VB_classes import (
    Connect,
    ProbeRecordingSettings,
)
from VB_logger import _init_logging
from ViperBox import ViperBox

# TODO: all return values should be caught and logged

session_datetime = time.strftime("%Y%m%d_%H%M%S")
_init_logging(session_datetime=session_datetime)
logger = logging.getLogger(__name__)

app = FastAPI()
VB = ViperBox(_session_datetime=session_datetime, headless=True)
# multiprocessing.Process(target=gui).start()


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/test")
async def test():
    return {"result": True, "feedback": "test"}


@app.post("/connect")
async def init(connect: Connect):
    # async def init(emulation: bool = False, boxless: bool = False):
    result, feedback = VB.connect(
        probe_list=connect.probe_list,
        emulation=connect.emulation,
        boxless=connect.boxless,
    )
    return {"result": result, "feedback": feedback}


@app.post("/disconnect")
async def disconnect():
    result, feedback = VB.disconnect()
    return {"result": result, "feedback": feedback}


@app.post("/shutdown")
async def shutdown():
    result, feedback = VB.shutdown()
    return {"result": result, "feedback": feedback}


@app.post("/verify_xml/")
async def verify_xml(type: str, path: Path):
    result, feedback = VB.verify_xml(type, path)
    return {"result": result, "feedback": feedback}


@app.post("/recording_settings/")
async def recording_settings(
    recording_settings: ProbeRecordingSettings,
    reset: bool = False,
    default_values: bool = False,
):
    result, feedback = VB.recording_settings(
        XML_file_path=recording_settings, reset=reset, default_values=default_values
    )
    return {"result": result, "feedback": feedback}


@app.post("/stimulation_settings/")
async def stimulation_settings(XML_file_path: str, default_values: bool = False):
    result, feedback = VB.stimulation_settings(XML_file_path, default_values)
    return {"result": result, "feedback": feedback}


@app.post("/start_recording/")
async def start_recording(recording_name: str | None = None):
    result, feedback = VB.start_recording(recording_name=recording_name)
    return {"result": result, "feedback": feedback}


@app.post("/stop_recording/")
async def stop_recording():
    result, feedback = VB.stop_recording()
    return {"result": result, "feedback": feedback}


@app.post("/start_stimulation/")
async def start_stimulation():
    result, feedback = VB.start_stimulation()
    return {"result": result, "feedback": feedback}


@app.post("/TTL_start/")
async def TTL_start():
    result, feedback = VB.TTL_start()
    return {"result": result, "feedback": feedback}
