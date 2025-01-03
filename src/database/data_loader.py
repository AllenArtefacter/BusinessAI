import json
import logging
import os
import pickle
from typing import Optional

import pandas as pd

from src.database.mask.dataset_masker import DataMasker, DataTransformer

logging.basicConfig(level=logging.INFO)


def load_json(path):
    data = None
    try:
        with open(path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.warning(f"[load_json] file {path} not found.")
    finally:
        return data


def pickle_save(path: str, data: object):
    with open(path, "wb") as file:
        pickle.dump(data, file)


def pickle_load(path) -> Optional[object]:
    try:
        with open(path, "rb") as file:
            data = pickle.load(file)
    except FileNotFoundError:
        return None
    return data


class DataLoader:
    def __init__(
        self,
        data_folder,
        transformers: list[DataTransformer],
        path_to_data_folder="./",
        force_transform=False,
    ):
        logging.info(f"DataLoader initializing with data_folder={data_folder}")
        self.path_to_data_folder = path_to_data_folder
        self.data_folder = data_folder
        self.transformers = transformers
        self.columns_usage_json_file_name = self.get_cm_json_file_name()
        self.descriptions_json_file_name = self.get_descriptions_json_file_name()

        self._data: Optional[dict[str, pd.DataFrame]] = None
        self._transformed_data: Optional[dict[str, pd.DataFrame]] = None

        # dict[dict[str, str]] is fore Table -> Col -> Details
        self._columns_config: Optional[dict[str, dict[str, str]]] = None
        self._descriptions: Optional[dict[str, dict[str, str]]] = None

        self.transformed_data_path = os.path.join(
            self.path_to_data_folder, self.data_folder, "transformed.pkl"
        )
        logging.info(f"Transformed data path: {self.transformed_data_path}")
        self.file_names = self.get_files()
        logging.info(f"Files found: {self.file_names}. Loading...")
        self.load()
        logging.info(
            f"Loaded {self.data_folder} with {len(self.data)} tables. Transforming..."
        )
        self.transform(force_transform=force_transform)
        logging.info(
            f"Transformed {self.data_folder} with {len(self.transformed_data)} tables."
        )
        self.load_gen_descriptions()

    def get_files(self):
        raise NotImplementedError

    @property
    def descriptions(self) -> Optional[dict[str, dict[str, str]]]:
        if self._descriptions is None:
            self.load_gen_descriptions()

        return self._descriptions

    @property
    def columns_config(self) -> Optional[dict[str, dict[str, str]]]:
        if self._columns_config is None:
            self.load_rel_col_usage()

        return self._columns_config

    def load_gen_descriptions(self):
        if self._descriptions is None:
            self._descriptions = load_json(path=self.descriptions_json_file_name)

        if self._descriptions is None:
            self._descriptions = {}
            for table_name, table in self.data.items():
                self._descriptions[table_name] = {}
                for col_name, col in table.items():
                    self._descriptions[table_name][col_name] = ""

    def load_rel_col_usage(self):
        if self._columns_config is None:
            self._columns_config = load_json(path=self.columns_usage_json_file_name)
        if self._columns_config is None:
            self._columns_config = {}
            for table_name, table in self.data.items():
                self._columns_config[table_name] = {}
                for col_name, col in table.items():
                    self._columns_config[table_name][col_name] = "ok"

    @descriptions.setter
    def descriptions(self, value):
        self._descriptions = value
        self.save_descriptions()

    def update_config(self, table_name, col_name, new_conf):
        self.columns_config[table_name][col_name] = new_conf
        self._transformed_data = {
            name: data.copy() for name, data in self._data.items()
        }

        for transformer in self.transformers:
            transformer.transform_on_col_update(
                self._transformed_data,
                self.columns_config,
                table_name,
                col_name,
                inplace=True,
            )

        self.save_rel_col_usage()
        self.save_transformed_data()

    def save_descriptions(self):
        with open(self.descriptions_json_file_name, "w") as file:
            json.dump(self._descriptions, file)

    def save_rel_col_usage(self):
        with open(self.columns_usage_json_file_name, "w") as file:
            json.dump(self._columns_config, file)

    def load(self):  # Implement in child and then call the parent one
        self.load_transformed_data()

        if not self._data:
            logging.error("Data not loaded")
        if not self.columns_config:
            logging.error("Columns details not loaded")
        if not self._transformed_data:
            logging.info(
                "Transformed data was not found: it is going to be lazy generated"
            )

    @property
    def transformed_data(self) -> Optional[dict[str, pd.DataFrame]]:
        if self.data is None:
            logging.error(
                "Data is not imported, the transformed version is not available"
            )
            return None

        if self._transformed_data is None:
            self.transform()
        return self._transformed_data

    @property
    def data(self) -> Optional[dict[str, pd.DataFrame]]:
        return self._data

    def transform(self, force_transform=False, save=True, force_save=False):
        if self.data is None:
            logging.error(
                "Data is not imported, the transformed version is not available"
            )
            return

        if not self._transformed_data or force_transform:
            self._transform_data()
            if save:
                self.save_transformed_data()
        if force_save:
            self.save_transformed_data()

    def _transform_data(self):
        self._transformed_data = {
            name: data.copy() for name, data in self._data.items()
        }
        for transformer in self.transformers:
            transformer.transform(
                self._transformed_data, self.columns_config, inplace=True
            )

    def get_cm_json_file_name(self):
        """Throw an error if the file is not in os.path.join(self.path_to_data_folder, self.data_folder)"""
        return os.path.join(self.path_to_data_folder, self.data_folder, "details.json")

    def get_descriptions_json_file_name(self):
        return os.path.join(
            self.path_to_data_folder, self.data_folder, "descriptions.json"
        )

    def save_transformed_data(self):
        if self.transformed_data is None:
            logging.error(
                "Data is not imported, the transformed version is not available"
            )
            return None

        pickle_save(path=self.transformed_data_path, data=self._transformed_data)

    def load_transformed_data(self):
        logging.info(f"Loading transformed data from {self.transformed_data_path}")
        self._transformed_data = pickle_load(path=self.transformed_data_path)
        logging.info(f"Loaded transformed tables")
