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




# CALCULATE ROI (return generated from a property)

def calculate_roi(net_profit, property_value):


    # Prevent division by zero

    if property_value == 0:

        return 0



    roi = (net_profit / property_value) * 100


    return roi