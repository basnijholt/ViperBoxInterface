from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, constr

from ViperBox import ViperBox


class Bitmask(BaseModel):
    bitmask: constr(regex="^[01]{16}$")


app = FastAPI()
VB = ViperBox()


@app.get("/test")
async def test():
    return {"result": True, "feedback": "test"}


@app.post("/connect")
async def init(test: Optional[bool] = False):
    result, feedback = VB.connect(test)
    # try:
    #     result, feedback = VB.init(test)
    # except NeuraviperAPIError as e:
    #     result, feedback = False, f"NeuraviperAPIError: {e}: {error_dct[e]}"
    return {"result": result, "feedback": feedback}


@app.post("/recording_settings")
async def recording_settings(XML_file: str, default_values: Optional[bool] = False):
    result, feedback = VB.recording_settings(XML_file, default_values)
    return {"result": result, "feedback": feedback}


@app.post("/stimulation_settings")
async def stimulation_settings(XML_file: str, default_values: Optional[bool] = False):
    result, feedback = VB.stimulation_settings(XML_file, default_values)
    return {"result": result, "feedback": feedback}


@app.post("/start_recording")
async def start_recording(recording_name: str):
    result, feedback = VB.start_recording(recording_name)
    return {"result": result, "feedback": feedback}


@app.post("/stop_recording")
async def stop_recording():
    result, feedback = VB.stop_recording()
    return {"result": result, "feedback": feedback}


@app.post("/start_stimulation")
async def start_stimulation(bitmask: Bitmask):
    result, feedback = VB.start_stimulation(bitmask.bitmask)
    return {"result": result, "feedback": feedback}


@app.post("/enter_test_mode")
async def enter_test_mode():
    result, feedback = VB.enter_test_mode()
    return {"result": result, "feedback": feedback}


@app.post("/exit_test_mode")
async def exit_test_mode():
    result, feedback = VB.exit_test_mode()
    return {"result": result, "feedback": feedback}


@app.post("/start_BIST")
async def start_BIST(BIST_number: int):
    result, feedback = VB.start_BIST(BIST_number)
    return {"result": result, "feedback": feedback}


@app.post("/start_impedance")
async def start_impedance(XML_file: str):
    result, feedback = VB.start_impedance(XML_file)
    return {"result": result, "feedback": feedback}


@app.post("/start_TTL")
async def start_TTL(SU_bitmask: str, TTL_channel: int, activation_sequence: str):
    result, feedback = VB.start_TTL(SU_bitmask, TTL_channel, activation_sequence)
    return {"result": result, "feedback": feedback}


@app.post("/stop_TTL")
async def stop_TTL(TTL_channel: int):
    result, feedback = VB.stop_TTL(TTL_channel)
    return {"result": result, "feedback": feedback}


@app.post("/start_script")
async def start_script(XML_file: str):
    result, feedback = VB.start_script(XML_file)
    return {"result": result, "feedback": feedback}


@app.post("/stop_script")
async def stop_script():
    result, feedback = VB.stop_script()
    return {"result": result, "feedback": feedback}


@app.post("/shutdown")
async def shutdown():
    result, feedback = VB.shutdown()
    return {"result": result, "feedback": feedback}
