import logging
from typing import Optional

import streamlit as st
from langchain.schema import AIMessage

from src.chat.chat import Chat
from src.chat.conversation import Conversation
from src.chat.message import Message
from src.chat.ui.chat_ui import ChatUI

logger = logging.getLogger(__name__)


def group_messages_by_chat_id(messages: list[Message]) -> dict[str, list[Message]]:
    grouped_messages = {}
    for message in messages:
        chat_id = message.chat_id
        if chat_id not in grouped_messages:
            grouped_messages[chat_id] = []
        grouped_messages[chat_id].append(message)

    return grouped_messages


class ConversationUI(Conversation):
    """
    Child of Conversation class that adds some UI specific methods.
    session_state being is stored here is a workaround using st.session_state behaving weirdly.
    """

    def __init__(self, session_state, chats: list[ChatUI] = None):
        super().__init__(chats)
        self.session_state = session_state
        self.show_full_messages = False

    def new_chat(self):
        self._chats.append(ChatUI(self.session_state))

    def show(self):
        nb_messages = len(self.messages)
        logging.info(f"Showing {nb_messages} messages")
        for i, message in enumerate(self.messages[::-1]):
            message.show_full_message = self.show_full_messages
            message.show(nb_messages - i)

    @classmethod
    def from_session_state(cls, session_state):
        if "messages" not in session_state:
            session_state["messages"] = []
        chats = group_messages_by_chat_id(session_state["messages"])
        chats = [
            ChatUI(session_state=session_state, messages=chats[chat_id])
            for chat_id in chats
        ]
        return cls(session_state=session_state, chats=chats)

    def __str__(self):
        return "\n".join(
            [f"id: {chat.id}: {len(chat)} messages" for chat in self._chats]
        )

    def __repr__(self):
        return self.__str__()
