# Purpose: financial calculation functions.



# CALCULATE TOTAL INCOME

def calculate_total_income(transactions):

    total_income = 0


    # LOOP THROUGH EVERY TRANSACTION

    for transaction in transactions:


        # TRANSACTION TYPE IS AT INDEX 2
        # AMOUNT IS AT INDEX 3

        if transaction[2] == "Income":

            total_income += transaction[3]


    return total_income






# CALCULATE TOTAL EXPENSES

def calculate_total_expenses(transactions):

    total_expenses = 0


    # LOOP THROUGH EVERY TRANSACTION

    for transaction in transactions:


        # CHECK IF TRANSACTION IS AN EXPENSE

        if transaction[2] == "Expense":

            total_expenses += transaction[3]


    return total_expenses






# CALCULATE NET PROFIT ()

def calculate_net_profit(total_income, total_expenses):

    net_profit = total_income - total_expenses


    return net_profit


# ROI CALCULATIONS

def calculate_rental_roi(weeklyRent, totalExpenses, purchasePrice):

    annualIncome = weeklyRent * 52

    if purchasePrice == 0:
        return 0

    roi = ((annualIncome - totalExpenses) / purchasePrice) * 100

    return round(roi, 2)



def calculate_total_roi(propertyValue, purchasePrice, weeklyRent, totalExpenses):

    annualIncome = weeklyRent * 52

    if purchasePrice == 0:
        return 0

    netRentalIncome = annualIncome - totalExpenses

    roi = ((propertyValue - purchasePrice + netRentalIncome) / purchasePrice) * 100

    return round(roi, 2)