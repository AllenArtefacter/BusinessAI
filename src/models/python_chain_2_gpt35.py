import logging

from langchain import ConversationChain, LLMChain, PromptTemplate
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
    human_get_python_from_steps,
    human_rephrase_raw,
    ia_python_expert,
    ia_rephrase_detailed,
    system_message_prompt,
)

formatter = logging.Formatter("%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)

rephrase_chain = LLMChain(
    llm=llm_chat_gpt4,
    prompt=ChatPromptTemplate.from_messages(
        [ia_rephrase_detailed, system_message_prompt, human_rephrase_raw]
    ),
    output_key="rephrased_request",
    verbose=True,
)

write_python_chain = LLMChain(
    llm=llm_chat_gpt4,
    prompt=ChatPromptTemplate.from_messages(
        [
            ia_python_expert,
            system_message_prompt,
            human_get_python_from_steps,
        ]
    ),
    output_key="python_code_final",
    verbose=True,
)

python_2_model_gpt3 = SequentialChain(
    chains=[rephrase_chain, write_python_chain],
    input_variables=["request", "db_schema"],
    output_variables=["python_code_final", "rephrased_request"],
    verbose=True,
    return_all=True,
)

if __name__ == "__main__":
    formatted_prompt = python_2_model_gpt3.prep_inputs(
        {"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"}
    )
    # print(f"{overall_chain_2.llm=}")
    print(f"{formatted_prompt=}")

    res = python_2_model_gpt3.run(
        {"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"}
    )
    run = python_2_model_gpt3.run(
        **{"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"}
    )
    call = python_2_model_gpt3.__call__(
        {"db_schema": "df_inv, df_price, df_sales", "request": "top 5 products"}
    )

    print(f"{res=}")
    print(f"{run=}")
    print(f"{call=}")

res = "Sure, here's the updated code to store the top 5 products by sales revenue in the `saved_dataframe` variable:\n\n```\n# Step 2: Join the dataframes\ndf = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# Step 3: Aggregate the data by product ID\ndf_agg = df.groupby('product_id').agg({'revenue': 'sum'})\n\n# Step 4: Sort the data in descending order by sales revenue and select the top 5 rows\ndf_top5 = df_agg.sort_values('revenue', ascending=False).head(5)\n\n# Step 5: Store the results in the saved_dataframe variable\nsaved_dataframe = df_top5\n```\n\nThis code will join the three dataframes on the `product_id` column, aggregate the data by product ID to get the total sales revenue for each product, sort the data in descending order by sales revenue, select the top 5 rows, and store the results in the `saved_dataframe` variable."
run = "Sure, here's the updated code to store the top 5 products by sales revenue in the `saved_dataframe` variable:\n\n```\n# Step 1: Define \"top\" as top 5 products by sales revenue\n# Step 2: Join the dataframes together on product ID\ndf = df_inv.merge(df_price, on='product_id').merge(df_sales, on='product_id')\n\n# Step 3: Aggregate the data by product ID to get total sales revenue\ndf_agg = df.groupby('product_id')['revenue'].sum().reset_index()\n\n# Step 4: Sort the data in descending order by sales revenue and select top 5 rows\ndf_top5 = df_agg.sort_values('revenue', ascending=False).head(5)\n\n# Step 5: Store the results in the saved_dataframe variable\nsaved_dataframe = df_top5\n```\n\nThis code will give you the top 5 products by sales revenue, stored in the `saved_dataframe` variable."
call = {
    "db_schema": "df_inv, df_price, df_sales",
    "request": "top 5 products",
    "python_code_final": "Sure, here's the code to perform the steps and store the final result in `saved_dataframe` variable:\n\n```python\n# Step 1: Define the metric for \"top\"\nmetric = 'sales revenue'\n\n# Step 2: Join the dataframes on a common key\ndf = pd.merge(df_inv, df_price, on='product ID')\ndf = pd.merge(df, df_sales, on='product ID')\n\n# Step 3: Aggregate the data by product ID to get the total sales revenue\ndf_agg = df.groupby('product ID').agg({'sales revenue': 'sum'})\n\n# Step 4: Sort the data in descending order by sales revenue and select the top 5 rows\ndf_top = df_agg.sort_values(by='sales revenue', ascending=False).head(5)\n\n# Step 5: Display the results in a table or chart\nsaved_dataframe = df_top\n```\n\nNote that you can change the `metric` variable to any other metric you want to use for determining the \"top\" products. Also, you can modify the `head(5)` method to select a different number of top products.",
}

# formatted_prompt={'db_schema': 'df_inv, df_price, df_sales', 'request': 'top 5 products'}
