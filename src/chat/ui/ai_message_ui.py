from enum import Enum
from typing import Optional, Union

import altair
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from langchain.schema import AIMessage

from src.chat.ui.message_ui import MessageUI
from src.chat.ui.ui_utils import streamlit_plot_figure
from src.tools.utils import mic

GPT_NAME = "Business Artificial Intelligence"


class AIMessageState(Enum):
    OK = "ok"  # Code received and executed successfully
    ERROR = "error"  # Code received but failed to execute
    QUESTION = (
        "question"  # The AI lacked information and asked a question to get more details
    )
    INCOMPLETE = "incomplete"  # The AI did not finish the sentence or the code


state_ui = {
    AIMessageState.OK: "SUCCESS ✅",
    AIMessageState.ERROR: "FAILURE ❌",
    AIMessageState.QUESTION: "QUESTION ❓",
    AIMessageState.INCOMPLETE: "INCOMPLETE ⏳",
}


def message_is_too_short_to_be_incomplete(content):
    """
    If less than 5 lines
    """
    return len(content.split("\n")) < 5


def get_state(
    message: AIMessage,
    result_dataframe: Optional[pd.DataFrame],
    result_figure: Optional[plt.Figure],
    result_error: Optional[str],
):
    if result_error is not None:
        return AIMessageState.ERROR
    elif result_dataframe is not None or result_figure is not None:
        return AIMessageState.OK
    elif "QUESTION:" in message.content or message_is_too_short_to_be_incomplete(message.content):
        return AIMessageState.QUESTION
    else:
        return AIMessageState.INCOMPLETE


def get_question(content: str):
    """
    Get all the text after QUESTION:
    """
    if "QUESTION:" in content:
        return content.split("QUESTION:")[1].strip()
    return content


class AIMessageUI(MessageUI):
    gpt_label = f"__*{GPT_NAME}:*__"

    def __init__(
        self,
        message: AIMessage,
        result_dataframe: Optional[pd.DataFrame],
        result_figure: Optional[plt.Figure],
        result_error: Optional[str],
        **kwargs,
    ):
        super().__init__(
            message,
            state=get_state(message, result_dataframe, result_figure, result_error),
            result_dataframe=result_dataframe,
            result_figure=result_figure,
            result_error=result_error,
            **kwargs,
        )

    @classmethod
    def from_content(
        cls,
        content: str,
        result_dataframe: Optional[pd.DataFrame],
        result_figure: Optional[
            Union[plt.Figure, altair.vegalite.v4.api.Chart]
        ],
        result_error: Optional[str],
        **kwargs,
    ):
        return cls(
            message=AIMessage(content=content),
            result_dataframe=result_dataframe,
            result_figure=result_figure,
            result_error=result_error,
            **kwargs,
        )

    def show(self, id_):
        with st.expander(
            label=f"Chat {id_}. {GPT_NAME} {mic * 3} *{state_ui[self.state or 'Unknown 🤔']}* {mic * 3} ",
            # f"{'History Used' if self.history_used else 'History Not Used'}",
            expanded=True,
        ):
            if self.state == AIMessageState.OK:
                if self.result_dataframe is not None:
                    st.write(self.result_dataframe)
                if self.result_figure is not None:
                    streamlit_plot_figure(self.result_figure)

            if self.state == AIMessageState.ERROR:
                assert self.result_error is not None
                st.markdown("**Error**:")
                st.code(self.result_error)

            if self.state == AIMessageState.QUESTION:
                st.markdown(f"**Question:** {get_question(self.content)}")

            if self.state == AIMessageState.INCOMPLETE:
                st.markdown(f"**Incomplete {GPT_NAME} Reply:**")
                st.write(f"{self.content}")

            if self.show_full_message:
                st.markdown(f"**Full {GPT_NAME} Reply:**")
                st.write(f"{self.content}")
