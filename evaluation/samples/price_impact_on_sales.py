# To analyze the impact of price changes on sales, we can calculate the percentage change in price and sell_in_qty for each product and distributor, and then compare these values to see if there is any correlation between them. We will first merge the dataframes and then calculate the percentage changes.


import pandas as pd

# Merge the dataframes
merged_df = pd.merge(
    inventory_df, product_price_df, on=["Month", "Distributor", "ProductID"]
)
merged_df = pd.merge(merged_df, sell_in_df, on=["Month", "Distributor", "ProductID"])

# Calculate the percentage change in price and sell_in_qty
merged_df["Price_pct_change"] = merged_df.groupby(["Distributor", "ProductID"])[
    "Price"
].pct_change()
merged_df["Sell_In_Qty_pct_change"] = merged_df.groupby(["Distributor", "ProductID"])[
    "Sell_In_Qty"
].pct_change()

# Drop rows with missing values (first row for each group will have NaN due to pct_change)
merged_df.dropna(subset=["Price_pct_change", "Sell_In_Qty_pct_change"], inplace=True)

# Calculate the correlation between price changes and sell_in_qty changes
correlation = merged_df["Price_pct_change"].corr(merged_df["Sell_In_Qty_pct_change"])

saved_dataframe = {"correlation": correlation, "data": merged_df}
# The saved_dataframe variable will contain the correlation value between price changes and sell_in_qty changes, as well as the merged dataframe with percentage change columns. A positive correlation value indicates that price increases are associated with increased sales, while a negative correlation value indicates that price increases are associated with decreased sales. A correlation value close to 0 indicates that there is no significant relationship between price changes and sales changes.


# fake_ia_message_rephrase = AIMessagePromptTemplate(
#     prompt=PromptTemplate(
#         template="""I am a data-scientist having more than 10 years of experience.
# I understand your needs and complete your requests using python pandas.""",
#         input_variables=[],
#     )
# )
#
# human_message_prompt = HumanMessagePromptTemplate(
#     prompt=PromptTemplate(
#         template="""I want {request}. I cannot give more details, make assumption if needed.
# Put the final result in `saved_dataframe` variable.""",
#         input_variables=["request"],
#     )
# )
#
# chat_prompt = ChatPromptTemplate.from_messages(
#     [fake_ia_message_rephrase, system_message_prompt, human_message_prompt]
# )
#
# chat = ChatOpenAI(
#     temperature=0,
#     model_name="gpt-4",
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0
# )
