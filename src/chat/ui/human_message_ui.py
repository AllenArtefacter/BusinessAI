import streamlit as st
from langchain.schema import HumanMessage

from src.chat.ui.message_ui import MessageUI, Sender

USER_NAME = "You"


class HumanMessageUI(MessageUI):
    user_label = f"__*{USER_NAME}:*__"

    def __init__(self, message: HumanMessage, user_input: str, **kwargs):
        super().__init__(message, user_input=user_input, **kwargs)

    @classmethod
    def from_content(cls, content: str, user_input: str, **kwargs):
        return cls(
            message=HumanMessage(content=content), user_input=user_input, **kwargs
        )

    def show(self, id_):
        with st.expander(label=f"Chat {id_}. {USER_NAME}", expanded=True):
            st.markdown(f"{self.user_input}")
            if self.show_full_message:
                st.text(f"{self.content}")
