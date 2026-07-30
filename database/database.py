# Purpose: tables and stuff



import sqlite3


connection = sqlite3.connect("omniledger_system.db")

cursor = connection.cursor()



# USER TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users(

    userID INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    passwordHash TEXT NOT NULL,

    loginSuccess INTEGER DEFAULT 0

)
""")



# PROPERTIES TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS Properties(

    propertyID TEXT PRIMARY KEY,

    userID INTEGER NOT NULL,

    propertyAddress TEXT NOT NULL,

    propertyType TEXT NOT NULL,

    ownershipData TEXT NOT NULL,

    tenantName TEXT,

    leaseStatus TEXT,

    leaseStart TEXT,

    leaseEnd TEXT,

    weeklyRent REAL,

    bankAccount TEXT,

    propertyValue REAL,

    purchasePrice REAL,

    notes TEXT,

    FOREIGN KEY(userID)
        REFERENCES Users(userID)

)
""")



# TRANSACTIONS TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS Transactions(

    transactionID INTEGER PRIMARY KEY AUTOINCREMENT,

    propertyID TEXT NOT NULL,

    transactionType TEXT NOT NULL,

    category TEXT NOT NULL,

    amount REAL NOT NULL,

    date TEXT NOT NULL,

    paymentMethod TEXT,

    description TEXT,

    attachment TEXT,

    gstValue REAL,

    FOREIGN KEY(propertyID)
        REFERENCES Properties(propertyID)

)
""")


# REPORTS TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS Reports(

    reportID INTEGER PRIMARY KEY AUTOINCREMENT,

    userID INTEGER NOT NULL,

    reportType TEXT,

    startDate TEXT,

    endDate TEXT,

    totalIncome REAL,

    totalExpense REAL,

    totalBills REAL,

    netProfit REAL,

    roi REAL,

    predictedInsights TEXT,

    FOREIGN KEY(userID)
        REFERENCES Users(userID)

)
""")



# MARKET DATA TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS MarketData(

    marketID INTEGER PRIMARY KEY AUTOINCREMENT,

    suburb TEXT,

    medianPrice REAL,

    rentalYield REAL,

    vacancyRate REAL,

    lastUpdated TEXT

)
""")


connection.commit()


connection.close()


print("Database and tables created successfully!")