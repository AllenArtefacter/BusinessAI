from typing import Optional

import pandas as pd


def db_schema_generation(
    tables: dict[str, pd.DataFrame], descriptions: Optional[dict[str, dict[str, str]]]
):
    _db_schema = """SCHEMA:"""
    # for table_name in tables_df:
    #     db_schema += f"""
    # Dataframe {table_name}
    # {tables_df[table_name].dtypes}
    # """
    for _table_name in tables:
        _db_schema += f"Dataframe {_table_name}\n"
        for col in tables[_table_name].columns:
            if (
                descriptions
                and _table_name in descriptions
                and col in descriptions[_table_name]
                and descriptions[_table_name][col] != ""
            ):
                _db_schema += f"{_table_name}.{col}: {tables[_table_name][col].dtype}. Description: {descriptions[_table_name][col]}\n"
            else:
                _db_schema += f"{_table_name}.{col}: {tables[_table_name][col].dtype}\n"
        _db_schema += "\n"
        _db_schema += f"Sample of {_table_name}:\n"
        _db_schema += tables[_table_name].head(3).to_string()
        _db_schema += "\n\n"

    return _db_schema


rules = f"""
RULES:
- if a column is not in SCHEMA, create it
- the variable `saved_dataframe` must contains the final result
"""
