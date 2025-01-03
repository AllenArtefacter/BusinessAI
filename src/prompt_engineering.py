from dataclasses import dataclass
from typing import Optional

QUERY_TO_REPLACE = "__QUERY"

DOC_TO_REPLACE = "DOCUMENTATION"
SQL_DIALECT_TO_REPLACE = "SQL_DIALECT"
PREVIOUS_CODE_TO_REPLACE = "PREVIOUS_CODE"
SQL_ERROR_TO_REPLACE = "SQLERROR"

KEYWORDS = [
    QUERY_TO_REPLACE,
    DOC_TO_REPLACE,
    SQL_DIALECT_TO_REPLACE,
    PREVIOUS_CODE_TO_REPLACE,
    SQL_ERROR_TO_REPLACE,
]

USER_KEYWORDS = [i for i in KEYWORDS if i[0] != "_"]


@dataclass
class PromptConfig:
    prompt: str
    sql_dialect: str
    doc: str
    system: Optional[str] = None
    assistant: Optional[str] = None

    @classmethod
    def no_prompt(cls, sql_dialect: str, doc: str):
        return cls(
            system=f"I am an helpful assistant trained complete {SQL_DIALECT_TO_REPLACE} tasks and write the results.",
            prompt=f"""{QUERY_TO_REPLACE}""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    @classmethod
    def only_code(cls, sql_dialect: str, doc: str):
        return cls(
            system=None,
            assistant=f"""I am a professional {SQL_DIALECT_TO_REPLACE} assistant. 
I have worked with {SQL_DIALECT_TO_REPLACE} for more than 20 years. 
I do not fall into the traps of {SQL_DIALECT_TO_REPLACE} and know all the subtleties
When necessary I am able to break down the task to make it easier to solve.
I write clear {SQL_DIALECT_TO_REPLACE} code with easy to understand table and column aliases.""",
            prompt=f"""Given the database schema, write a {SQL_DIALECT_TO_REPLACE} query that returns the following information:
{QUERY_TO_REPLACE}
Make the table and columns aliases as clear as possible.
You only need to write SQL code using "```sql <your {SQL_DIALECT_TO_REPLACE} code>```". No comment, no explanation. Just code.
Always use table name in column reference to avoid ambiguity
{DOC_TO_REPLACE}
""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    @classmethod
    def think_about_it(cls, sql_dialect: str, doc: str):
        return cls(
            system=None,
            assistant=f"""I am a professional {SQL_DIALECT_TO_REPLACE} assistant. 
I have worked with {SQL_DIALECT_TO_REPLACE} for more than 20 years. 
I do not fall into the traps of {SQL_DIALECT_TO_REPLACE} and know all the subtleties
When necessary I am able to break down the task to make it easier to solve.
I write clear {SQL_DIALECT_TO_REPLACE} code with easy to understand table and column aliases.""",
            prompt=f"""Given the database schema, write a {SQL_DIALECT_TO_REPLACE} query that returns the following information:
{QUERY_TO_REPLACE}
---
Write your thought process down the task and then SQL code using "```sql <your {SQL_DIALECT_TO_REPLACE} code>```".
Always use table name in column reference to avoid ambiguity
{DOC_TO_REPLACE}""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    @classmethod
    def balance(cls, sql_dialect: str, doc: str):
        return cls(
            system=None,
            assistant=f"""I am a professional {SQL_DIALECT_TO_REPLACE} assistant. 
I have worked with {SQL_DIALECT_TO_REPLACE} for many years. 
I do not fall into the traps of {SQL_DIALECT_TO_REPLACE} and know all the subtleties
When necessary I am able to break down the task to make it easier to solve.""",
            prompt=f"""Write a {SQL_DIALECT_TO_REPLACE} query that returns the following information:
{QUERY_TO_REPLACE}
Always use table name in column reference to avoid ambiguity
{DOC_TO_REPLACE}""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    @classmethod
    def free_gpt(cls, sql_dialect: str, doc: str):
        return cls(
            system=f"I am an helpful assistant trained complete {SQL_DIALECT_TO_REPLACE} tasks and write the results.",
            prompt=f"""Given the database schema, write a {SQL_DIALECT_TO_REPLACE} query that returns the following information:
{QUERY_TO_REPLACE}
Please use "```sql <your {SQL_DIALECT_TO_REPLACE} code>```" to write your SQL code.
Always use table name in column reference to avoid ambiguity
{DOC_TO_REPLACE}""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    @classmethod
    def auto_correct_on_error(cls, sql_dialect: str, doc: str):
        return cls(
            system=f"I am an helpful assistant trained complete {SQL_DIALECT_TO_REPLACE} tasks and write the results.",
            prompt=f"""Given the database schema, fix the {SQL_DIALECT_TO_REPLACE} query so that it returns the following information:
{QUERY_TO_REPLACE}
The query to fix is: ```sql {PREVIOUS_CODE_TO_REPLACE}```
For reference, it generated this error: {SQL_ERROR_TO_REPLACE}
Please use "```sql <your {SQL_DIALECT_TO_REPLACE} code>```" to write your SQL code.
Always use table name in column reference to avoid ambiguity
{DOC_TO_REPLACE}""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    @classmethod
    def auto_correct_on_error2(cls, sql_dialect: str, doc: str):
        return cls(
            system=f"I am an helpful assistant trained complete {SQL_DIALECT_TO_REPLACE} tasks and write the results.",
            prompt=f"""I wanted {QUERY_TO_REPLACE} and I tried using {PREVIOUS_CODE_TO_REPLACE} but it generated this error: {SQL_ERROR_TO_REPLACE}. Please fix it.
{DOC_TO_REPLACE}""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    @classmethod
    def try_again(cls, sql_dialect: str, doc: str):
        return cls(
            system=f"I am an helpful assistant trained complete {SQL_DIALECT_TO_REPLACE} tasks and write the results.",
            prompt=f"""I wanted {QUERY_TO_REPLACE} and I tried using {PREVIOUS_CODE_TO_REPLACE} but it did not output what I wanted. Please fix it.
{DOC_TO_REPLACE}""",
            sql_dialect=sql_dialect,
            doc=doc,
        )

    def _replace(self, s, user_input, gpt_message):
        s = (
            s.replace(QUERY_TO_REPLACE, user_input)
            .replace(DOC_TO_REPLACE, self.doc)
            .replace(SQL_DIALECT_TO_REPLACE, self.sql_dialect)
        )

        if gpt_message and gpt_message.error:
            s = s.replace(SQL_ERROR_TO_REPLACE, gpt_message.error)
        if gpt_message and gpt_message.code:
            s = s.replace(PREVIOUS_CODE_TO_REPLACE, gpt_message.code)
        return s

    def get_query(self, user_input: str, gpt_message=None):
        system = (
            self._replace(self.system, user_input, gpt_message) if self.system else None
        )
        prompt = self._replace(self.prompt, user_input, gpt_message)
        assistant = (
            self._replace(self.assistant, user_input, gpt_message)
            if self.assistant
            else None
        )

        return system, assistant, prompt

    def __call__(self, *args, **kwargs):
        return self.get_query(*args, **kwargs)


prompts = {
    "Code Only": PromptConfig.only_code,
    "No Prompt": PromptConfig.no_prompt,
    "Think About It": PromptConfig.think_about_it,
    "Balance": PromptConfig.balance,
    # "Think About It Twice": PromptConfig.think_about_it_twice,
    "Free GPT": PromptConfig.free_gpt,
}


def sql_documentation_generator(columns: dict[str, list[tuple]]) -> str:
    doc = f"""
DATABASE SCHEMA:\n
Total Tables: {len(columns)}"""
    for table_name in columns:
        doc += f"""\n---
Table: [{table_name}] has Columns:"""
        for column_name, column_type in columns[table_name]:
            doc += f"""
 - {column_name} {column_type.upper()}"""

    doc += (
        f"""\n\nIf a column or table is not in DATABASE SCHEMA feel free to create it"""
    )

    return doc


# -- Sell_In table
# CREATE TABLE IF NOT EXISTS Sell_In (
#     Month DATE NOT NULL,
#     Distributor VARCHAR(255) NOT NULL,
#     ProductID INT NOT NULL,
#     Sell_In_Qty INT NOT NULL
# );
#
# -- Inventory table
# CREATE TABLE IF NOT EXISTS Inventory (
#     Month DATE NOT NULL,
#     Distributor VARCHAR(255) NOT NULL,
#     ProductID INT NOT NULL,
#     Inventory_Qty INT NOT NULL
# );
#
# -- Product_Price table
# CREATE TABLE IF NOT EXISTS Product_Price (
#     Month DATE NOT NULL,
#     Distributor VARCHAR(255) NOT NULL,
#     ProductID INT NOT NULL,
#     Price DECIMAL(10, 2) NOT NULL
# );


if __name__ == "__main__":
    columns = {
        "Sell_In": [
            ("Month", "Date"),
            ("Distributor", "VARCHAR(255)"),
            ("ProductID", "INT"),
            ("Sell_In_Qty", "INT"),
        ],
        "Inventory": [
            ("Month", "Date"),
            ("Distributor", "VARCHAR(255)"),
            ("ProductID", "INT"),
            ("Inventory_Qty", "INT"),
        ],
        "Product_Price": [
            ("Month", "Date"),
            ("Distributor", "VARCHAR(255)"),
            ("ProductID", "INT"),
            ("Price", "DECIMAL(10, 2)"),
        ],
    }

    user_input = (
        "Create a SELECT statement to fetch all columns from the 'customers' table."
    )

    # Usage example:
    prompt_conf = PromptConfig.think_about_it(
        sql_dialect="MySQL", doc=sql_documentation_generator(columns)
    )

# 2023 - 04 - 23
# 16: 19:35.728
# gpt_stream_completion
# conversation = [{'role': 'assistant',
#                  'content': 'I am a professional MySQL assistant. \nI have worked with MySQL for many years. \nI do not fall into the traps of MySQL and know all the subtleties\nWhen necessary I am able to break down the task to make it easier to solve.'},
#                 {'role': 'user',
#                  'content': 'Given the database schema, write a MySQL query that returns the following information:\nSell OUT calculation: for each Month x Distributor x Product, Sell_Out_Qty = (Inventory_Qty_last_month + Sell_In) - Inventory_Qty\nInventory_Qty_last_month column does not exist\nmake the table and columns aliases as clear as possible\nYou only need to write SQL code using "```sql <your MySQL code>```". No comment, no explanation. Just code.\nAlways use table name in column reference to avoid ambiguity\n\nDATABASE SCHEMA DOCUMENTATION. Any non listed table/column do not exist.\n\nTotal Tables: 3\n---\nTable: [Inventory] has Columns:\n - Distributor TEXT\n - Inventory_Qty BIGINT\n - Month DATETIME\n - ProductID TEXT\n---\nTable: [Product_Price] has Columns:\n - Distributor TEXT\n - Month DATETIME\n - Price DOUBLE\n - ProductID TEXT\n---\nTable: [Sell_In] has Columns:\n - Distributor TEXT\n - Month DATETIME\n - ProductID TEXT\n - Sell_In_Qty BIGINT\n'}]
#
# """
# SELECT
#     s.Month AS Month,
#     s.Distributor AS Distributor,
#     s.ProductID AS ProductID,
#     (i.Inventory_Qty + s.Sell_In_Qty - COALESCE((SELECT Inventory_Qty FROM Inventory i2 WHERE i2.Month < s.Month AND i2.Distributor = s.Distributor AND i2.ProductID = s.ProductID ORDER BY i2.Month DESC LIMIT 1), 0)) AS Sell_Out_Qty
# FROM
#     Sell_In s
#     JOIN Inventory i ON s.Distributor = i.Distributor AND s.ProductID = i.ProductID AND s.Month = i.Month"""

# 2023 - 04 - 23
# 16: 19:06.143
# gpt_stream_completion
# conversation = [{'role': 'assistant',
#                  'content': 'I am a professional MySQL assistant. \nI have worked with MySQL for many years. \nI do not fall into the traps of MySQL and know all the subtleties\nWhen necessary I am able to break down the task to make it easier to solve.'},
#                 {'role': 'user',
#                  'content': 'Given the database schema, write a MySQL query that returns the following information:\nSell OUT calculation: for each Month x Distributor x Product, Sell_Out_Qty = (Inventory_Qty_last_month + Sell_In) - Inventory_Qty\nInventory_Qty_last_month column does not exist\nmake the table and columns aliases as clear as possible\nYou only need to write SQL code using "```sql <your MySQL code>```". No comment, no explanation. Just code.\nAlways use table name in column reference to avoid ambiguity\n\nDATABASE SCHEMA DOCUMENTATION. Any non listed table/column do not exist.\n\nTotal Tables: 3\n---\nTable: [Inventory] has Columns:\n - Distributor TEXT\n - Inventory_Qty BIGINT\n - Month DATETIME\n - ProductID TEXT\n---\nTable: [Product_Price] has Columns:\n - Distributor TEXT\n - Month DATETIME\n - Price DOUBLE\n - ProductID TEXT\n---\nTable: [Sell_In] has Columns:\n - Distributor TEXT\n - Month DATETIME\n - ProductID TEXT\n - Sell_In_Qty BIGINT\n'}]
#
# """
# SELECT
#     inv.Month AS Month,
#     inv.Distributor AS Distributor,
#     inv.ProductID AS Product,
#     ((SELECT Inventory_Qty FROM Inventory WHERE Month = DATE_SUB(inv.Month, INTERVAL 1 MONTH) AND Distributor = inv.Distributor AND ProductID = inv.ProductID) + si.Sell_In_Qty) - inv.Inventory_Qty AS Sell_Out_Qty
# FROM
#     Inventory inv
#     JOIN Sell_In si ON inv.Distributor = si.Distributor AND inv.Month = si.Month AND inv.ProductID = si.ProductID
#     """
