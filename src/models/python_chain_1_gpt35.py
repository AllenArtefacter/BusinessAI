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

from src.models.chat_llms import llm_chat_gpt3
from src.models.prompts import (
    human_get_python,
    ia_steps_and_code_detailed,
    system_message_prompt,
)

formatter = logging.Formatter("%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)

chat_prompt = ChatPromptTemplate.from_messages(
    [ia_steps_and_code_detailed, system_message_prompt, human_get_python]
)

python_1_chain = LLMChain(
    llm=llm_chat_gpt3, prompt=chat_prompt, output_key="python_code_final", verbose=True
)

python_1_model_gpt3 = SequentialChain(
    chains=[python_1_chain],
    input_variables=["request", "db_schema"],
    output_variables=["python_code_final"],
    verbose=True,
    return_all=True,
)

if __name__ == "__main__":
    formatted_prompt = python_1_chain.prompt.format_prompt(
        db_schema="df_inv, df_price, df_sales", request="top 5 products"
    )
    formatted_prompt2 = python_1_chain.prep_prompts(
        [{"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"}]
    )
    # print(f"{python_1_prompt.llm=}")
    print(f"{formatted_prompt=}")
    print(f"{formatted_prompt2=}")

    res = python_1_chain.run(
        {"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"}
    )
    # run = python_1_prompt.run(**{"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"})
    # predict = python_1_prompt.predict(**{"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"})
    # call = python_1_prompt.__call__({"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"})
    # generate = python_1_prompt.generate([{"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"}])

    print(f"{res=}")
    # print(f"{run=}")
    # print(f"{predict=}")
    # print(f"{call=}")
    # print(f"{generate=}")

    print(f"{python_1_chain.memory=}")

# formatted_prompt = ChatPromptValue(messages=[AIMessage(
#     content='For many years I have helped data scientist to understand executive request. Often they have an idea of what they want but they are not able to express it clearly. I break down the problem into main and sub-steps. More specifically, while making sure what I explain is feasible with the data schema, I explain :\n    - Precise expected output\n    - joins & merges\n    - filters\n    - missing values handling\n    - sort\n\nOnce I have done this, I become a professional python developer. I write python code for each of python step by thinking about the input, the output and execution of each. To help the understanding I break down the different steps into multiple python sub-steps.\nI have worked with python and pandas for more than 20 years. I know all the subtleties and the most recent best practices\nI write clear python code.',
#     additional_kwargs={}), SystemMessage(content='df_inv, df_price, df_sales', additional_kwargs={}), HumanMessage(
#     content='"top 5 products". I cannot give more details, make assumption if needed.\nPut the final result in `saved_dataframe` variable.',
#     additional_kwargs={})])
# formatted_prompt2 = ([ChatPromptValue(messages=[AIMessage(
#     content='For many years I have helped data scientist to understand executive request. Often they have an idea of what they want but they are not able to express it clearly. I break down the problem into main and sub-steps. More specifically, while making sure what I explain is feasible with the data schema, I explain :\n    - Precise expected output\n    - joins & merges\n    - filters\n    - missing values handling\n    - sort\n\nOnce I have done this, I become a professional python developer. I write python code for each of python step by thinking about the input, the output and execution of each. To help the understanding I break down the different steps into multiple python sub-steps.\nI have worked with python and pandas for more than 20 years. I know all the subtleties and the most recent best practices\nI write clear python code.',
#     additional_kwargs={}), SystemMessage(content='df_inv, df_price, df_sales', additional_kwargs={}), HumanMessage(
#     content='"top 5 products". I cannot give more details, make assumption if needed.\nPut the final result in `saved_dataframe` variable.',
#     additional_kwargs={})])], None)

# res = "Sure, here's some code that should do what you're asking for:\n\n```python\n# merge the three dataframes on the common column 'product_id'\nmerged_df = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# group by product_id and sum the sales\ngrouped_df = merged_df.groupby('product_id').sum()\n\n# sort by sales in descending order and take the top 5 rows\ntop_5 = grouped_df.sort_values('sales', ascending=False).head(5)\n\n# assign the top 5 products to the saved_dataframe variable\nsaved_dataframe = top_5.index.tolist()\n```\n\nThis code assumes that the `df_inv`, `df_price`, and `df_sales` dataframes all have a column called `product_id` that can be used to merge them together. It also assumes that the `df_sales` dataframe has a column called `sales` that represents the amount of sales for each product. If any of these assumptions are incorrect, the code may need to be modified accordingly."

# run = "Sure, here's some code that should do what you're asking for:\n\n```python\n# merge the three dataframes on the common column 'product_id'\nmerged_df = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# group by product_id and sum the sales\ngrouped_df = merged_df.groupby('product_id').sum()\n\n# sort by sales in descending order and take the top 5 rows\ntop_5 = grouped_df.sort_values('sales', ascending=False).head(5)\n\n# assign the top 5 products to the saved_dataframe variable\nsaved_dataframe = top_5.index.tolist()\n```\n\nThis code assumes that the `df_inv`, `df_price`, and `df_sales` dataframes all have a column called `product_id` that can be used to merge them together. It also assumes that the `df_sales` dataframe has a column called `sales` that represents the amount of sales for each product. If any of these assumptions are incorrect, the code may need to be modified accordingly."

# predict = "Sure, here's some code that should do what you're asking for:\n\n```python\n# merge the three dataframes on the common column 'product_id'\nmerged_df = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# group by product_id and sum the sales\ngrouped_df = merged_df.groupby('product_id').sum()\n\n# sort by sales in descending order and take the top 5 rows\ntop_5 = grouped_df.sort_values('sales', ascending=False).head(5)\n\n# assign the top 5 products to the saved_dataframe variable\nsaved_dataframe = top_5.index.tolist()\n```\n\nThis code assumes that the `df_inv`, `df_price`, and `df_sales` dataframes all have a column called `product_id` that can be used to merge them together. It also assumes that the `df_sales` dataframe has a column called `sales` that represents the amount of sales for each product. If any of these assumptions are incorrect, the code may need to be modified accordingly."

# call = {'db_schema': 'df_inv, df_price, df_sales', 'request': 'top 5 products',
#         'python_code_final': "Sure, here's some code that should do what you're asking for:\n\n```python\n# merge the three dataframes on the common column 'product_id'\nmerged_df = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# group by product_id and sum the sales\ngrouped_df = merged_df.groupby('product_id').sum()\n\n# sort by sales in descending order and take the top 5 rows\ntop_5 = grouped_df.sort_values('sales', ascending=False).head(5)\n\n# assign the top 5 products to the saved_dataframe variable\nsaved_dataframe = top_5.index.tolist()\n```\n\nThis code assumes that the `df_inv`, `df_price`, and `df_sales` dataframes all have a column called `product_id` that can be used to merge them together. It also assumes that the `df_sales` dataframe has a column called `sales` that represents the amount of sales for each product. If any of these assumptions are incorrect, the code may need to be modified accordingly."}

# generate = LLMResult(generations=[[ChatGeneration(
#     text="Sure, here's some code that should do what you're asking for:\n\n```python\n# merge the three dataframes on the common column 'product_id'\nmerged_df = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# group by product_id and sum the sales\ngrouped_df = merged_df.groupby('product_id').sum()\n\n# sort by sales in descending order and take the top 5 rows\ntop_5 = grouped_df.sort_values('sales', ascending=False).head(5)\n\n# assign the top 5 products to the saved_dataframe variable\nsaved_dataframe = top_5.index.tolist()\n```\n\nThis code assumes that the `df_inv`, `df_price`, and `df_sales` dataframes all have a column called `product_id` that can be used to merge them together. It also assumes that the `df_sales` dataframe has a column called `sales` that represents the amount of sales for each product. If any of these assumptions are incorrect, the code may need to be modified accordingly.",
#     generation_info=None, message=AIMessage(
#         content="Sure, here's some code that should do what you're asking for:\n\n```python\n# merge the three dataframes on the common column 'product_id'\nmerged_df = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# group by product_id and sum the sales\ngrouped_df = merged_df.groupby('product_id').sum()\n\n# sort by sales in descending order and take the top 5 rows\ntop_5 = grouped_df.sort_values('sales', ascending=False).head(5)\n\n# assign the top 5 products to the saved_dataframe variable\nsaved_dataframe = top_5.index.tolist()\n```\n\nThis code assumes that the `df_inv`, `df_price`, and `df_sales` dataframes all have a column called `product_id` that can be used to merge them together. It also assumes that the `df_sales` dataframe has a column called `sales` that represents the amount of sales for each product. If any of these assumptions are incorrect, the code may need to be modified accordingly.",
#         additional_kwargs={}))]],
#                      llm_output={'token_usage': {'prompt_tokens': 230, 'completion_tokens': 217, 'total_tokens': 447},
#                                  'model_name': 'gpt-3.5-turbo'})
