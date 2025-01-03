import mysql.connector
from mysql.connector import Error


class MySQLWrapperNotUsed:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = self.create_connection()

    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def close_connection(self, connection):
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection is closed.")

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
        except Error as e:
            print(f"Error: {e}")

    def insert_df_in_table(self, df, table_name):
        for index, row in df.iterrows():
            columns = ", ".join(df.columns)
            values = ", ".join([f"'{str(i)}'" for i in row.values])
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.execute_query(self.connection, insert_query)

    def fetch_results(self, connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            records = cursor.fetchall()
            return records
        except Error as e:
            print(f"Error: {e}")
            return None

    def __del__(self):
        self.close_connection(self.connection)


# Usage example
if __name__ == "__main__":
    config = {
        "host": "xxx.xxx.xxx.xxx",
        "user": "x",
        "password": "XXXXXXX",
        "database": "x",
    }

    wrapper = MySQLWrapperNotUsed(**config)
    if not wrapper.connection:
        print("Connection failed.")
        exit()
    wrapper.execute_from_file("demo.sql")
