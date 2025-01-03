import logging

from langchain import LLMChain, PromptTemplate
from langchain.chains import SequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from src.models.chat_llms import llm_chat_gpt4
from src.models.prompts import (
    ai_data_scientist,
    human_get_python_from_steps,
    human_rephrase_raw,
    ia_rephrase_detailed,
)

formatter = logging.Formatter("%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)

system_message_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(template="""{db_schema}""", input_variables=["db_schema"])
)


chat_prompt_template_rephrase = ChatPromptTemplate.from_messages(
    [ia_rephrase_detailed, system_message_prompt, human_rephrase_raw]
)

rephrase_chain = LLMChain(
    llm=llm_chat_gpt4,
    prompt=chat_prompt_template_rephrase,
    output_key="rephrased_request",
    verbose=True,
)

chat_prompt_template_get_python = ChatPromptTemplate.from_messages(
    [
        ai_data_scientist,
        system_message_prompt,
        human_get_python_from_steps,
    ]
)

write_python_chain = LLMChain(
    llm=llm_chat_gpt4,
    prompt=chat_prompt_template_get_python,
    output_key="python_code_final",
    verbose=True,
)

python_2_model_gpt4 = SequentialChain(
    chains=[rephrase_chain, write_python_chain],
    input_variables=["request", "db_schema"],
    output_variables=["python_code_final", "rephrased_request"],
    verbose=True,
    return_all=True,
)
