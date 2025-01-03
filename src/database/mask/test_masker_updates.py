import pytest

from src.database.mask.dataset_masker import DataMasker, count_words, p_words


def test_create_mappings():
    # Initialize a DataMasker object
    masker = DataMasker()

    # Create a dataframe for testing
    df = {
        "test_df": pd.DataFrame(
            {"name": ["John Doe", "Jane Doe"], "company": ["OpenAI", "Google"]}
        )
    }

    # Create the masking details
    masking_details = {"test_df": {"name": "mask_name", "company": "mask_company"}}

    # Add mappings to the DataMasker object
    masker.create_mappings(df, masking_details)

    # Check that the mappings have been added correctly
    usage_sets = masker.masking_sets.masking_sets
    assert "mask_name" in usage_sets
    assert "mask_company" in usage_sets
    assert "John Doe" in usage_sets["mask_name"]
    assert "Jane Doe" in usage_sets["mask_name"]
    assert "OpenAI" in usage_sets["mask_company"]
    assert "Google" in usage_sets["mask_company"]

    word_mapping = masker.word_mapping.word_mapping
    assert "John" in word_mapping
    assert "Jane" in word_mapping
    assert "Doe" in word_mapping
    assert "OpenAI" in word_mapping
    assert "Google" in word_mapping

    regex_word_mapping = masker.word_mapping.regex_word_mapping
    assert r"\bJohn\b" in regex_word_mapping
    assert r"\bJane\b" in regex_word_mapping
    assert r"\bDoe\b" in regex_word_mapping
    assert r"\bOpenAI\b" in regex_word_mapping
    assert r"\bGoogle\b" in regex_word_mapping

    placeholder_mapping = masker.word_mapping.placeholder_mapping
    for key in regex_word_mapping.values():
        assert f"\\b{key}\\b" in placeholder_mapping


def test_add_mappings():
    # Initialize a DataMasker object
    masker = DataMasker()

    # Create a dataframe for testing
    df = {
        "test_df": pd.DataFrame(
            {"name": ["John Doe", "Jane Doe"], "company": ["OpenAI", "Google"]}
        )
    }

    # Create the masking details
    masking_details = {"test_df": {"name": "mask_name", "company": "mask_company"}}

    # Add mappings to the DataMasker object
    masker.create_mappings(df, masking_details)

    df2 = {
        "test_df2": pd.DataFrame(
            {
                "oui": ["en effet"],
                "pourquoi": ["parceque"],
            }
        )
    }

    # Create the masking details
    masking_details2 = {
        "test_df2": {
            "oui": "mask_name",
            "pourquoi": "mask_any",
        }
    }

    masker.add_mappings(df2, masking_details2)
    wm = masker.word_mapping.word_mapping
    rwm = masker.word_mapping.regex_word_mapping
    assert "mask_name" in masker.masking_sets.masking_sets
    assert "mask_any" in masker.masking_sets.masking_sets
    assert "en effet" in masker.masking_sets.masking_sets["mask_name"]
    assert "parceque" in masker.masking_sets.masking_sets["mask_any"]
    assert "parceque" in wm

    assert r"\beffet\b" in rwm
    assert r"\ben\b" in rwm
    assert r"\bparceque\b" in rwm

    assert r"\ben\b" in rwm
    assert r"\bJohn\b" in rwm
    assert r"\bJane\b" in rwm
    assert r"\bDoe\b" in rwm
    assert r"\bOpenAI\b" in rwm
    assert r"\bGoogle\b" in rwm

    placeholder_mapping = masker.word_mapping.placeholder_mapping
    for key in rwm.values():
        assert f"\\b{key}\\b" in placeholder_mapping


import pandas as pd


def test_mask_new_data():
    # Create an instance of the DataMasker class
    masker = DataMasker()

    df = {
        "test_df": pd.DataFrame(
            {
                "name": ["John Doe", "Jane Doe"],
                "company": ["OpenAI", "Google"],
                "oui": ["en effet", "pourquoi. ok . yes"],
            }
        )
    }

    # Create the masking details
    masking_details = {
        "test_df": {"name": "mask_name", "company": "mask_company", "oui": "mask_any"}
    }

    masker.create_mappings(df, masking_details)

    # Store a copy of the original word mapping
    original_word_mapping = masker.word_mapping.word_mapping.copy()

    # Define your test data
    test_string = "This is a test string. Google Doe"

    # Call the mask_new_data method
    result = masker.mask_new_str(test_string)

    # Define what you expect the result to be
    # We don't know exactly what the result will be because it's randomly generated.
    # However, we can test that the result is a string and has the same number of words as the input.
    assert isinstance(result, str), "Result is not a string."
    assert count_words(result) == count_words(
        test_string
    ), "Number of words in the result and the input do not match."
    assert result != test_string, "The result is the same as the input."

    # Check if the existing words in word maps did not change
    for word, masked_word in original_word_mapping.items():
        assert (
            word in masker.word_mapping.word_mapping
        ), f"The word '{word}' is missing in the updated word mapping."
        assert (
            masker.word_mapping.word_mapping[word] == masked_word
        ), f"The masked version of '{word}' has changed in the updated word mapping."

    # Check if the new words were properly added
    new_words = set(p_words(test_string)) - set(original_word_mapping.keys())
    for word in new_words:
        assert (
            word in masker.word_mapping.word_mapping
        ), f"The new word '{word}' is not in the updated word mapping."

    # Check if the result is correct
    # For each word in the input string, check that it's been replaced in the result
    for word in p_words(test_string):
        masked_word = masker.word_mapping.word_mapping.get(word)
        if masked_word:
            assert (
                masked_word in result
            ), f"The word '{word}' has not been correctly replaced in the result."
        else:
            assert (
                word in result
            ), f"The word '{word}' should not have been replaced in the result."


def test_mask_new_data():
    # Create an instance of the DataMasker class
    masker = DataMasker()

    df = {
        "test_df": pd.DataFrame(
            {
                "name": ["John Doe", "Jane Doe"],
                "company": ["OpenAI", "Google"],
                "oui": ["en effet", "pourquoi. ok . yes"],
            }
        )
    }

    # Create the masking details
    masking_details = {
        "test_df": {"name": "mask_name", "company": "ok", "oui": "mask_any"}
    }

    masked_dfs1 = masker.transform(df, masking_details, inplace=False)
    masking_details = {
        "test_df": {"name": "mask_name", "company": "mask_company", "oui": "mask_any"}
    }
    masked_dfs2 = masker.transform_on_col_update(
        df, masking_details, table_name="test_df", col_name="company", inplace=False
    )
    # Define your test data

    # Define what you expect the result to be
    # We don't know exactly what the result will be because it's randomly generated.
    # However, we can test that the result is a string and has the same number of words as the input.
    assert (df["test_df"].company.values == masked_dfs1["test_df"].company.values).all()
    assert (df["test_df"].company.values != masked_dfs2["test_df"].company.values).all()
    assert (df["test_df"].name.values != masked_dfs2["test_df"].name.values).all()
    assert (
        masked_dfs1["test_df"].name.values == masked_dfs2["test_df"].name.values
    ).all()

    masking_details = {
        "test_df": {"name": "mask_name", "company": "ok", "oui": "mask_any"}
    }
    masked_dfs3 = masker.transform_on_col_update(
        df, masking_details, table_name="test_df", col_name="company", inplace=False
    )
    assert (
        masked_dfs2["test_df"].company.values != masked_dfs3["test_df"].company.values
    ).all()
    assert (df["test_df"].company.values == masked_dfs3["test_df"].company.values).all()


def test_mask_new_data_md():
    # Create an instance of the DataMasker class
    masker = DataMasker()

    df = {
        "test_df": pd.DataFrame(
            {
                "name": ["John Doe", "Jane Doe"],
                "company": ["OpenAI", "Google"],
                "oui": ["en effet", "pourquoi. ok . yes"],
            }
        ),
        "test_df2": pd.DataFrame(
            {
                "name": ["John Doe2", "Jane Doe"],
                "company": ["OpenAI", "Google"],
                "oui": ["en effet", "pourquoi. ok . yes"],
            }
        ),
    }

    # Create the masking details
    masking_details = {
        "test_df": {"name": "mask_name", "company": "ok", "oui": "mask_any"},
        "test_df2": {"name": "mask_name", "company": "ok", "oui": "mask_any"},
    }

    masked_dfs1 = masker.transform(df, masking_details, inplace=False)
    masking_details = {
        "test_df": {"name": "mask_name", "company": "mask_company", "oui": "mask_any"},
        "test_df2": {"name": "mask_name", "company": "ok", "oui": "mask_any"},
    }
    masked_dfs2 = masker.transform_on_col_update(
        df, masking_details, table_name="test_df", col_name="company", inplace=False
    )

    assert (df["test_df"].company.values == masked_dfs1["test_df"].company.values).all()
    assert (df["test_df"].company.values != masked_dfs2["test_df"].company.values).all()
    assert (df["test_df"].name.values != masked_dfs2["test_df"].name.values).all()
    assert (
        masked_dfs1["test_df"].name.values == masked_dfs2["test_df"].name.values
    ).all()

    assert (
        masked_dfs2["test_df2"].company.values != masked_dfs2["test_df"].company.values
    ).all()

    masking_details = {
        "test_df": {"name": "mask_name", "company": "mask_company", "oui": "mask_any"},
        "test_df2": {"name": "mask_name", "company": "mask_company", "oui": "mask_any"},
    }
    masked_dfs2 = masker.transform_on_col_update(
        df, masking_details, table_name="test_df2", col_name="company", inplace=False
    )
    # Define your test data

    assert (
        masked_dfs2["test_df2"].company.values == masked_dfs2["test_df"].company.values
    ).all()

    # masking_details = {
    #     "test_df": {"name": "mask_name", "company": "ok", "oui": "mask_any"},
    #     "test_df2": {"name": "mask_name", "company": "ok", "oui": "mask_any"}
    # }
    # masked_dfs3 = masker.transform_on_col_update(df, masking_details, table_name='test_df', col_name='company',
    #                                              inplace=False)
    # assert (masked_dfs2['test_df'].company.values != masked_dfs3['test_df'].company.values).all()
    # assert (df['test_df'].company.values == masked_dfs3['test_df'].company.values).all()


def test_mask_new_data_diff():
    # Create an instance of the DataMasker class
    masker = DataMasker()

    df = {
        "test_df": pd.DataFrame(
            {
                "name": ["John Doe", "Jane Doe"],
                "company": ["OpenAI", "Google"],
                "oui": ["en effet", "pourquoi. ok . yes"],
            }
        ),
        "test_df2": pd.DataFrame(
            {
                "name": ["John Doe2", "Jane Doe"],
                "company": ["OpenAI", "Google"],
                "oui": ["en effet", "pourquoi. ok . yes"],
            }
        ),
    }

    # Create the masking details
    masking_details = {
        "test_df": {"name": "mask_name", "company": "ok", "oui": "mask_any"},
        "test_df2": {"name": "mask_name", "company": "mask_any", "oui": "mask_any"},
    }

    masked_dfs1 = masker.transform(df, masking_details, inplace=False)
    masking_details = {
        "test_df": {"name": "mask_name", "company": "mask_company", "oui": "mask_any"},
        "test_df2": {"name": "mask_name", "company": "mask_any", "oui": "mask_any"},
    }
    masked_dfs2 = masker.transform_on_col_update(
        df, masking_details, table_name="test_df", col_name="company", inplace=False
    )

    assert (
        masked_dfs2["test_df2"].company.values == masked_dfs2["test_df"].company.values
    ).all()
    assert (
        df["test_df2"].company.values != masked_dfs2["test_df2"].company.values
    ).all()
    assert (
        masked_dfs1["test_df2"].company.values != masked_dfs2["test_df2"].company.values
    ).all()


def test_mask_new_data_diff2():
    # Create an instance of the DataMasker class
    masker = DataMasker()

    df = {
        "test_df": pd.DataFrame(
            {
                "name": ["John Doe", "Jane Doe", "Daniel", "Kev"],
                "company": ["OpenAI", "Google", "Baidu", "Tencent"],
                "oui": ["en effet", "pourquoi. ok . yes", "en effet2", "pourquoi?."],
            }
        ),
        "test_df2": pd.DataFrame(
            {
                "name": ["John Doe2", "Jane Doe", "Steph"],
                "company": ["OpenAI", "Google", "Microsoft"],
                "oui": ["en effet", "pourquoi. ok . yes", "aie"],
            }
        ),
    }

    # Create the masking details
    masking_details = {
        "test_df": {"name": "mask_name", "company": "ok", "oui": "mask_any"},
        "test_df2": {"name": "mask_name", "company": "mask_any", "oui": "mask_any"},
    }

    _ = masker.transform(df, masking_details, inplace=False)
    masking_details = {
        "test_df": {"name": "mask_name", "company": "mask_company", "oui": "mask_any"},
        "test_df2": {"name": "mask_name", "company": "mask_any", "oui": "mask_any"},
    }
    masked_dfs2 = masker.transform_on_col_update(
        df, masking_details, table_name="test_df", col_name="company", inplace=False
    )

    assert not masked_dfs2["test_df2"].company.str.contains("ERROR").any()
    assert (
        masked_dfs2["test_df2"].company.values[:2]
        == masked_dfs2["test_df"].company.values[:2]
    ).all()
    # assert (masked_dfs1['test_df2'].company.values != masked_dfs2['test_df2'].company.values).all()


if __name__ == "__main__":
    pytest.main([__file__])
