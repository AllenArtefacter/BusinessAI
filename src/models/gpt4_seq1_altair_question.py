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
    system_message_prompt_question,
)

formatter = logging.Formatter("%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)


ia_ds_expert = AIMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""I am a professional data-scientist developer with over 20 years in python coding.
Ask me anything about your data and I will define the steps and write the python code for you.""",
        input_variables=[],
    )
)

human_get_python = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""Request: ```{request}```. 
A. If the request is not clear, ask for clarifications by writing
    QUESTION: <question>

    Examples of questions:
        QUESTION: can you give me an example of <something>?
        QUESTION: can you give me more details about <something>?
        QUESTION: how to calculate <something>?

B. OTHERWISE, make assumptions about the what is the expected result and the appropriate air plot. Specifically,
        1. Determine what altair plot would be most appropriate for this request: type, axis, all specs... The plot has to be human readable with labels and legends and have a reasonable size.
        2. Determine the overall way to get the result from the dataframes
        3. Define the steps to get the result : join, filter, groupby, etc.
        4. Write the python code. Save the final dataframe in `saved_dataframe` variable and the final plot in `saved_figure` variable."

    Important: Anything not in the "SCHEMA:" is not available and will not be provided.

You must do A. or B.
""",
        input_variables=["request"],
    )
)

"""
        4. Write the python code. Save your plot in `saved_figure` variable. Also save the final dataframe in `saved_dataframe` variable.
"""

llm_chain_gpt4 = LLMChain(
    llm=llm_chat_gpt4,
    prompt=ChatPromptTemplate.from_messages(
        [
            ia_ds_expert,
            system_message_prompt_question,
            human_get_python,
        ]
    ),
    output_key="python_code_final",
    verbose=True,
)

gpt4_seq1_altair_question = SequentialChain(
    chains=[llm_chain_gpt4],
    input_variables=["request", "db_schema"],
    output_variables=["python_code_final"],
    verbose=True,
    return_all=True,
)
