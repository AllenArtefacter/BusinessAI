import logging
from typing import Optional

from langchain.schema import AIMessage

from src.chat.message import Message

logger = logging.getLogger(__name__)


class Chat:
    def __init__(self, messages: list[Message] = None):
        self._messages: list[Message] = []
        self.id = id(self)

        if messages:
            print(messages)
            chat_id_from_messages = next(
                (message.chat_id for message in messages), None
            )
            self.id = chat_id_from_messages or self.id
            self.add_messages(messages)  # Ensure chat_id is set

    def add_message(self, message: Message):
        if message not in self.messages:
            message.message.additional_kwargs["chat_id"] = self.id
            self.messages.append(message)

    def add_messages(self, messages):
        for message in messages:
            self.add_message(message)

    def edit_message(self, old_message, new_message):
        index = next(
            (i for i, message in enumerate(self.messages) if message == old_message),
            None,
        )
        if index is not None:
            self.messages[index] = new_message
        else:
            logger.warning(f"Message {old_message} not found in chat {self}")

    def delete_message(self, message):
        self.messages.remove(message)

    def clear(self):
        self._messages = []

    @property
    def last_gpt_message(self) -> Optional[AIMessage]:
        return next(
            (message for message in reversed(self.messages) if message.is_from_ai()),
            None,
        )

    @property
    def last_human_message(self) -> Optional[Message]:
        return next(
            (message for message in reversed(self.messages) if message.is_from_human()),
            None,
        )

    @property
    def messages(self) -> list[Message]:
        return self._messages

    @property
    def last_message(self):
        if not self.messages or not len(self.messages):
            return None
        return self.messages[-1]

    def last_message_is_from_human(self):
        if not self.last_message:
            return False
        return self.last_message.is_from_human()

    def last_message_is_from_ai(self):
        if not self.last_message:
            return False
        return self.last_message.is_from_ai()

    def __iter__(self):
        return iter(self.messages)

    def __reversed__(self):
        return reversed(self.messages)

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, item):
        return self.messages[item]

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_message(cls, message, **kwargs):
        return cls(messages=[message])

    def __str__(self):
        return f"Chat {self.id}\n\n" + "\n".join(
            ["Chat:"] + [f"{i}: {message}" for i, message in enumerate(self.messages)]
        )

    def get_base_messages(self):
        return [message.message for message in self.messages]


if __name__ == "__main__":
    pass
