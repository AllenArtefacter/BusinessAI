from src.tools.utils import exec_on_tables


def test_exec_on_tables():
    code = """
def f(x):
    return x + 1
saved_dataframe = f(3)
"""
    tables_df = {"df": 1}
    saved_dataframe, saved_figure = exec_on_tables(code, tables_df)
    assert saved_dataframe == 4
