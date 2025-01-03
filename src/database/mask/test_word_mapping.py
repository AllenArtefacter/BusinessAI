import pandas as pd
import pytest

from src.database.mask.dataset_masker import DataMasker, WordMapping


def replace(series, word_mapping):
    (
        regex_word_mapping,
        regex_word_mapping_no_regex,
        placeholder_mapping,
        placeholder_mapping_no_regex,
    ) = WordMapping.get_regex_word_mapping(word_mapping)

    result = DataMasker.apply_word_mapping(
        series,
        regex_word_mapping,
        regex_word_mapping_no_regex,
        placeholder_mapping,
        placeholder_mapping_no_regex,
    )
    print(result)
    return result


def test_apply_word_mapping():
    series = pd.Series(["this is a test", "another test", "yet another test"])

    word_mapping = {
        "this": "that",
        "that": "this",
        "is": "is not",
        "test": "exam",
        "another": "a different",
        "a different": "another",
    }
    result = replace(series, word_mapping)
    expected_series = pd.Series(
        ["that is not a exam", "a different exam", "yet a different exam"]
    )
    assert result.equals(expected_series)

    word_mapping = {"this": "this", "test": "test"}
    result = replace(series, word_mapping)

    expected_series = pd.Series(["this is a test", "another test", "yet another test"])
    assert result.equals(expected_series)

    word_mapping = {"this": "that", "that": "this"}
    result = replace(series, word_mapping)

    expected_series = pd.Series(["that is a test", "another test", "yet another test"])
    assert result.equals(expected_series)


def test_apply_word_mapping_loop():
    series = pd.Series(["this and that are tests"])

    word_mapping = {
        "this": "that",
        "that": "this",
    }
    result = replace(series, word_mapping)

    expected_series = pd.Series(["that and this are tests"])
    assert result.equals(expected_series)


def test_apply_word_mapping_special_sep():
    series = pd.Series(["this|is|a|test", "another/test", "yet=another?test"])

    word_mapping = {
        "this": "that",
        "that": "this",
        "is": "is not",
        "test": "exam",
        "another": "a different",
        "a different": "another",
    }
    result = replace(series, word_mapping)

    expected_series = pd.Series(
        ["that|is not|a|exam", "a different/exam", "yet=a different?exam"]
    )
    assert result.equals(expected_series)


if __name__ == "__main__":
    pytest.main([__file__])
