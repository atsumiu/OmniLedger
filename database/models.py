# Purpose: functions that communicate with database tables (CRUD)
import sqlite3

# Connect to database
def connect_database():

    return sqlite3.connect("omniledger_system.db")



# USER FUNCTIONS

# CREATE USER
def create_user(email, password):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO Users(email, password)
    VALUES (?, ?)
    """,
    (email, password))


    connection.commit()
    connection.close()


# READ USERS
def get_users():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM Users
    """)

    users = cursor.fetchall()

    connection.close()

    return users



# PROPERTY FUNCTIONS

# CREATE PROPERTY (adds new proerty record into database)
def create_property(propertyID, propertyAddress, ownershipData, tenantInfo):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO Properties(
        propertyID,
        propertyAddress,
        ownershipData,
        tenantInfo
    )
    VALUES (?, ?, ?, ?)
    """,
    (
        propertyID,
        propertyAddress,
        ownershipData,
        tenantInfo
    ))

    connection.commit()
    connection.close()


# READ PROPERTIES (retrieves all stored properties)
def get_properties():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM Properties
    """)

    properties = cursor.fetchall()

    connection.close()

    return properties





# TRANSACTION FUNCTIONS (users can create and view transactions, system auto calculates gst)

# CREATE TRANSACTION (adds a new transaction into the database)
# User inputs:
# - propertyID
# - transactionType
# - amount
# - date
# - category
# - description
# - attachment
#
# System calculates:
# - gstValue


def create_transaction(
    propertyID,
    transactionType,
    amount,
    date,
    category,
    description,
    attachment
):

    # CALCULATE GST VALUE (aus is 10%)

    gstValue = amount * 0.10


    # CONNECT TO DATABASE

    connection = connect_database()

    cursor = connection.cursor()



    # INSERT TRANSACTION RECORD INTO DATABASE

    cursor.execute("""
    INSERT INTO Transactions(
        propertyID,
        transactionType,
        amount,
        date,
        category,
        description,
        attachment,
        gstValue
    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

    """,
    (
        propertyID,
        transactionType,
        amount,
        date,
        category,
        description,
        attachment,
        gstValue
    ))



    # SAVE CHANGES

    connection.commit()


    # CLOSE DATABASE CONNECTION

    connection.close()





# READ TRANSACTIONS (gets all financial transaction stored in the database)

def get_transactions():

    # CONNECT TO DATABASE

    connection = connect_database()

    cursor = connection.cursor()



    # RETRIEVE TRANSACTION RECORDS

    cursor.execute("""
    SELECT * FROM Transactions
    """)



    transactions = cursor.fetchall()



    # CLOSE DATABASE CONNECTION

    connection.close()


    return transactions




# REPORT FUNCTIONS (stores processed info like income, expenses, profit, and roi)

# CREATE REPORT (saves a generated report into the database)

def create_report(
    reportType,
    startDate,
    endDate,
    totalIncome,
    totalExpense,
    totalBills,
    netProfit,
    roi,
    predictedInsights
):

    # CONNECT TO DATABASE

    connection = connect_database()

    cursor = connection.cursor()



    # INSERT REPORT DATA

    cursor.execute("""
    INSERT INTO Reports(
        reportType,
        startDate,
        endDate,
        totalIncome,
        totalExpense,
        totalBills,
        netProfit,
        roi,
        predictedInsights
    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

    """,
    (
        reportType,
        startDate,
        endDate,
        totalIncome,
        totalExpense,
        totalBills,
        netProfit,
        roi,
        predictedInsights
    ))



    # SAVE CHANGES

    connection.commit()



    # CLOSE DATABASE

    connection.close()





# READ REPORTS (gets all generated reports)
def get_reports():

    # Connect to database

    connection = connect_database()

    cursor = connection.cursor()



    # RETRIEVE REPORTS

    cursor.execute("""
    SELECT * FROM Reports
    """)



    reports = cursor.fetchall()



    # CLOSE DATABASE

    connection.close()


    return reports