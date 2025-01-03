import os

import pandas as pd
import pymysql
from pymysql import MySQLError
from sqlalchemy import create_engine


class MySQLWrapper:  # Add abstraction
    def __init__(self, host, user, password, database, connect=True):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        if connect:
            self.connection, self.engine = self.create_connection()

    def get_connection_string(self):
        return (
            f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}"
        )

    def create_connection(self):
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            engine = create_engine(
                f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}"
            )

            return connection, engine
        except MySQLError as e:
            print(f"Error: {e}")
            return None, None

    def close_connection(self):
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()

    def execute_from_file(self, file):
        with open(file, "r") as f:
            sql_commands = f.read().split(";")
            for command in sql_commands:
                if command.strip() != "":
                    self.execute_query(command)

    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully.")
        except MySQLError as e:
            print(f"Error: {e}")

    def insert_df_in_table(self, df, table_name):
        for index, row in df.iterrows():
            columns = ", ".join(df.columns)
            values = ", ".join([f"'{str(i)}'" for i in row.values])
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.execute_query(insert_query)

    def fetch_results(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            records = cursor.fetchall()
            return records
        except MySQLError as e:
            print(f"Error: {e}")
            return None

    def fetch_results_pandas(self, query):
        return pd.read_sql_query(query, self.connection)

    @property
    def sql_dialect(self):
        return "MySQL"

    def __del__(self):
        self.close_connection()

    def get_table_info(self):
        query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE();
        """

        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        table_info = {}
        for row in result:
            table_name, column_name, data_type = row
            if table_name not in table_info:
                table_info[table_name] = []
            table_info[table_name].append((column_name, data_type))

        return table_info

    def get_table_names(self):
        return self.get_table_info().keys()


# Usage example
if __name__ == "__main__":
    config = {
        "host": os.environ["DB_HOST"],
        "user": "x",
        "password": os.environ["db_pwd"],
        "database": "x",
    }

    wrapper = MySQLWrapper(**config)
    if not wrapper.connection:
        print("Connection failed.")
        exit()
    wrapper.execute_from_file("demo.sql")

    print(wrapper.get_table_info())
