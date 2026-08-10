def calculate_total_income(transactions):

    total_income = 0

    for transaction in transactions:

        if transaction[2] == "Income":

            total_income += transaction[4]

    return round(total_income, 2)


def calculate_total_expenses(transactions):

    total_expenses = 0

    for transaction in transactions:

        if transaction[2] == "Expense":

            total_expenses += transaction[4]

    return round(total_expenses, 2)


def calculate_net_profit(total_income, total_expenses):

    net_profit = total_income - total_expenses

    return round(net_profit, 2)


# INCOME STATEMENT

def calculate_income_statement(transactions):

    total_income = calculate_total_income(transactions)

    total_expenses = calculate_total_expenses(transactions)

    net_profit = calculate_net_profit(
        total_income,
        total_expenses
    )

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_profit": net_profit
    }


# INCOME BREAKDOWN

def calculate_income_breakdown(transactions):

    income_breakdown = {}

    for transaction in transactions:

        # TRANSACTION TYPE = INDEX 2
        # CATEGORY = INDEX 3
        # AMOUNT = INDEX 4

        if transaction[2] == "Income":

            category = transaction[3]
            amount = transaction[4]

            if category not in income_breakdown:

                income_breakdown[category] = 0

            income_breakdown[category] += amount


    # Round values

    for category in income_breakdown:

        income_breakdown[category] = round(
            income_breakdown[category],
            2
        )


    return income_breakdown


# EXPENSE BREAKDOWN

def calculate_expense_breakdown(transactions):

    expense_breakdown = {}

    for transaction in transactions:


        if transaction[2] == "Expense":

            category = transaction[3]
            amount = transaction[4]

            if category not in expense_breakdown:

                expense_breakdown[category] = 0

            expense_breakdown[category] += amount


    for category in expense_breakdown:

        expense_breakdown[category] = round(
            expense_breakdown[category],
            2
        )


    return expense_breakdown


# GST

def calculate_gst(transactions):

    total_gst = 0

    # GST VALUE = INDEX 9

    for transaction in transactions:

        gst_value = transaction[9] or 0

        total_gst += gst_value


    return round(total_gst, 2)


def calculate_gst_summary(transactions):

    gst_income = 0
    gst_expenses = 0

    for transaction in transactions:

        transaction_type = transaction[2]

        gst_value = transaction[9] or 0


        if transaction_type == "Income":

            gst_income += gst_value


        elif transaction_type == "Expense":

            gst_expenses += gst_value


    net_gst = gst_income - gst_expenses


    return {
        "gst_on_income": round(gst_income, 2),

        "gst_on_expenses": round(gst_expenses, 2),

        "net_gst": round(net_gst, 2)
    }


# CASH FLOW

def calculate_cash_flow(transactions):

    cash_inflow = 0
    cash_outflow = 0


    for transaction in transactions:

        transaction_type = transaction[2]
        amount = transaction[4]


        if transaction_type == "Income":

            cash_inflow += amount


        elif transaction_type == "Expense":

            cash_outflow += amount


    net_cash_flow = cash_inflow - cash_outflow


    return {
        "cash_inflow": round(cash_inflow, 2),

        "cash_outflow": round(cash_outflow, 2),

        "net_cash_flow": round(net_cash_flow, 2)
    }


# BILLS
def calculate_total_bills(transactions):

    total_bills = 0


    for transaction in transactions:

        transaction_type = transaction[2]
        category = transaction[3]
        amount = transaction[4]

        if (
            transaction_type == "Expense"
            and category.lower() in [
                "bill",
                "bills"
            ]
        ):

            total_bills += amount


    return round(total_bills, 2)


# RENTAL ROI

def calculate_rental_roi(
    weeklyRent,
    totalExpenses,
    purchasePrice
):

    annualIncome = weeklyRent * 52


    if purchasePrice == 0:

        return 0


    roi = (
        (annualIncome - totalExpenses)
        / purchasePrice
    ) * 100


    return round(roi, 2)


# TOTAL ROI
def calculate_total_roi(
    propertyValue,
    purchasePrice,
    weeklyRent,
    totalExpenses
):

    annualIncome = weeklyRent * 52


    if purchasePrice == 0:

        return 0


    netRentalIncome = (
        annualIncome - totalExpenses
    )


    roi = (
        (
            propertyValue
            - purchasePrice
            + netRentalIncome
        )
        / purchasePrice
    ) * 100


    return round(roi, 2)


# PROPERTY ROI

def calculate_property_roi(
    propertyValue,
    purchasePrice,
    weeklyRent,
    totalExpenses
):

    rental_roi = calculate_rental_roi(
        weeklyRent,
        totalExpenses,
        purchasePrice
    )


    total_roi = calculate_total_roi(
        propertyValue,
        purchasePrice,
        weeklyRent,
        totalExpenses
    )


    return {
        "rental_roi": rental_roi,

        "total_roi": total_roi
    }


# BALANCE SHEET

def calculate_balance_sheet(
    propertyValue=0,
    liabilities=0
):

    propertyValue = propertyValue or 0
    liabilities = liabilities or 0


    assets = propertyValue


    equity = assets - liabilities


    return {
        "assets": round(assets, 2),

        "liabilities": round(liabilities, 2),

        "equity": round(equity, 2)
    }