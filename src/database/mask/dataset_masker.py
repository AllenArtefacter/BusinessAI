import logging
import random
import re
import string
from collections import defaultdict
from typing import Callable, Optional, Tuple

import pandas as pd
import trrex as tx
from faker import Faker
from tqdm import tqdm

tqdm.pandas(desc="Processing")

LIMIT_FORCE_NEW = 100


def count_words(text: str) -> int:
    return len(p_words(text))


def p_words(text: str) -> list:
    return re.findall(r"\w+", text)


possibles_configs = {
    "ok",
    "mask_any",
    "mask_any_words",
    "mask_company",
    "mask_name",
    "mask_id",
    "drop",
}


class DataTransformer:  # TODO make this abstract
    def __init__(self):
        pass

    def transform(
        self,
        dataframes: dict[str, pd.DataFrame],
        columns_config: dict[str, dict[str, str]],
        inplace=False,
    ):
        raise NotImplementedError("This has to be implemented in child classes")

    def transform_on_col_update(
        self,
        original_dataframes: dict[str, pd.DataFrame],
        columns_config: dict[str, dict[str, str]],
        table_name: str,
        col_name: str,
        inplace=False,
    ):
        raise NotImplementedError("This has to be implemented in child classes")


class MaskingSets:
    def __init__(self, sets=None):
        if sets is None:
            sets = defaultdict(set)
        self.masking_sets = sets
        self.ordered_set = [
            "mask_id",
            "mask_company",
            "mask_name",
            "mask_any_words",
            "mask_any",
        ]

    def update_usage(self, dataframe, columns_config):
        to_add_usage_sets = MaskingSets.gen_masking_sets(
            dataframe, masking_details=columns_config
        )
        for _type in to_add_usage_sets:
            if _type not in self.masking_sets:
                self.masking_sets[_type] = set()
            self.masking_sets[_type].update(to_add_usage_sets[_type])

    def __str__(self):
        return str(self.masking_sets)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for _type in self.ordered_set:
            if _type not in self.masking_sets:
                continue
            yield _type, self.masking_sets[_type]

    def keys(self):
        return self.masking_sets.keys()

    def values(self):
        return self.masking_sets.values()

    @staticmethod
    def gen_masking_sets(datasets, masking_details: dict[str, dict[str, str]]):
        masking_sets = defaultdict(set)

        # Parse datasets and sort words into appropriate sets
        for dataset_name, table in datasets.items():
            masking_details_df = masking_details[dataset_name]
            for column in table:
                masking_details_col = masking_details_df[column]
                if masking_details_col.startswith("mask"):
                    masking_sets[masking_details_col].update(
                        set(table[column][table[column].notna()].to_list())
                    )

        return masking_sets

    @classmethod
    def from_dataframes(cls, dataframes, masking_details):
        return cls(cls.gen_masking_sets(dataframes, masking_details))

    @classmethod
    def from_col_usage(cls, col, usage):
        if usage.startswith("mask"):
            return cls({usage: set(col[col.notna()].to_list())})
        return cls({})

    @classmethod
    def from_dict(cls, param):
        raise NotImplementedError


class WordMapping:
    def __init__(self, word_mapping: Optional[dict] = None):
        if word_mapping is None:
            word_mapping = {}
        self.word_mapping: dict = word_mapping

        self.regex_word_mapping = {}
        self.placeholder_mapping = {}
        self.regex_word_mapping_no_regex = {}
        self.placeholder_mapping_no_regex = {}

        self.reversed_word_mapping = {}

        self.reversed_regex_word_mapping = {}
        self.reversed_regex_word_mapping_no_regex = {}
        self.reversed_placeholder_mapping = {}
        self.reversed_placeholder_mapping_no_regex = {}

    @staticmethod
    def generate_mask_from_type_count(
        _type: str, count: int, force_new=False, word_lengths=None
    ) -> list:
        def force_any(count_):
            return [
                "".join(random.choices(string.ascii_letters, k=word_length))
                for word_length in [random.randint(5, 8) for _ in range(count_)]
            ]

        def generate_fake_words(count_: int, word_gen_func: Callable):
            words = []
            while len(words) < count_:
                words += p_words(word_gen_func())
            return words[:count_]

        maskers_force_true = {
            "mask_id": lambda: [
                str(random.randint(10 ** ((c * 4) - 1), 10 ** (c * 4) - 1))
                for c in word_lengths
            ],
            "mask_company": lambda: force_any(count),
            "mask_name": lambda: force_any(count),
            "mask_any": lambda: force_any(count),
            "mask_any_words": lambda: force_any(count),
        }

        maskers_force_false = {
            "mask_id": lambda: [
                str(random.randint(10 ** (c - 1), 10**c - 1) for c in word_lengths)
            ],
            "mask_company": lambda: generate_fake_words(count, DataMasker.fake.company),
            "mask_name": lambda: generate_fake_words(count, DataMasker.fake.name),
            "mask_any": lambda: [DataMasker.fake.word() for _ in range(count)]
            if count <= 3
            else DataMasker.fake.sentence(count, variable_nb_words=False).split(" "),
            "mask_any_words": lambda: [DataMasker.fake.word() for _ in range(count)],
        }

        maskers = maskers_force_true if force_new else maskers_force_false

        if _type not in maskers:
            raise ValueError(f"Unknown type {_type}")

        res = maskers[_type]()
        if any([a for a in res if a == " "]):
            print(f"WARNING: space in mask {_type}", res)
        return res

    @classmethod
    def from_masking_sets(cls, usage_sets: MaskingSets, word_mapping: dict = None):
        return cls(
            WordMapping.create_word_mapping_from_usage_sets_(usage_sets, word_mapping)
        )

    @staticmethod
    def create_word_mapping_from_usage_sets_(
        usage_sets: MaskingSets, word_mapping: dict = None
    ) -> dict[str, str]:
        if word_mapping is None:
            word_mapping = dict()

        print("Sets are", usage_sets.keys())

        assert (
            len(set(usage_sets.keys()) - set(usage_sets.ordered_set)) == 0
        ), f"unknown type {set(usage_sets.keys()) - set(usage_sets.ordered_set)}"
        force_new = [False]  # not so clean

        def mask(words: str):
            i = 0
            if not isinstance(words, str):
                words = str(words)
                logging.warning(f"words is not a str words:{words}")

            words_list = p_words(words)
            words_len = len(words_list)

            while len([word for word in words_list if word not in word_mapping]):
                i += 1
                if not force_new[0] and i > LIMIT_FORCE_NEW:
                    force_new[0] = True

                new_words: list = WordMapping.generate_mask_from_type_count(
                    _type,
                    words_len,
                    force_new=force_new[0],
                    word_lengths=[len(word) for word in words_list]
                    if _type == "mask_id"
                    else None,
                )
                for word, new_word in zip(words_list, new_words):
                    if (
                        word not in word_mapping
                        and new_word not in word_mapping.values()
                        and word != new_word
                    ):
                        word_mapping[word] = new_word

        # Run over all sets and create the mapping
        for _type, _set in usage_sets:
            force_new[0] = False
            tqdm.pandas(
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}, iter={n}] Creating word mapping for "
                + _type
            )
            pd.Series(list(_set)).progress_apply(mask)

        return word_mapping

    @staticmethod
    def get_regex_word_mapping(word_mapping: dict):
        regex_word_mapping_no_regex = {}
        regex_word_mapping = {}
        placeholder_mapping_no_regex = {}
        placeholder_mapping = {}
        for i, (word, replacement) in enumerate(word_mapping.items()):
            placeholder = f"__PLACEHOLDER{i}__"
            regex_word_mapping[f"\\b{word}\\b"] = placeholder
            regex_word_mapping_no_regex[word] = placeholder
            placeholder_mapping[f"\\b{placeholder}\\b"] = replacement
            placeholder_mapping_no_regex[placeholder] = replacement

        return (
            regex_word_mapping,
            regex_word_mapping_no_regex,
            placeholder_mapping,
            placeholder_mapping_no_regex,
        )

    def __create_word_mapping_from_usage_sets(self, usage_sets: MaskingSets):
        # from static to oo
        self.word_mapping = WordMapping.create_word_mapping_from_usage_sets_(
            usage_sets, self.word_mapping
        )

    def __create_reverse_mapping(self):
        # reverse mapping
        self.reversed_word_mapping = {v: k for k, v in self.word_mapping.items()}
        (
            self.reversed_regex_word_mapping,
            self.reversed_regex_word_mapping_no_regex,
            self.reversed_placeholder_mapping,
            self.reversed_placeholder_mapping_no_regex,
        ) = WordMapping.get_regex_word_mapping(self.reversed_word_mapping)

    def update_ignore(self, usage_sets: MaskingSets):
        """
        Update word mapping, if word already in the mapping will be ignored
        """
        self.__create_word_mapping_from_usage_sets(usage_sets)
        (
            self.regex_word_mapping,
            self.regex_word_mapping_no_regex,
            self.placeholder_mapping,
            self.placeholder_mapping_no_regex,
        ) = WordMapping.get_regex_word_mapping(self.word_mapping)

        # reverse mapping
        self.__create_reverse_mapping()

    def update_replace(self, updated_usage_sets: MaskingSets):
        """
        Update word mapping, if word already in the mapping will be replaced
        """
        for _type, _set in updated_usage_sets:
            for words in _set:
                for word in p_words(str(words)):
                    if word in self.word_mapping:
                        del self.word_mapping[word]

        self.update_ignore(updated_usage_sets)

    @classmethod
    def from_dict(cls, param):
        raise NotImplementedError

    def is_empty(self) -> bool:
        return len(self.word_mapping) == 0


class DataMasker(DataTransformer):
    fake = Faker()
    fake.seed_instance(42)

    def __init__(self):
        super().__init__()
        self.masking_sets = MaskingSets()
        self.word_mapping = WordMapping()

    def __dict__(self):
        return {
            "usage_sets": self.masking_sets,
            "word_mapping": self.word_mapping,
        }

    def export(self, path):
        self.export_as_json(path)

    def export_as_pkl(self, path):
        raise NotImplementedError

    def export_as_json(self, path):
        import json

        with open(path, "w") as f:
            json.dump(self.__dict__(), f)

    @classmethod
    def from_json(cls, path):
        import json

        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data):
        masker = cls()
        masker.masking_sets = MaskingSets.from_dict(data["usage_sets"])
        masker.word_mapping = WordMapping.from_dict(data["word_mapping"])
        return masker

    @staticmethod
    def apply_word_mapping(
        series: pd.Series,
        regex_word_mapping: dict,
        regex_word_mapping_no_regex: dict,
        placeholder_mapping: dict,
        placeholder_mapping_no_regex: dict,
    ):
        def fast_replace(d, d_no_regex, s):
            pattern = tx.make(list(d.keys()), suffix="", prefix="")

            def replacer(match):
                return d_no_regex.get(match.group(), "ERROR")

            return s.str.replace(pattern, replacer, regex=True)

        if pd.api.types.is_string_dtype(series):
            series = fast_replace(
                regex_word_mapping, regex_word_mapping_no_regex, series
            )
            series = fast_replace(
                placeholder_mapping, placeholder_mapping_no_regex, series
            )

        return series

    def transform(
        self,
        dataframes: dict[str, pd.DataFrame],
        columns_config: Optional[dict[str, dict[str, str]]],
        inplace=False,
    ):
        if not inplace:
            dataframes = {
                name: dataframe.copy() for name, dataframe in dataframes.items()
            }
        if columns_config is None:
            logging.info("No related columns usage, skipping masking")
            return dataframes

        return self.__map_mask(dataframes, columns_config)

    def transform_on_col_update(
        self,
        original_dataframes: dict[str, pd.DataFrame],
        columns_config: Optional[dict[str, dict[str, str]]],
        table_name: str,
        col_name: str,
        inplace=False,
    ):
        if self.word_mapping.is_empty():
            return self.transform(
                dataframes=original_dataframes,
                columns_config=columns_config,
                inplace=inplace,
            )

        dataframes = original_dataframes
        if not inplace:
            dataframes = {
                name: dataframe.copy() for name, dataframe in dataframes.items()
            }
        if columns_config is None:
            logging.info("No related columns usage, skipping masking")
            return dataframes

        df = dataframes[table_name]
        usage = columns_config[table_name][col_name]

        # Create the set related to this column
        self.masking_sets = MaskingSets.from_dataframes(dataframes, columns_config)
        tmp_usage_set = MaskingSets().from_col_usage(df[col_name], usage)

        # Update the word mapping
        self.word_mapping.update_replace(tmp_usage_set)

        # Mask the data
        # self.mask_col(df, col_name, usage)

        # Re Mask the entire df (should depend on the changes) # FIXME
        self.mask(dataframes, columns_config)

        return dataframes

    def mask_col(self, df, column, usage):
        if usage.startswith("mask"):
            df[column] = self.apply_word_mapping(
                df[column].astype(str),
                self.word_mapping.regex_word_mapping,
                self.word_mapping.regex_word_mapping_no_regex,
                self.word_mapping.placeholder_mapping,
                self.word_mapping.placeholder_mapping_no_regex,
            )

    def __map_mask(
        self,
        dataframes: dict[str, pd.DataFrame],
        columns_config: Optional[dict[str, dict[str, str]]],
    ):
        self.create_mappings(dataframes, columns_config)
        self.mask(dataframes, columns_config)

        return dataframes

    def mask(self, dataframes: dict[str, pd.DataFrame], columns_config):
        original_dtypes = [original_df.dtypes for original_df in dataframes.values()]

        for dataframe_name in list(dataframes.keys()):
            df = dataframes[dataframe_name]
            for col, usage in tqdm(
                columns_config[dataframe_name].items(), desc=dataframe_name
            ):
                self.mask_col(df, col, usage)

        for dtypes, masked_df in zip(original_dtypes, dataframes.values()):
            for col in masked_df.columns:
                try:
                    masked_df[col] = masked_df[col].astype(dtypes[col])
                except ValueError:
                    logging.error(f"Could not convert {col} to {dtypes[col]}")

    def unmask_str(self, string_: str):
        return DataMasker.apply_word_mapping(
            pd.Series([string_]),
            self.word_mapping.reversed_regex_word_mapping,
            self.word_mapping.reversed_regex_word_mapping_no_regex,
            self.word_mapping.reversed_placeholder_mapping,
            self.word_mapping.reversed_placeholder_mapping_no_regex,
        )[0]

    def mask_new_str(self, string_: str):
        # check if we have a mapping for these p_words(word)
        # if not, create a new mapping
        dataframes = {"tmp_df": pd.DataFrame({"tmp": [string_]})}
        columns_config = {"tmp_df": {"tmp": "mask_any"}}

        if len(
            [
                word
                for word in p_words(string_)
                if word not in self.word_mapping.word_mapping
            ]
        ):
            self.add_mappings(dataframes, columns_config)

        self.mask(dataframes, columns_config)
        return dataframes["tmp_df"]["tmp"].iloc[0]

    def create_mappings(
        self,
        dataframes: dict[str, pd.DataFrame],
        columns_config: dict[str, dict[str, str]],
    ):
        self.masking_sets = MaskingSets.from_dataframes(
            dataframes, masking_details=columns_config
        )
        self.word_mapping.update_ignore(self.masking_sets)

    def add_mappings(self, dataframes: dict[str, pd.DataFrame], columns_config):
        self.masking_sets.update_usage(dataframes, columns_config)
        tmp_to_add_usage_sets = MaskingSets.from_dataframes(
            dataframes, masking_details=columns_config
        )
        self.word_mapping.update_ignore(tmp_to_add_usage_sets)

    def save(self):
        pass  # TODO

    def load(self):
        pass  # TODO


class DataFilter(DataTransformer):
    def __init__(self):
        super().__init__()
        self.dropped_columns = []

    def transform(
        self,
        dataframes: dict[str, pd.DataFrame],
        columns_config: Optional[dict[str, dict[str, str]]],
        inplace=False,
    ):
        return self.drop_cols(dataframes, columns_config, inplace)

    def transform_on_col_update(
        self,
        original_dataframes: dict[str, pd.DataFrame],
        columns_config: dict[str, dict[str, str]],
        table_name: str,
        col_name: str,
        inplace=False,
    ):
        return self.transform(original_dataframes, columns_config, inplace)

    def drop_cols(
        self, dataframes: dict[str, pd.DataFrame], columns_config, inplace=False
    ):
        if not inplace:
            dataframes = {
                name: dataframe.copy() for name, dataframe in dataframes.items()
            }
        if columns_config is None:
            logging.info("No related columns usage, skipping masking")
            return dataframes

        for dataframe_name in list(dataframes.keys()):
            df = dataframes[dataframe_name]
            for col, usage in tqdm(
                columns_config[dataframe_name].items(), desc=dataframe_name
            ):
                if usage == "drop":
                    self.dropped_columns.append(col)
                    df.drop(col, axis=1, inplace=True)

        return dataframes
