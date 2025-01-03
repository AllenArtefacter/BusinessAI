import math

import streamlit as st

from src.tools.states import (
    CANCELED,
    EXECUTION,
    FINISH,
    GENERATING,
    IDLE,
    INIT,
    PARSING,
    STATE,
)
from src.tools.utils import mic


def get_progress_bar_data(session_state, state_to_compensate_for_session_stage=IDLE):
    # model = u_session_state["model"]
    state = session_state[STATE]
    # state = session_state[STATE] if STATE in session_state else state_to_compensate_for_session_stage
    if state == IDLE:
        raise ValueError("Should not be called when state is IDLE")
    if state == INIT:
        return 0, "Initializing"
    if state == GENERATING:
        # def curve(x):
        #     math.log((x + 70) ** 2, 1.04)
        curve = lambda x: math.log((x + 70) ** 2, 1.04)
        progress = min(90, int((lambda x: curve(x) - curve(0))(50)))
        return progress, f"Generating... {mic * 3} *This part can last up to 2 minutes*"
    if state == PARSING:
        return 94, "Parsing"
    if state == EXECUTION:
        return 98, "Running Python code."
    if state == FINISH:
        return 100, "Adding message."
    # if state == CANCELED:
    #     raise ValueError("Should not be called when state is CANCELED")
