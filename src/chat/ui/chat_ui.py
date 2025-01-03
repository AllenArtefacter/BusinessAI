import datetime
from enum import Enum
from typing import Optional, cast

import pandas as pd
import streamlit as st
from langchain.schema import BaseMessage

from src.chat.chat import Chat
from src.chat.ui.ai_message_ui import AIMessageUI
from src.chat.ui.human_message_ui import HumanMessageUI
from src.chat.ui.message_ui import MessageUI
from src.chat.ui.ui_utils import update_session_state_chat_messages


class ChatUI(Chat):
    """
    This class allows for separation between streamlit related chat and the chat class
    session_state being is stored here is a workaround using st.session_state behaving weirdly.
    """

    def __init__(self, session_state, messages: list[MessageUI] = None):
        super().__init__(messages=None)
        self.show_full_messages: bool = False
        self.session_state = session_state

        if messages:
            chat_id_from_messages = next(
                (message.chat_id for message in messages), None
            )
            self.id = chat_id_from_messages or self.id
            self.add_messages(messages, silent=True)  # Ensure chat_id is set

    def show(self):
        for i, message in enumerate(self[::-1]):
            message.show_full_message = self.show_full_messages
            message.show(len(self) - i)

    @classmethod
    def from_session_state(cls, session_state):
        if "messages" not in session_state:
            session_state["messages"] = []
        return cls(session_state=session_state, messages=session_state["messages"])

    @update_session_state_chat_messages
    def add_message(self, message: MessageUI, **kwargs):
        super().add_message(message)

    @update_session_state_chat_messages
    def add_messages(self, messages: list[MessageUI], **kwargs):
        for message in messages:
            self.add_message(message, **kwargs)

    @update_session_state_chat_messages
    def add_base_messages(self, messages: list[BaseMessage], **kwargs):
        self.add_messages(
            [MessageUI.from_base_message(msg) for msg in messages], **kwargs
        )

    @update_session_state_chat_messages
    def edit_message(self, old_message: MessageUI, new_message: MessageUI, **kwargs):
        super().edit_message(old_message, new_message)

    @update_session_state_chat_messages
    def delete_message(self, message: MessageUI, **kwargs):
        super().delete_message(message)

    @update_session_state_chat_messages
    def clear(self, **kwargs):
        super().clear()

    @property
    def last_gpt_message(self) -> Optional[AIMessageUI]:
        return super().last_gpt_message

    @property
    def last_human_message(self) -> Optional[HumanMessageUI]:
        return super().last_human_message

    @property
    def messages(self) -> list[MessageUI]:
        msgs = super().messages
        # assert all(
        #     issubclass(type(message), MessageUI) for message in msgs
        # ), f"Expected MessageUI, got {[type(message) for message in msgs]}"
        # return cast(list[MessageUI], msgs)
        return msgs

    @property
    def last_message(self):
        return self.messages[-1]

    def __iter__(self):
        return iter(self.messages)

    def __reversed__(self):
        return reversed(self.messages)

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, item):
        return self.messages[item]

    # @classmethod
    # def from_message(cls, message, **kwargs):
    #     return cls(messages=[message], session_state=kwargs["session_state"])

    def __str__(self):
        return "\n".join(
            ["Chat:"] + [f"{i}: {message}" for i, message in enumerate(self.messages)]
        )


if __name__ == "__main__":
    pass
