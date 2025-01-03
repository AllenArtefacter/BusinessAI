import logging
from typing import Optional

import pandas as pd
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class Message:
    """
    This class is used to represent a message using easily message class from langchain
    this class allow for serialization and deserialization of the message
    and makes it easy to use with other langchain classes.
    It is stored in this class to allow for custom method and make this class easier to use
    """

    def __init__(self, message: BaseMessage, **kwargs):
        self.message: BaseMessage = message
        # combine all kwargs into additional_kwargs
        self.message.additional_kwargs = self.message.additional_kwargs | kwargs
        if not self.message.additional_kwargs.get("id", None):
            self.message.additional_kwargs["id"] = id(self)
        if self.datetime is None:
            self.message.additional_kwargs["datetime"] = pd.Timestamp.now()

    @classmethod
    def from_base_message(cls, message: BaseMessage, **kwargs):
        return cls(message=message, **kwargs)

    @classmethod
    def from_content_type(cls, content: str, type: str, **kwargs):
        if type == "ai":
            return cls(AIMessage(content=content), **kwargs)
        elif type == "human":
            return cls(HumanMessage(content=content), **kwargs)
        elif type == "system":
            return cls(SystemMessage(content=content), **kwargs)
        raise ValueError(f"Type must be either 'ai' or 'human' or 'system' not {type}")

    @property
    def id(self):
        id_ = self.message.additional_kwargs.get("id", None)
        if id_ is None:
            logger.warning(f"Message [[[{self}]]] has no id")
        return id_

    @property
    def content(self):
        return self.message.content

    @property
    def type(self):
        return self.message.type

    @property
    def code(self):
        return self.message.additional_kwargs.get("code", None)

    @property
    def state(self):
        return self.message.additional_kwargs.get("state", None)

    @property
    def result_dataframe(self) -> Optional[pd.DataFrame]:
        if self.type != "ai":
            logger.warning(
                f"result_dataframe is only available for ai messages not {self.type}"
            )
        return self.message.additional_kwargs.get("result_dataframe", None)

    @property
    def result_figure(self):
        if self.type != "ai":
            logger.warning(
                f"result_figure is only available for ai messages not {self.type}"
            )
        return self.message.additional_kwargs.get("result_figure", None)

    @property
    def result_error(self) -> Optional[str]:
        if self.type != "ai":
            logger.warning(
                f"result_error is only available for ai messages not {self.type}"
            )
        return self.message.additional_kwargs.get("result_error", None)

    @property
    def chat_id(self) -> str:
        chat_id_ = self.message.additional_kwargs.get("chat_id", None)
        if chat_id_ is None:
            raise ValueError(f"Message {self} has no chat_id")
        return chat_id_

    @property
    def datetime(self) -> pd.Timestamp:
        return self.message.additional_kwargs.get("datetime", None)

    @property
    def user_input(self) -> Optional[str]:
        if self.type != "human":
            logger.warning(
                f"user_input is only available for human messages not {self.type}"
            )
        return self.message.additional_kwargs.get("user_input", None)

    @property
    def prompted_ai_message(self) -> Optional[bool]:
        """When the IA message is not generated by the AI but as been prompt by the user"""
        if self.type != "ai":
            logger.warning(
                f"prompted_ai_message is only available for ai messages not {self.type}"
            )
        return self.message.additional_kwargs.get("prompted_ai_message", None)

    def set_result_dataframe(self, result_dataframe: pd.DataFrame):
        if self.type != "ai":
            logger.warning(
                f"set_result_dataframe is only available for ai messages not {self.type}"
            )
        self.message.additional_kwargs["result_dataframe"] = result_dataframe

    def set_result_error(self, result_error: str):
        if self.type != "ai":
            logger.warning(
                f"set_result_error is only available for ai messages not {self.type}"
            )
        self.message.additional_kwargs["result_error"] = result_error

    def set_code(self, code: str):
        if self.type != "ai":
            logger.warning(
                f"set_code is only available for ai messages not {self.type}"
            )
        self.message.additional_kwargs["code"] = code

    def set_chat_id(self, chat_id: str):
        self.message.additional_kwargs["chat_id"] = chat_id

    def is_from_ai(self):
        return self.type == "ai"

    def is_from_human(self):
        return self.type == "human"

    def is_from_system(self):
        return self.type == "system"

    @property
    def lang_chain_message(self):
        return self.message

    def __repr__(self):
        return f"{self.type}: {self.content}"

    def __str__(self):
        return self.message.content

    def __dict__(self):
        return self.message.__dict__

    def __eq__(self, other):
        return self.id == other.id