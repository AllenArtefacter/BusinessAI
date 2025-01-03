request = """Sell OUT calculation: for each Month x Distributor x Product, Sell_Out_Qty = Sell_In - Inventory_Qty"""

column_to_match = "Sell_Out_Qty"

query = """
SELECT 
    i2.Distributor,
    i2.ProductID,
    i2.Month,
    (i1.Inventory_Qty + s.Sell_In_Qty) - i2.Inventory_Qty AS Sell_Out_Qty
FROM 
    Inventory AS i1
JOIN
    Inventory AS i2 ON i1.Distributor = i2.Distributor AND i1.ProductID = i2.ProductID AND DATE_ADD(i1.Month, INTERVAL 1 MONTH) = i2.Month
JOIN
    Sell_In AS s ON i2.Distributor = s.Distributor AND i2.ProductID = s.ProductID AND i2.Month = s.Month
"""


check = """
SELECT
    i2.Distributor,
    i2.ProductID,
    i2.Month,
    i2.Inventory_Qty,
    i1.Inventory_Qty AS Inventory_Qty_Last_Month,
    s.Sell_In_Qty,
    (i1.Inventory_Qty + s.Sell_In_Qty) - i2.Inventory_Qty AS Sell_Out_Qty_Computed,
    so.Sell_Out_Qty
FROM 
    Inventory AS i1
JOIN 
    Inventory AS i2 ON i1.Distributor = i2.Distributor AND i1.ProductID = i2.ProductID AND DATE_ADD(i1.Month, INTERVAL 1 MONTH) = i2.Month
JOIN 
    Sell_In AS s ON i2.Distributor = s.Distributor AND i2.ProductID = s.ProductID AND i2.Month = s.Month
JOIN
    _Sell_Out AS so ON i2.Distributor = so.Distributor AND i2.ProductID = so.ProductID AND i2.Month = so.Month
"""

query2 = """
SELECT
    so.Distributor,
    so.ProductID,
    so.Month,
    so.Sell_Out_Qty
FROM
    _Sell_Out AS so 
"""

check2 = """
SELECT 
    inv.Distributor, 
    inv.ProductID, 
    inv.Month, 
    prev_inv.Inventory_Qty AS Inventory_Qty_Last_Month,
    sell_in.Sell_In_Qty,
    inv.Inventory_Qty,
    ((COALESCE(prev_inv.Inventory_Qty, 0) + sell_in.Sell_In_Qty) - inv.Inventory_Qty) AS Sell_Out_Qty_Computed,
    so.Sell_Out_Qty
FROM 
    Inventory inv
LEFT JOIN 
    Inventory prev_inv ON inv.Distributor = prev_inv.Distributor 
                        AND inv.ProductID = prev_inv.ProductID 
                        AND DATE_SUB(inv.Month, INTERVAL 1 MONTH) = prev_inv.Month
LEFT JOIN 
    Sell_In sell_in ON inv.Distributor = sell_in.Distributor 
                    AND inv.ProductID = sell_in.ProductID 
                    AND inv.Month = sell_in.Month
LEFT JOIN
    _Sell_Out so ON inv.Distributor = so.Distributor
                    AND inv.ProductID = so.ProductID
                    AND inv.Month = so.Month;"""


oui = """
SELECT inv.Distributor, inv.ProductID, DATE_FORMAT(inv.Month, '%Y-%m') AS Month, ((prev_inv.Inventory_Qty + COALESCE(sell_in.Sell_In_Qty, 0)) - inv.Inventory_Qty) AS Sell_Out_Qty FROM Inventory inv LEFT JOIN Inventory prev_inv ON inv.Distributor = prev_inv.Distributor AND inv.ProductID = prev_inv.ProductID AND DATE_FORMAT(inv.Month, '%Y-%m') = DATE_FORMAT(DATE_SUB(prev_inv.Month, INTERVAL 1 MONTH), '%Y-%m') LEFT JOIN Sell_In sell_in ON inv.Distributor = sell_in.Distributor AND inv.ProductID = sell_in.ProductID AND DATE_FORMAT(inv.Month, '%Y-%m') = DATE_FORMAT(sell_in.Month, '%Y-%m') WHERE inv.Month = (SELECT MAX(Month) FROM Inventory) GROUP BY inv.Distributor, inv.ProductID, DATE_FORMAT(inv.Month, '%Y-%m')
"""
