import json
import logging
import os
import pickle
from typing import Optional

import pandas as pd

from src.database.data_loader import DataLoader
from src.database.mask.dataset_masker import DataMasker, DataTransformer

logging.basicConfig(level=logging.INFO)


class CSVDataLoader(DataLoader):
    def __init__(
        self, data_folder, transformers: list[DataTransformer], path_to_data_folder="./"
    ):
        super().__init__(data_folder, transformers, path_to_data_folder)

    def get_files(self) -> list[str]:
        folder = os.path.join(self.path_to_data_folder, self.data_folder)
        files = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]
        return files

    def load(self):
        self.load_csv()
        super().load()

    def load_csv(self):
        dataframe_names = [
            f"{f.lower().replace(' ', '').replace('.csv', '')}_df"
            for f in self.file_names
        ]

        self._data = {}
        for table_file, dataframe_name in zip(self.file_names, dataframe_names):
            logging.info(f"reading {table_file}")
            data = pd.read_csv(
                os.path.join(self.path_to_data_folder, self.data_folder, table_file),
                sep=None,
                engine="python",
            )
            logging.info(f"reading {table_file} ok")

            # Remove columns with only null values
            data = data.dropna(axis=1, how="all")
            self._data[dataframe_name] = data

        logging.info("reading csv ok")

