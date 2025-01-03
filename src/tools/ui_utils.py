import logging

import streamlit as st

from src.chat.ui.ai_message_ui import GPT_NAME
from src.chat.ui.conversation_ui import ConversationUI
from src.tools.progress_bar import get_progress_bar_data
from src.tools.states import (
    EXECUTION,
    FINISH,
    GENERATING,
    IDLE,
    INIT,
    MODE,
    PARSING,
    REPLY,
    STATE,
)
from src.tools.utils import mic


def display_chat(conv_: ConversationUI, show_details_, u_session_state):
    logging.info(f"Displaying chat {conv_}")

    if u_session_state[STATE] in [INIT, GENERATING, PARSING, EXECUTION, FINISH]:
        with st.expander(
            label=f"Chat {len(conv_.messages) + 1}. {GPT_NAME} {mic * 3} *{'PROCESSING'}* {mic * 3} "
            f"{('Replying to previous message' if u_session_state[MODE] == REPLY else 'New conversation')}",
            expanded=True,
        ):
            pb_col, cancel_col = st.columns([18, 1])
            with pb_col:
                progress_bar = st.progress(
                    *get_progress_bar_data(session_state=u_session_state)
                )
            with cancel_col:
                if st.button("❌", key="cancel_button"):
                    u_session_state[STATE] = IDLE
                    # u_session_state["model"].cancel()
                    progress_bar.progress(0, text="Operation cancelled.")
                    conv_.chat.delete_message(
                        conv_.chat.last_message
                    )  # Will rerun the app
                    if not len(conv_.chat):
                        conv_.delete_chat(conv_.chat)

    conv_.show_full_messages = show_details_
    logging.info(f"conv_.show() {conv_}")
    conv_.show()

    if u_session_state[STATE] in [INIT, GENERATING, PARSING, EXECUTION, FINISH]:
        return progress_bar
