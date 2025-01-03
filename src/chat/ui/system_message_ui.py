import streamlit as st
from langchain.schema import SystemMessage

from src.chat.ui.message_ui import MessageUI

SYSTEM_NAME = "System"


class SystemMessageUI(MessageUI):
    system_label = f"__*{SYSTEM_NAME}:*__"

    def __init__(self, message: SystemMessage, **kwargs):
        super().__init__(message, **kwargs)

    @classmethod
    def from_content(cls, content: str, **kwargs):
        return cls(message=SystemMessage(content=content), **kwargs)

    def show(self, id_):
        if self.show_full_message:  # Do not show if details is not on. Can be removed
            with st.expander(label=f"Chat {id_}. {SYSTEM_NAME}", expanded=True):
                st.markdown(f"Information about the schema and the rules.")
                if self.show_full_message:
                    st.text(f"{self.content}")
