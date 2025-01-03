from src.models.gpt4_seq1_altair import gpt4_seq1_altair
from src.models.gpt4_seq1_altair_question import gpt4_seq1_altair_question
from src.models.gpt4_seq1_matplotlib import gpt4_seq1_pyplot
from src.models.python_chain_1_gpt4 import python_1_model_gpt4
from src.models.python_chain_1_gpt35 import python_1_model_gpt3
from src.models.python_chain_2_gpt4 import python_2_model_gpt4
from src.models.python_chain_2_gpt35 import python_2_model_gpt3

QUICK_MODEL_NAME = "Python Base"
ACCURATE_MODEL_NAME = "Python Advanced"
QUICK_MODEL_NAME_4 = "Python Base GPT4"
ACCURATE_MODEL_NAME_4 = "Python Advanced GPT4"
PYPLOT_PLOT = "Matplotlib Plot"
ALTAIR_PLOT = "Altair Plot"
ALTAIR_PLOT_QUESTION = "Altair Plot Question"

MAIN_MODEL = "GPT4 Model"
MAIN_MODEL_SA = "GPT3 Model"

all_models = {
    f"{QUICK_MODEL_NAME}": python_1_model_gpt3,
    f"{ACCURATE_MODEL_NAME}": python_2_model_gpt3,
    f"{QUICK_MODEL_NAME_4}": python_1_model_gpt4,
    f"{ACCURATE_MODEL_NAME_4}": python_2_model_gpt4,
    f"{PYPLOT_PLOT}": gpt4_seq1_pyplot,
    f"{ALTAIR_PLOT}": gpt4_seq1_altair,
    f"{ALTAIR_PLOT_QUESTION}": gpt4_seq1_altair_question,
}

models = {
    f"{MAIN_MODEL}": gpt4_seq1_altair_question,
}

# models_sa = {
#     f"{MAIN_MODEL}": any,
# }

models_description = {
    f"{QUICK_MODEL_NAME}": "This model is the fastest. Perfect for simple to medium questions",
    f"{ACCURATE_MODEL_NAME}": "This model is the most accurate. It can handle more complex questions but it is twice "
    "slower than the base model",
    f"{QUICK_MODEL_NAME_4}": "GPT 4 version of the base model.",
    f"{ACCURATE_MODEL_NAME_4}": "GPT 4 version of the advanced model.",
    f"{PYPLOT_PLOT}": "GPT 4 Model using Matplotlib.",
    f"{ALTAIR_PLOT}": "GPT 4 Model using Altair.",
    f"{ALTAIR_PLOT_QUESTION}": "GPT 4 Model able to plot data using Altair and ask questions to clarify",
}

models_description[f"{MAIN_MODEL}"] = models_description[f"{ALTAIR_PLOT_QUESTION}"]


BAYER_PRE_WRITTEN_PROMPTS = {
    "None": "",
    "Top Selling Hint": "What are the top best selling products? sell out = sell in - inventory",
    "Top Selling": "What are the top best selling products?",
    "Top 5": "What are my top 5 products? with id and sell out revenue",
    "Sell Out": "Sell OUT calculation: for each Month x Distributor x Product, Sell_Out_Qty = Sell_In - Inventory_Qty",
    # "Best per Month + info": "What is the best selling product in revenue from sell_out for each month? sell out = sell in - inventory",
    "Best per Month + info": "What is the best selling product in revenue from sell_out for each month? sell out = sell in - inventory_variations",
    "Best per Month": "What is the best selling product in revenue from sell_out for each month?",
    "DoH + info": """DoH Calculation: for each Month x Distributor x Product, DoH = Inventory / avg_of_last_3_month(Sell_Out_Qty * Price)
    info: Sell OUT calculation: for each Month x Distributor x Product, Sell_Out_Qty = Sell_In - Inventory_Qty""",
    "DoH": """DoH Calculation: for each Month x Distributor x Product, DoH = Inventory / avg_of_last_3_month(Sell_Out_Qty * Price)""",
    "sales trends": "Identify trends in product sales to determine which products are selling well and which are not.",
    "price impact on sales": "Analyze the pricing data to determine if any price changes have had a significant impact on sales.",
    "turnover": "Determine the inventory turnover rate by product and distributor to identify which products are selling quickly and which ones are not.",
    "sales trends per distributor": "Identify trends in product sales by distributor to determine which products are selling well and which are not.",
    "selling speed per ditributor": "Compare monthly sell-in and sell-out data to determine which distributors are selling products quickly and which ones are not.",
    "pricing strategy per distributor": "Determine the average price of each product by distributor to evaluate pricing strategies.",
    "Which product/distrib is profitable": "Calculate the profit margins by product and distributor to determine which products and distributors are most profitable.",
}

TIKTOK_PRE_WRITTEN_PROMPTS = {
    "None": "",
    # OK
    "[Question 1] Top Selling": "what are the top best selling products?",
    # OK
    "[Question 2] Top 5 Selling": "what are the top 5 best selling products?",
    # OK
    "[Question 3] Top Selling Per Day": "what is the best selling product in revenue for each day?",

    # Show me the performance of TikTok videos with more than 500k views. among other relevant things show title, creator, views, shares, likes, comments...
    "[Question 4] Top 1 Video Performance": "Show the performance of my top video with multiple indicators over time (views, shares, likes, engagement, shares) on 5 different sub-plots",
    "[Question 5] Top 1 Product Performance": "Show the performance of my top product with multiple indicators over time (sales, revenue, buyers, orders, clicks) on 5 different sub-plots",
    # Perfect
    "[Question 6] Tiktok Performance": "How we perform on Tiktok? Show a performance summary",

    # Perfect
    "[Question 7] GMV on TikTok": "Show me the sources of GMV contribution on TikTok",
    # Perfect
    "[Question 8] Most liked hashtags": "Show the most liked hashtags",
    # ok
    "[Question 9] Top 10 products in livestream": "Show the Top 10 selling products in livestream",

    # "[Question] Last 7 days performance": "Show me the performance videos for last 7 days. And in a line chart?",
    # No
    # "What’s the Indonesia MNY video traffic distribution is like, maybe with a pie chart?": "What’s the Indonesia MNY video traffice distribution is like, maybe with a pie chart?",

    "[Edit Previous Result 1] Sort (altair)": "Order the data. Sort the plot by the most relevant column (the one displayed). Use sort parameter in the encoding function for the axis to be sorted",
    "[Edit Previous Result 2] Filter": "Filter the result to keep only what is important",
    "[Edit Previous Result 3] Bigger": "Make the plot bigger",

}

SALES_PRE_WRITTEN_PROMPTS = {
    "None": "",
    # Basic
    "[Question 1] Revenue per country": "What is the total revenue generated per country?",
    # Cool colored hist with scale
    "[Question 2] Top 10 products": "Show top 10 best-selling (in quantity) products. histogram with quantity as y axis and revenue as color",
    # Bof
    "[Question 3] Revenue vs Quantity": "What is the relationship between revenue and quantity? Show a scatter plot with log scale (omit negative values)",
    #
    # "5. Average unit price / countries": "What is the average unit price of our products, and how does this vary between countries?",
    # Medium
    # 3. super cool colored multilevel hist
    "[Question 4] Sales volume over time": "What is the trend in sales volume over time? Show a histogram per week and day same in the same plot",
    # Cool basic line
    "[Question 5] Unique customers": "How many unique customers do we have and how has this number changed over time? monthly basis",
    #
    # "Products sold per hour": "Are there specific products that sell better at certain times of the day?",
    # "10. Products bought by same customer": "Are there any patterns in the type of products bought by the same customer? Are there opportunities for product bundling?",
    # "11. Products bought together": "Which products are often bought together? Are there cross-selling opportunities?",
    # "12. Customer Retention": "show the buying frequency of customers. and which one are the new ones arriving each month",
    # Common hist but nice finding
    # "Stock for best-selling products": "How much stock should we maintain for our best-selling products?",
    # "14. Qty of product per invoice/ How it varies?": "What is the average quantity of products per invoice? Does this vary by country or over time?",
    # "16. Sales peak / Reasons": "Are there certain times of the year when sales peak? Can we attribute this to certain events or seasons?",
    "[Incomplete Question 1] Evolution": "What is the evolution?",
    "[Incomplete Question 2] Results": "What are the results?",

    "[Edit Previous Result 1] Sort (altair)": "Order the data. Sort the plot by the most relevant column (the one displayed). Use sort parameter in the encoding function for the axis to be sorted",
    "[Edit Previous Result 2] Filter": "Filter the result to keep only what is important",
    "[Edit Previous Result 3] Bigger": "Make the plot bigger",
}

# 1. Boring histogram Work well. Not impressive -> Follow up with reply1. Sort works
# 2. Boring histogram Ok but need to specify what cols we want otherwise it takes either
# 3. Cool but the trend is somewhat
# 4. Boring histogram


def get_pre_written_prompts(data_selected):
    pre_written_prompts = {"None": ""}
    if data_selected == "Sellin and Inventory Data":
        pre_written_prompts = BAYER_PRE_WRITTEN_PROMPTS
    if data_selected == "Tiktok":
        pre_written_prompts = TIKTOK_PRE_WRITTEN_PROMPTS
    if data_selected == "Online Order Data":
        pre_written_prompts = SALES_PRE_WRITTEN_PROMPTS
    return pre_written_prompts
