# Purpose: Connects to the SQLite database and creates all tables. Only creates database structures

# IMPORTS
import sqlite3


# CONNECT TO DATABASE
connection = sqlite3.connect("omniledger_system.db")

#PYTHON SEND SQL COMMANDS
cursor = connection.cursor()


# CREATE USERS TABLE (stores user login info)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users(

    userID INTEGER PRIMARY KEY AUTOINCREMENT,

    email TEXT NOT NULL UNIQUE,

    password TEXT NOT NULL,

    loginSuccess INTEGER DEFAULT 0

)
""")


# CREATE PROPERTIES TABLE (stores property details)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Properties(

    propertyID TEXT PRIMARY KEY,

    propertyAddress TEXT NOT NULL,

    ownershipData TEXT NOT NULL,

    tenantInfo TEXT

)
""")


# CREATE TRANSACTIONS TABLE (stores financial transactions & propertyID links to property)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Transactions(

    transactionID INTEGER PRIMARY KEY AUTOINCREMENT,

    propertyID TEXT NOT NULL,

    transactionType TEXT NOT NULL,

    amount REAL NOT NULL,

    date TEXT NOT NULL,

    category TEXT NOT NULL,

    description TEXT,

    attachment TEXT,

    gstValue REAL,

    FOREIGN KEY(propertyID)
        REFERENCES Properties(propertyID)

)
""")


# CREATE REPORTS TABLE (stores generated reports)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Reports(

    reportID INTEGER PRIMARY KEY AUTOINCREMENT,

    reportType TEXT,

    startDate TEXT,

    endDate TEXT,

    totalIncome REAL,

    totalExpense REAL,

    totalBills REAL,

    netProfit REAL,

    roi REAL,

    predictedInsights TEXT

)
""")


# CREATE MARKET DATA TABLE (stores info received from future api)
cursor.execute("""
CREATE TABLE IF NOT EXISTS MarketData(

    marketID INTEGER PRIMARY KEY AUTOINCREMENT,

    searchCriteria TEXT,

    marketData TEXT

)
""")


# SAVE CHANGES (writes every create table command permanently)
connection.commit()


# CLOSE DATABASE (closes connection)
connection.close()



# MESSAGE (confirmation that database and tables were created successfully)
print("Database and tables created successfully!")
