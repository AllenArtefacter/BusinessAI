import os

request_easy = """I want : DoH Calculation: for each Month x Distributor x Product, DoH = Inventory / avg_of_last_3_month(Sell_Out_Qty * Price)
info: Sell OUT calculation: for each Month x Distributor x Product, Sell_Out_Qty = (Inventory_Qty_last_month + Sell_In) - Inventory_Qty"""

request = "DoH Calculation: for each Month x Distributor x Product, DoH = Inventory / avg_of_last_3_month(Sell_Out_Qty * Price)"

column_to_match = "DoH"

query = """
WITH avg_sell_out_qty_price AS (
    WITH sell_out AS (
        SELECT i.Distributor, i.Month, i.ProductID,
            (si.Sell_In_Qty - i.Inventory_Qty) AS Sell_Out_Qty
        FROM Inventory i
        JOIN Sell_In si ON i.Distributor = si.Distributor AND i.Month = si.Month AND i.ProductID = si.ProductID
        GROUP BY i.Distributor, i.Month, i.ProductID, Sell_Out_Qty
    )
    SELECT
        si1.Distributor,
        si1.ProductID,
        si1.Month,
        AVG(so.Sell_Out_Qty * pp.Price) as avg_sell_out_qty_price_last_3_months
    FROM
        Sell_In si1
    JOIN Sell_In si2 ON
        si1.Distributor = si2.Distributor
        AND si1.ProductID = si2.ProductID
        AND si2.Month BETWEEN DATE_SUB(si1.Month, INTERVAL 3 MONTH) AND DATE_SUB(si1.Month, INTERVAL 1 MONTH)
    JOIN Product_Price pp ON
        si2.Distributor = pp.Distributor
        AND si2.ProductID = pp.ProductID
        AND si2.Month = pp.Month
    JOIN sell_out so ON
        si2.Distributor = so.Distributor
        AND si2.ProductID = so.ProductID
        AND si2.Month = so.Month
    GROUP BY
        si1.Distributor,
        si1.ProductID,
        si1.Month
)
SELECT
    i.Distributor,
    i.ProductID,
    i.Month,
    i.Inventory_Qty / a.avg_sell_out_qty_price_last_3_months as DoH
FROM
    Inventory i
JOIN avg_sell_out_qty_price a ON
    i.Distributor = a.Distributor
    AND i.ProductID = a.ProductID
    AND i.Month = a.Month
# ORDER BY DoH; 
# FIXME
"""


def doh(Sell_In_df, Inventory_df, Product_Price_df):
    merged_df = pd.merge(
        Inventory_df, Sell_In_df, on=["Month", "Distributor", "ProductID"], how="left"
    )

    # Step 2: Sort the merged dataframe
    merged_df = merged_df.sort_values(by=["Month", "Distributor", "ProductID"])

    # Step 3: Create a new column Inventory_Qty_last_month
    merged_df["Inventory_Qty_last_month"] = (
        merged_df.groupby(["Distributor", "ProductID"])["Inventory_Qty"]
        .shift(1)
        .fillna(0)
    )

    # Step 4: Create a new column Sell_Out_Qty
    merged_df["Sell_Out_Qty"] = (
        merged_df["Inventory_Qty_last_month"] + merged_df["Sell_In_Qty"]
    ) - merged_df["Inventory_Qty"]

    # Step 5: Merge Product_Price_df dataframe
    merged_df = pd.merge(
        merged_df,
        Product_Price_df,
        on=["Month", "Distributor", "ProductID"],
        how="left",
    )

    # Step 6: Create a new column Sell_Out_Value
    merged_df["Sell_Out_Value"] = merged_df["Sell_Out_Qty"] * merged_df["Price"]

    # Step 7: Create a new column avg_of_last_3_month_Sell_Out_Value
    merged_df = merged_df.sort_values(by=["Distributor", "ProductID", "Month"])
    merged_df.reset_index(inplace=True, drop=True)
    merged_df["avg_of_last_3_month_Sell_Out_Value"] = (
        merged_df[["Sell_Out_Value"]]
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(drop=True)
    )

    # Step 8: Create a new column DoH
    merged_df["DoH"] = (
        merged_df["Inventory_Qty"] / merged_df["avg_of_last_3_month_Sell_Out_Value"]
    )

    # Step 9: Select the columns Month, Distributor, ProductID, and DoH
    saved_dataframe = merged_df[
        [
            "Month",
            "Distributor",
            "ProductID",
            "avg_of_last_3_month_Sell_Out_Value",
            "Sell_Out_Qty",
            "DoH",
            "Sell_Out_Value",
        ]
    ]
    saved_dataframe.sort_values("DoH")
    return saved_dataframe


if __name__ == "__main__":
    import pandas as pd

    from src.database.old.pymysql_wrapper import MySQLWrapper

    db = MySQLWrapper(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
    Sell_In_df = db.fetch_results_pandas("SELECT * FROM Sell_In")
    Inventory_df = db.fetch_results_pandas("SELECT * FROM Inventory")
    Product_Price_df = db.fetch_results_pandas("SELECT * FROM Product_Price")

    saved_dataframe = doh(Sell_In_df, Inventory_df, Product_Price_df)

    # Display the result
    print(
        saved_dataframe.loc[
            :, ["Distributor", "ProductID", "Month", "DoH"]
        ].sort_values(["DoH"])
    )
