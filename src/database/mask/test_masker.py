from collections import defaultdict

import pandas as pd
import pytest
from faker import Faker

from src.database.mask.dataset_masker import (
    DataMasker,
    MaskingSets,
    WordMapping,
    count_words,
)


def test_count_words():
    assert count_words("one two three") == 3
    assert count_words("one|two/three\\four") == 4
    assert count_words("four12T_") == 1


def test_create_word_mapping():
    usage_sets = {
        "mask_company": {"test company 1", "test company 2"},
        "mask_name": {"test name", "test company 1"},
    }
    us = MaskingSets(usage_sets)
    wm = WordMapping.from_masking_sets(us)
    assert isinstance(wm.word_mapping, dict)
    assert len(wm.word_mapping) == 5


fake = Faker()
fake.seed_instance(0)


@pytest.fixture
def mock_datasets():
    return {
        "df1": pd.DataFrame(
            {
                "company": [fake.company() for _ in range(1000)],
                "name": [fake.name() for _ in range(1000)],
                "sentence": [fake.sentence() for _ in range(1000)],
                "id": [str(fake.random_int(min=1000, max=9999)) for _ in range(1000)],
            }
        ),
        "df2": pd.DataFrame(
            {
                "company": [fake.company() for _ in range(1000)],
                "name": [fake.name() for _ in range(1000)],
                "sentence": [fake.sentence() for _ in range(1000)],
                "id": [str(fake.random_int(min=1000, max=9999)) for _ in range(1000)],
            }
        ),
    }


@pytest.fixture
def mock_usages():
    return {
        "df1": {
            "company": "mask_company",
            "name": "mask_name",
            "sentence": "mask_any",
            "id": "mask_id",
        },
        "df2": {
            "company": "mask_company",
            "name": "mask_name",
            "sentence": "mask_any",
            "id": "mask_id",
        },
    }


def test_parse_datasets(mock_datasets, mock_usages):
    masking_sets: MaskingSets = MaskingSets.from_dataframes(
        mock_datasets, masking_details=mock_usages
    )
    assert isinstance(masking_sets.masking_sets, defaultdict)
    assert len(masking_sets.masking_sets) == 4
    assert all(isinstance(s, set) for s in masking_sets.values())


def test_mask_datasets(mock_datasets, mock_usages):
    masker = DataMasker()

    # Compute the value counts for each column in each dataset before masking
    original_value_counts = {
        dataset_name: {
            column_name: dataset[column_name].value_counts()
            for column_name in dataset.columns
        }
        for dataset_name, dataset in mock_datasets.items()
    }

    # Perform the masking operation
    masked_datasets = masker.transform(mock_datasets, mock_usages, inplace=False)

    # Compute the value counts for each column in each dataset after masking
    masked_value_counts = {
        dataset_name: {
            column_name: dataset[column_name].value_counts()
            for column_name in dataset.columns
        }
        for dataset_name, dataset in masked_datasets.items()
    }

    # Check that the frequency distribution of each column remains the same after masking
    for dataset_name in mock_datasets.keys():
        for column_name in mock_datasets[dataset_name].columns:
            assert (
                original_value_counts[dataset_name][column_name].values
                == masked_value_counts[dataset_name][column_name].values
            ).all()

            # Check that the actual values have changed
            assert not (
                original_value_counts[dataset_name][column_name].index
                == masked_value_counts[dataset_name][column_name].index
            ).any(), f"The actual values have not changed after masking {column_name} in {dataset_name}"


if __name__ == "__main__":
    pytest.main([__file__])
