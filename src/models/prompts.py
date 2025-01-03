from langchain import PromptTemplate
from langchain.prompts import (
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# =========================================================================================== #
# System
# =========================================================================================== #

system_message_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(template="""{db_schema}""", input_variables=["db_schema"])
)

system_message_prompt_question = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""{db_schema}
    
To ask question write
QUESTION: <question>
""",
        input_variables=["db_schema"],
    )
)

# =========================================================================================== #
# AI
# =========================================================================================== #

# Rephrase : Steps

ia_rephrase_detailed = AIMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""For many years, I have assisted data analysts in comprehending executive requests. I specialize in transforming raw requests into clear and concise steps. While ensuring that my explanations align with the data schema, I provide guidance on:

- Specific expected outputs
- Joins and merges
- Grouping by categories
- Filters
- Handling missing values
- Sorting

After providing these insights, I allow the data scientist to write the necessary Pandas Python code.""",
        input_variables=[],
    )
)

# Python code

ai_data_scientist = AIMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""As a data scientist with over 10 years of experience, I have the expertise to understand your requirements and fulfill your requests using Python and Pandas.""",
        input_variables=[],
    )
)

ia_steps_and_code_detailed = AIMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""For many years, I have been assisting data analysts in understanding executive requests by transforming raw requests into clear and concise steps. While making sure my explanations align with the data schema, I provide guidance on:

Specific expected outputs
Joins and merges
Grouping by categories
Filters
Handling missing values
Sorting
With over 10 years of experience as a Python expert, I have the expertise to understand and fulfill your requests using Python and Pandas. I meticulously write Python code, considering the input, output, and execution of each step. To facilitate understanding, I break down the process into multiple Python sub-steps.

Having worked with Python and Pandas for more than 20 years, I am well-versed in all the nuances and up-to-date best practices. I take pride in writing clear and efficient Python code.""",
        input_variables=[],
    )
)

ia_python_expert = AIMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""I am a professional python developer. I write python code for each of python step by thinking about the input, the output and execution of each step. To help the understanding I break down the different steps into multiple python sub-steps.
I have worked with python and pandas for more than 20 years. I know all the subtleties and the most recent best practices
I write clear python code.""",
        input_variables=[],
    )
)


# =========================================================================================== #
# Human
# =========================================================================================== #

human_message_prompt_raw = HumanMessagePromptTemplate(
    prompt=PromptTemplate(template="{request}", input_variables=["request"])
)

human_message_prompt_reply = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""{request}
Important: Write the whole code. Do NOT continue the previous one if any. 
""",
        input_variables=["request"],
    )
)

# Get Python code

human_get_python = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""Request: {request}. 
I cannot give more details, make assumption if needed.
Store the final result in the variable named `saved_dataframe`.""",
        input_variables=["request"],
    )
)

human_get_python_from_steps = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["rephrased_request"],
        template="""My adviser broke down my request into the following steps:
{rephrased_request}.

Store the final result in the variable named `saved_dataframe`.""",
    )
)

# Get rephrase / steps

human_rephrase_raw = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="""Request: {request}. 
I cannot give more details, make assumption if needed.
Just make everything clear. Don't write the python code.""",
        input_variables=["request"],
    )
)
