import os

import pandas as pd

from src.database.config.bayer_demo.columns_meaning import (
    inventory_columns,
    product_price_columns,
    sell_in_columns,
    sell_out_columns,
)
from src.database.config.bayer_demo.columns_usage import (
    inventory_columns_usage,
    product_price_columns_usage,
    sell_in_columns_usage,
    sell_out_columns_usage,
)
from src.database.factory_data_loader import DataLoaderFactory
from src.database.mask.dataset_masker import DataFilter, DataMasker
from src.tools.prompting import db_schema_generation

# columns, descriptions, tables, default_tables_selection = get_bayer_data()

data_dir = "res/data/bayer"

tables_files = [
    "Inventory.csv",
    "Product_Price.csv",
    "Sell_In.csv",
    "_Sell_Out.csv",  # '_' Because the goal is not to use it.
]

dataframe_names = [
    "inventory_df",
    "product_price_df",
    "sell_in_df",
    "sell_out_df",
]

default_tables_selection = [
    "inventory_df",
    "product_price_df",
    "sell_in_df",
]

related_columns_meaning = {
    "inventory_df": inventory_columns,
    "product_price_df": product_price_columns,
    "sell_in_df": sell_in_columns,
    "sell_out_df": sell_out_columns,
}

columns_config = {
    "inventory_df": inventory_columns_usage,
    "product_price_df": product_price_columns_usage,
    "sell_in_df": sell_in_columns_usage,
    "sell_out_df": sell_out_columns_usage,
}


def get_b_data(path_to_root="./"):
    dataframes = {}
    columns = {}
    description = {}

    for table_file, dataframe_name in zip(tables_files, dataframe_names):
        dataframes[dataframe_name] = pd.read_csv(
            os.path.join(path_to_root, data_dir, table_file)
        )

    for dataframe_name, table in dataframes.items():
        columns[dataframe_name] = list(table.columns)

    masker = DataMasker()

    masked_dataframes = masker.__map_mask(dataframes, columns_config, inplace=False)

    return (
        dataframes,
        masked_dataframes,
        related_columns_meaning,
        default_tables_selection,
    )


if __name__ == "__main__":
    path_to_data_folder = "../../res/data"

    dl = DataLoaderFactory.from_folder(
        "bayer_demo", [DataMasker(), DataFilter()], path_to_data_folder
    )
    dataframes = dl.data
    transformed_dataframes = dl.transformed_data
    related_columns_meaning = dl.columns_config
    default_tables_selection = list(dataframes.keys())

    db_schema = db_schema_generation(transformed_dataframes, related_columns_meaning)
    print("db_schema", db_schema)
