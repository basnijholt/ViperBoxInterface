import logging
import time

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from VB_logger import _init_logging
from ViperBox import ViperBox

# TODO: all return values should be caught and logged
session_datetime = time.strftime("%Y%m%d_%H%M%S")

_init_logging(session_datetime=session_datetime)
logger = logging.getLogger(__name__)
app = FastAPI()
VB = ViperBox(_session_datetime=session_datetime, headless=True)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/test")
async def test():
    return {"result": True, "feedback": "test"}


@app.post("/connect")
async def init(emulation: bool = False, boxless: bool = False):
    result, feedback = VB.connect(emulation=emulation, boxless=boxless)
    return {"result": result, "feedback": feedback}


@app.post("/recording_settings")
async def recording_settings(
    XML_file_path: str, restart: bool = False, default_values: bool = False
):
    result, feedback = VB.recording_settings(
        XML_file_path=XML_file_path, restart=restart, default_values=default_values
    )
    return {"result": result, "feedback": feedback}


@app.post("/stimulation_settings")
async def stimulation_settings(XML_file_path: str, default_values: bool = False):
    result, feedback = VB.stimulation_settings(XML_file_path, default_values)
    return {"result": result, "feedback": feedback}
