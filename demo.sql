-- Sell_In table
CREATE TABLE IF NOT EXISTS Sell_In (
    Month DATE NOT NULL,
    Distributor VARCHAR(255) NOT NULL,
    ProductID INT NOT NULL,
    Sell_In_Qty INT NOT NULL
);

-- Inventory table
CREATE TABLE IF NOT EXISTS Inventory (
    Month DATE NOT NULL,
    Distributor VARCHAR(255) NOT NULL,
    ProductID INT NOT NULL,
    Inventory_Qty INT NOT NULL
);

-- Product_Price table
CREATE TABLE IF NOT EXISTS Product_Price (
    Month DATE NOT NULL,
    Distributor VARCHAR(255) NOT NULL,
    ProductID INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL
);


