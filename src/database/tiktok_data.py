import logging
import os
from typing import Optional

import pandas as pd

from src.database.config.tiktok.columns_meaning import (
    account_columns,
    campaign_columns,
    live_columns,
    product_columns,
    video_columns,
)
from src.database.config.tiktok.columns_usage import (
    account_columns_usage,
    campaign_columns_usage,
    live_columns_usage,
    product_columns_usage,
    video_columns_usage,
)
from src.database.factory_data_loader import DataLoaderFactory
from src.database.mask.dataset_masker import DataMasker, DataTransformer
from src.tools.prompting import db_schema_generation

tables_files: list[str] = [
    "account_daily.csv",
    "campaign_daily.csv",
    "livestream_daily.csv",
    "product_daily.csv",
    "video_daily.csv",
]

related_columns_meaning: dict[str, dict] = {
    "account_daily": account_columns,
    "campaign_daily": campaign_columns,
    "livestream_daily": live_columns,
    "product_daily": product_columns,
    "video_daily": video_columns,
}

columns_config: [dict[dict[str, str]]] = {
    "account_daily": account_columns_usage,
    "campaign_daily": campaign_columns_usage,
    "livestream_daily": live_columns_usage,
    "product_daily": product_columns_usage,
    "video_daily": video_columns_usage,
}

default_tables_selection: list[str] = [
    "account_daily",
    "campaign_daily",
    "livestream_daily",
    "product_daily",
    "video_daily",
]


if __name__ == "__main__":
    # Check columns are the same
    assert set(video_columns) == set(video_columns_usage)
    assert set(live_columns) == set(live_columns_usage)
    assert set(product_columns) == set(product_columns_usage)
    assert set(account_columns) == set(account_columns_usage)
    assert set(campaign_columns) == set(campaign_columns_usage)

    path_to_data_folder = "./res/data"

    dl = DataLoaderFactory.from_folder("Tiktok", [DataMasker()], path_to_data_folder)
    dataframes = dl.data
    transformed_dataframes = dl.transformed_data
    related_columns_meaning = dl.columns_config
    default_tables_selection = list(transformed_dataframes.keys())

    db_schema = db_schema_generation(transformed_dataframes, related_columns_meaning)
    print("db_schema", db_schema)
