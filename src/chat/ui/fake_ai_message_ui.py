from typing import Optional

import pandas as pd
import streamlit as st
from langchain.schema import AIMessage, BaseMessage

from src.chat.ui.ai_message_ui import GPT_NAME
from src.chat.ui.message_ui import MessageUI, Sender
from src.tools.utils import mic


class FakeAIMessageUI(MessageUI):
    gpt_label = f"__*{GPT_NAME}:*__"

    def __init__(self, message: AIMessage, **kwargs):
        super().__init__(message, **kwargs)

    @classmethod
    def from_content(cls, content: str, **kwargs):
        return cls(message=AIMessage(content=content), **kwargs)

    def show(self, id_):
        if self.show_full_message:  # Do not show if details is not on. Can be removed
            with st.expander(
                label=f"Chat {id_}. {GPT_NAME} {mic * 3} *FAKE GPT MESSAGE FROM PROMPT*",
                expanded=False,
            ):
                st.markdown(f"{self.content}")
