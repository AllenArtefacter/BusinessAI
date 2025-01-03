import json
import logging
import os
import pickle
from typing import Optional

import pandas as pd

from src.database.csv_data_loader import CSVDataLoader
from src.database.excel_data_loader import ExcelDataLoader
from src.database.mask.dataset_masker import DataMasker, DataTransformer

logging.basicConfig(level=logging.INFO)


class DataLoaderFactory:
    @staticmethod
    def from_folder(
        data_folder, transformers: list[DataTransformer], path_to_data_folder="./"
    ):
        if data_folder is None:
            return None
        folder = os.path.join(path_to_data_folder, data_folder)
        kwargs = {
            "data_folder": data_folder,
            "transformers": transformers,
            "path_to_data_folder": path_to_data_folder,
        }
        file_list = os.listdir(folder)
        for file in file_list:
            if file.lower().endswith(".csv"):
                return CSVDataLoader(**kwargs)
            elif file.lower().endswith(".xlsx") or file.lower().endswith(".xls"):
                return ExcelDataLoader(**kwargs)


if __name__ == '__main__':
    dl = DataLoaderFactory.from_folder(os.path.join('../../', 'res/data/tiktok'), [DataMasker()])