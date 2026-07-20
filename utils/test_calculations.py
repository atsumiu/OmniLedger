# Purpose: tests financial calculation functions
from calculations import *


# EXAMPLE TRANSACTION DATA (transactionID, propertyID, type, amount, date)

transactions = [

    (1, "PROP001", "Income", 2500, "20/07/2026"),

    (2, "PROP001", "Expense", 500, "21/07/2026")

]



income = calculate_total_income(transactions)

expenses = calculate_total_expenses(transactions)

profit = calculate_net_profit(
    income,
    expenses
)



print("Total Income:")
print(income)


print("\nTotal Expenses:")
print(expenses)


print("\nNet Profit:")
print(profit)