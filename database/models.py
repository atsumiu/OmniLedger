# Purpose: functions that communicate with database tables (CRUD)


import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash


def connect_database():

    connection = sqlite3.connect("omniledger_system.db")

    return connection




# USER FUNCTIONS

# CREATE USER

def create_user(name, email, password):

    connection = connect_database()

    cursor = connection.cursor()


    # Convert password into secure hash

    passwordHash = generate_password_hash(password)


    cursor.execute(
        """
        INSERT INTO Users(name, email, passwordHash)

        VALUES (?, ?, ?)
        """,

        (name, email, passwordHash)

    )


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

# CHECK USER LOGIN

def check_user(email, password):

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT userID, name, email, passwordHash

        FROM Users

        WHERE email = ?
        """,

        (email,)
    )

    user = cursor.fetchone()


    connection.close()



    # EXISTENCE CHECK

    if user:

        userID = user[0]
        name = user[1]
        storedEmail = user[2]
        storedPassword = user[3]

        
        if check_password_hash(storedPassword, password):

            return {

                "userID": userID,

                "name": name,

                "email": storedEmail

            }


    return None


# PROPERTY FUNCTIONS

# GENERATE PROPERTY ID

def generate_property_id():

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
    SELECT propertyID

    FROM Properties

    ORDER BY propertyID DESC

    LIMIT 1
    """)


    last_property = cursor.fetchone()


    connection.close()


    # FIRST 

    if last_property is None:

        return "PROP001"



    last_number = int(last_property[0][4:])

    new_number = last_number + 1


    return f"PROP{new_number:03d}"


# CREATE PROPERTY

def create_property(

    userID,
    propertyAddress,
    propertyType,
    ownershipData,
    tenantName,
    leaseStatus,
    leaseStart,
    leaseEnd,
    weeklyRent,
    bankAccount,
    propertyValue,
    purchasePrice,
    notes

):

    connection = connect_database()

    cursor = connection.cursor()

    propertyID = generate_property_id()


    cursor.execute("""

    INSERT INTO Properties(

        propertyID,
        userID,
        propertyAddress,
        propertyType,
        ownershipData,
        tenantName,
        leaseStatus,
        leaseStart,
        leaseEnd,
        weeklyRent,
        bankAccount,
        propertyValue,
        purchasePrice,
        notes

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """,

    (

        propertyID,
        userID,
        propertyAddress,
        propertyType,
        ownershipData,
        tenantName,
        leaseStatus,
        leaseStart,
        leaseEnd,
        weeklyRent,
        bankAccount,
        propertyValue,
        purchasePrice,
        notes

    ))

    connection.commit()

    connection.close()

    return propertyID


# UPDATE PROPERTY

def update_property(

    propertyID,
    propertyAddress,
    propertyType,
    ownershipData,
    tenantName,
    leaseStatus,
    leaseStart,
    leaseEnd,
    weeklyRent,
    bankAccount,
    propertyValue,
    purchasePrice,
    notes

):


    conn = connect_database()

    cursor = conn.cursor()



    cursor.execute(
    """

    UPDATE Properties

    SET

        propertyAddress=?,
        propertyType=?,
        ownershipData=?,
        tenantName=?,
        leaseStatus=?,
        leaseStart=?,
        leaseEnd=?,
        weeklyRent=?,
        bankAccount=?,
        propertyValue=?,
        purchasePrice=?,
        notes=?

    WHERE propertyID=?


    """,

    (

        propertyAddress,
        propertyType,
        ownershipData,
        tenantName,
        leaseStatus,
        leaseStart,
        leaseEnd,
        weeklyRent,
        bankAccount,
        propertyValue,
        purchasePrice,
        notes,
        propertyID

    ))



    conn.commit()

    conn.close()



# READ PROPERTIES

def get_properties(userID):

    conn = connect_database()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *

        FROM Properties

        WHERE userID = ?
        """,

        (userID,)
    )

    properties = cursor.fetchall()

    conn.close()

    return properties


# GET PROPERTY
def get_property(propertyID):

    conn = connect_database()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Properties
        WHERE propertyID = ?
    """, (propertyID,))

    property = cursor.fetchone()

    conn.close()

    if property:
        return dict(property)

    return None



# TRANSACTION FUNCTIONS 

# CREATE TRANSACTION

def create_transaction(

    propertyID,
    transactionType,
    category,
    amount,
    date,
    paymentMethod,
    description,
    attachment

):

    gstValue = amount * 0.10

    connection = connect_database()

    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO Transactions(
        propertyID,
        transactionType,
        category,
        amount,
        date,
        paymentMethod,
        description,
        attachment,
        gstValue
    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,

    (
        propertyID,
        transactionType,
        category,
        amount,
        date,
        paymentMethod,
        description,
        attachment,
        gstValue
    ))

    connection.commit()

    connection.close()


# GET TRANSACTIONS
def get_transactions(propertyID):

    connection = connect_database()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *

        FROM Transactions

        WHERE propertyID = ?

        ORDER BY date DESC
        """,

        (propertyID,)
    )

    transactions = cursor.fetchall()

    connection.close()

    return transactions


#PROPERTY TOTALS
def get_property_expenses(propertyID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM Transactions
        WHERE propertyID = ?
        AND transactionType = 'Expense'
    """, (propertyID,))

    result = cursor.fetchone()

    conn.close()

    if result[0] is None:
        return 0

    return result[0]


# PROPERTY INCOME

def get_property_income(propertyID):

    conn = connect_database()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM Transactions
        WHERE propertyID = ?
        AND transactionType = 'Income'
    """, (propertyID,))

    result = cursor.fetchone()

    conn.close()

    if result[0] is None:
        return 0

    return result[0]


# DASHBOARD FINANCE CALCULATIONS


# GET TOTAL INCOME

def get_total_income(userID):

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""

    SELECT SUM(Transactions.amount)

    FROM Transactions

    JOIN Properties

    ON Transactions.propertyID = Properties.propertyID

    WHERE Properties.userID = ?

    AND Transactions.transactionType = 'Income'

    """,

    (userID,))


    result = cursor.fetchone()[0]


    connection.close()


    return result if result else 0


# PROPERTY INCOME
def get_property_income(propertyID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM Transactions
        WHERE propertyID = ?
        AND transactionType = 'Income'
    """, (propertyID,))

    result = cursor.fetchone()

    conn.close()

    if result[0] is None:
        return 0

    return result[0]


# GET TOTAL EXPENSES

def get_total_expenses(userID):

    connection = connect_database()

    cursor = connection.cursor()



    cursor.execute("""

    SELECT SUM(Transactions.amount)

    FROM Transactions

    JOIN Properties

    ON Transactions.propertyID = Properties.propertyID

    WHERE Properties.userID = ?

    AND Transactions.transactionType = 'Expense'

    """,

    (userID,))



    result = cursor.fetchone()[0]


    connection.close()


    return result if result else 0





# GET NET PROFIT

def get_net_profit(userID):


    income = get_total_income(userID)


    expenses = get_total_expenses(userID)


    return income - expenses



# CREATE REPORT

def create_report(

    userID,
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

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""

    INSERT INTO Reports(

        userID,
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

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """,

    (

        userID,
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

    connection.commit()

    connection.close()





# READ REPORTS 

def get_reports(userID):

    # CONNECT TO DATABASE

    connection = connect_database()

    cursor = connection.cursor()


    cursor.execute("""
    SELECT *

    FROM Reports

    WHERE userID = ?

    """,

    (userID,))



    reports = cursor.fetchall()


    connection.close()


    return reports


