import os
import random
from datetime import datetime
from itertools import product

import pandas as pd
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from faker import Faker

from src.database.old.pymysql_wrapper import MySQLWrapper

fake = Faker()
fake.seed_instance(0)


def generate_data(nb_months=48):
    start_date = datetime(2016, 1, 1)

    sell_in_data = []
    sell_out_data = []
    inventory_data = []
    product_price_data = []

    fake.name()

    distributors = [fake.company() for _ in range(5)]
    product_ids = [fake.ean(length=8) for _ in range(10)]

    inventory_qty = 0
    for distributor, product_id, month in product(
        distributors, product_ids, range(nb_months)
    ):
        if month == 0:
            inventory_qty = 0
        month = start_date + relativedelta(months=month)

        sell_in_qty = inventory_qty + random.randint(500, 1000)
        sell_out_qty = random.randint(50, sell_in_qty)
        inventory_qty = sell_in_qty - sell_out_qty

        price = round(random.uniform(20, 80), 2)

        sell_in_data.append((month, distributor, product_id, sell_in_qty))
        sell_out_data.append((month, distributor, product_id, sell_out_qty))
        inventory_data.append((month, distributor, product_id, inventory_qty))
        product_price_data.append((month, distributor, product_id, price))
        print(sell_in_qty)

    sell_in_df = pd.DataFrame(
        sell_in_data, columns=["Month", "Distributor", "ProductID", "Sell_In_Qty"]
    )
    sell_out_df = pd.DataFrame(
        sell_out_data, columns=["Month", "Distributor", "ProductID", "Sell_Out_Qty"]
    )
    inventory_df = pd.DataFrame(
        inventory_data,
        columns=["Month", "Distributor", "ProductID", "Inventory_Qty"],
    )
    product_price_df = pd.DataFrame(
        product_price_data, columns=["Month", "Distributor", "ProductID", "Price"]
    )

    return sell_in_df, sell_out_df, inventory_df, product_price_df


if __name__ == "__main__":
    env_path = "./credentials.env"
    load_dotenv(dotenv_path=env_path)

    wrapper = MySQLWrapper(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )

    if not wrapper.connection:
        print("Connection failed.")

    sell_in_df, sell_out_df, inventory_df, product_price_df = generate_data()
