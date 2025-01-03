import datetime
import re
from typing import Optional

import streamlit as st

# from sql_formatter.core import format_sql

mic = "ㅤ"  # U+3164


def get_db_credentials(db_type):
    if db_type == "MySQL":
        with st.expander("MySQL Credentials", expanded=True):
            db_host = st.text_input("host", "localhost")
            db_port = st.text_input("port", "5432")
            db_user = st.text_input("user", "postgres")
            db_password = st.text_input("password", "postgres", type="password")
            db_name = st.text_input("database", "postgres")
    else:
        db_host = st.secrets["DB_HOST"]
        db_user = st.secrets["DB_USERNAME"]
        db_password = st.secrets["DB_PASSWORD"]
        db_port = "3306"
        db_name = "client1"
    return db_host, db_port, db_user, db_password, db_name


#
# def extract_sql(response: str):
#     response = response.replace("sql SELECT", " SELECT").replace(
#         "sql\nSELECT", "SELECT"
#     )
#
#     def extract_core_code(input_text):
#         def ensure_semicolon(code):
#             code = code.strip()
#             if not code.endswith(";"):
#                 code += ";"
#             return code
#
#         patterns = [
#             r"```[ ]*(?i)sql(.*?)```",
#             r"```\n(.*?)\n```",
#             r"```(.*?)```",
#         ]
#
#         last_match = None
#         for pattern in patterns:
#             for match in re.finditer(pattern, input_text, re.DOTALL):
#                 last_match = match
#
#         if last_match:
#             return ensure_semicolon(last_match.group(1).strip()).replace("\n", " ")
#
#         return ensure_semicolon(input_text.strip()).replace("\n", " ")
#
#     code = extract_core_code(response)
#     return code, format_sql(code)


def extract_python(response: str) -> Optional[str]:
    def remove_pandas_io(code_string: Optional[str]):
        if code_string is None:
            return None
        lines = code_string.split("\n")
        filtered_lines = []

        for line in lines:
            if not (
                "pd.read_csv" in line
                or "to_csv" in line
                or "saved_figure.show()" in line
                or re.search("pd\..*sql.*", line)
            ):
                filtered_lines.append(line)

        filtered_code_string = "\n".join(filtered_lines)
        return filtered_code_string

    def extract_core_code(input_text):
        patterns = [
            r"(?<=```python\n)[\s\S]*?(?=```)",
            r"(?<=```python )[\s\S]*?(?=```)",
            r"(?<=```\n)[\s\S]*?(?=```)",
            r"(?<=``` )[\s\S]*?(?=```)",
        ]

        for pattern in patterns:
            last_match = None
            for match in re.finditer(pattern, input_text, re.DOTALL):
                last_match = match.group(0)
            if last_match is not None:
                return last_match

        return None

    # print(f"extract_python [{response}]")
    code = extract_core_code(response)
    # print(f"extract_core_code [{code}]")
    code = remove_pandas_io(code)
    print(f"returned code [{code}]")

    return code


def timestamp_to_date(timestamp: int):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def exec_on_tables(code: str, tables_df: dict):
    import math

    import altair as alt
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import sklearn
    import sklearn as sk

    for key, value in tables_df.items():
        print(f"Loading {key} in memory")
        locals()[key] = value

    code = f"""
import math
import altair as alt
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import sklearn as sk

{code}"""

    print(f"Running Python code >>>\n{code}\n<<< ===================", end="\n\n")
    locals_ = locals()
    exec(code, globals(), locals_)

    saved_dataframe = locals_.get("saved_dataframe", None)
    saved_figure = locals_.get("saved_figure", None)

    return saved_dataframe, saved_figure
