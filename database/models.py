import sqlite3

from database.database import connect_database

from werkzeug.security import generate_password_hash, check_password_hash


# USER STUFF

def create_user(name, email, password):

    conn = connect_database()
    cursor = conn.cursor()


    passwordHash = generate_password_hash(
        password
    )

    cursor.execute("""
        INSERT INTO Users (
            name,
            email,
            passwordHash
        )
        VALUES (?, ?, ?)
    """, (
        name,
        email,
        passwordHash
    ))

    conn.commit()
    conn.close()


def get_users():

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Users
    """)

    users = cursor.fetchall()

    conn.close()

    return users


def check_user(email, password):

    conn = connect_database()
    cursor = conn.cursor()


    cursor.execute("""
        SELECT userID, name, email, passwordHash
        FROM Users
        WHERE email = ?
    """, (
        email,
    ))

    user = cursor.fetchone()

    conn.close()


    if user is None:

        return None


    stored_password = user["passwordHash"]


    try:

        password_correct = check_password_hash(
            stored_password,
            password
        )

    except ValueError:

        password_correct = False


    if not password_correct:

        password_correct = (
            stored_password == password
        )


    if password_correct:

        return {
            "userID": user["userID"],
            "name": user["name"],
            "email": user["email"]
        }


    return None

# PROPERTY

def generate_property_id():

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT propertyID
        FROM Properties
        ORDER BY propertyID DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return "PROP001"

    last_id = result[0]

    try:

        number = int(last_id.replace("PROP", ""))

        return f"PROP{number + 1:03d}"

    except (ValueError, AttributeError):

        return "PROP001"


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

    conn = connect_database()
    cursor = conn.cursor()

    propertyID = generate_property_id()

    cursor.execute("""
        INSERT INTO Properties (
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
    """, (
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

    conn.commit()
    conn.close()

    return propertyID


def get_properties(userID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Properties
        WHERE userID = ?
    """, (userID,))

    properties = cursor.fetchall()

    conn.close()

    return properties


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

    cursor.execute("""
        UPDATE Properties
        SET
            propertyAddress = ?,
            propertyType = ?,
            ownershipData = ?,
            tenantName = ?,
            leaseStatus = ?,
            leaseStart = ?,
            leaseEnd = ?,
            weeklyRent = ?,
            bankAccount = ?,
            propertyValue = ?,
            purchasePrice = ?,
            notes = ?
        WHERE propertyID = ?
    """, (
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


def get_property(propertyID, userID=None):

    conn = connect_database()
    cursor = conn.cursor()

    if userID is not None:

        cursor.execute("""
            SELECT *
            FROM Properties
            WHERE propertyID = ?
            AND userID = ?
        """, (
            propertyID,
            userID
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM Properties
            WHERE propertyID = ?
        """, (propertyID,))

    property_data = cursor.fetchone()

    conn.close()

    return property_data


# TRANSACTIONS

def create_transaction(
    propertyID,
    transactionType,
    category,
    amount,
    date,
    paymentMethod,
    description,
    attachment=None
):

    conn = connect_database()
    cursor = conn.cursor()

    # GST calculation
    gstValue = amount * 0.10

    cursor.execute("""
        INSERT INTO Transactions (
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
    """, (
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

    conn.commit()
    conn.close()


def get_transactions(propertyID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Transactions
        WHERE propertyID = ?
        ORDER BY date DESC
    """, (propertyID,))

    transactions = cursor.fetchall()

    conn.close()

    return transactions


def get_report_transactions(
    userID,
    propertyID="all",
    startDate=None,
    endDate=None
):

    conn = connect_database()
    cursor = conn.cursor()

    query = """
        SELECT
            t.transactionID,
            t.propertyID,
            t.transactionType,
            t.category,
            t.amount,
            t.date,
            t.paymentMethod,
            t.description,
            t.attachment,
            t.gstValue

        FROM Transactions t

        INNER JOIN Properties p
            ON t.propertyID = p.propertyID

        WHERE p.userID = ?
    """

    parameters = [userID]


    # FILTER BY PROPERTY

    if propertyID and propertyID != "all":

        query += """
            AND t.propertyID = ?
        """

        parameters.append(propertyID)


    # FILTER BY START DATE

    if startDate:

        query += """
            AND date(
                substr(t.date, 7, 4) || '-' ||
                substr(t.date, 4, 2) || '-' ||
                substr(t.date, 1, 2)
            ) >= date(?)
        """

        parameters.append(startDate)


    # FILTER BY END DATE

    if endDate:

        query += """
            AND date(
                substr(t.date, 7, 4) || '-' ||
                substr(t.date, 4, 2) || '-' ||
                substr(t.date, 1, 2)
            ) <= date(?)
        """

        parameters.append(endDate)


    # SORT BY DATE

    query += """
        ORDER BY t.date ASC
    """


    cursor.execute(
        query,
        parameters
    )

    transactions = cursor.fetchall()

    conn.close()

    return transactions

# PROPERTY

def get_property_income(propertyID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE propertyID = ?
        AND transactionType = 'Income'
    """, (propertyID,))

    total_income = cursor.fetchone()[0]

    conn.close()

    return total_income


def get_property_expenses(propertyID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM Transactions
        WHERE propertyID = ?
        AND transactionType = 'Expense'
    """, (propertyID,))

    total_expenses = cursor.fetchone()[0]

    conn.close()

    return total_expenses


# FINANCE STUFF

def get_total_income(userID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(t.amount), 0)

        FROM Transactions t

        INNER JOIN Properties p
            ON t.propertyID = p.propertyID

        WHERE p.userID = ?
        AND t.transactionType = 'Income'
    """, (userID,))

    total_income = cursor.fetchone()[0]

    conn.close()

    return total_income


def get_total_expenses(userID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(t.amount), 0)

        FROM Transactions t

        INNER JOIN Properties p
            ON t.propertyID = p.propertyID

        WHERE p.userID = ?
        AND t.transactionType = 'Expense'
    """, (userID,))

    total_expenses = cursor.fetchone()[0]

    conn.close()

    return total_expenses


def get_net_profit(userID):

    total_income = get_total_income(userID)
    total_expenses = get_total_expenses(userID)

    return total_income - total_expenses


# REPORT

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

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Reports (
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
    """, (
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

    reportID = cursor.lastrowid

    conn.commit()
    conn.close()

    return reportID


def get_reports(userID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Reports
        WHERE userID = ?
        ORDER BY reportID DESC
    """, (userID,))

    reports = cursor.fetchall()

    conn.close()

    return reports


def get_report(reportID, userID):

    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Reports
        WHERE reportID = ?
        AND userID = ?
    """, (
        reportID,
        userID
    ))

    report = cursor.fetchone()

    conn.close()

    return report