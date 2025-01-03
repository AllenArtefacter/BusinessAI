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

from src.models.chat_llms import llm_chat_gpt4
from src.models.prompts import (
    ai_data_scientist,
    human_get_python,
    system_message_prompt,
)

formatter = logging.Formatter("%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)

chat_prompt = ChatPromptTemplate.from_messages(
    [ai_data_scientist, system_message_prompt, human_get_python]
)


llm_chain_gpt4 = LLMChain(
    llm=llm_chat_gpt4, prompt=chat_prompt, output_key="python_code_final", verbose=True
)

python_1_model_gpt4 = SequentialChain(
    chains=[llm_chain_gpt4],
    input_variables=["request", "db_schema"],
    output_variables=["python_code_final"],
    verbose=True,
    return_all=True,
)
