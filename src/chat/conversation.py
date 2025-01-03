import logging
from typing import Optional

from langchain.schema import AIMessage

from src.chat.chat import Chat
from src.chat.message import Message
from src.chat.ui.ui_utils import update_session_state_conversation_messages

logger = logging.getLogger(__name__)


class Conversation:

    """
    This class works as a chat manager. You always use last chat by default.
    """

    def __init__(self, chats: list[Chat] = None):
        self._chats: list[Chat] = chats or [Chat()]

    @property
    def chat(self):
        """return currently used chat i.e. the last one in the list"""
        return self._chats[-1]

    def new_chat(self):
        self._chats.append(Chat())

    @update_session_state_conversation_messages
    def delete_chat(self, chat):
        self._chats.remove(chat)

    @update_session_state_conversation_messages
    def clear(self):
        self._chats = []

    def iterate_over_messages(self):
        """iterate over messages in each chat"""
        for chat in self._chats:
            for message in chat:
                yield message

    def __iter__(self):
        return iter(self._chats)

    def __len__(self):
        return len(self._chats)

    def len_msgs(self):
        return len(self.messages)

    @property
    def messages(self):
        return [message for message in self.iterate_over_messages()]


if __name__ == "__main__":
    pass
