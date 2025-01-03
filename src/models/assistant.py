import logging

from langchain import LLMChain, PromptTemplate
from langchain.chains import SequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import BaseMessage

from src.models.chat_llms import llm_chat_gpt4
from src.models.prompts import human_message_prompt_reply

formatter = logging.Formatter("%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)


def get_assistant(history: list[BaseMessage]):
    chain = LLMChain(
        llm=llm_chat_gpt4,
        prompt=ChatPromptTemplate.from_messages(
            # history + [system_message_prompt, human_message_prompt_raw]
            history
            + [human_message_prompt_reply]
        ),
        output_key="python_code_final",
        verbose=True,
    )
    assistant_model = SequentialChain(
        chains=[chain],
        input_variables=["request"],
        output_variables=["python_code_final"],
        verbose=True,
        return_all=True,
    )
    return assistant_model
