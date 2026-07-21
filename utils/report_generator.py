# Purpose: generate the financial reports 




# IMPORT DATABASE


from database.models import (
    get_transactions,
    create_report
)

from utils.calculations import (
    calculate_total_income,
    calculate_total_expenses,
    calculate_net_profit,
    calculate_roi
)




# GENERATE REPORT

def generate_report():

    
    # GET ALL TRANSACTIONS
    

    transactions = get_transactions()



    
    # CALCULATIONS
    

    total_income = calculate_total_income(transactions)

    total_expenses = calculate_total_expenses(transactions)

    net_profit = calculate_net_profit(
        total_income,
        total_expenses
    )


    # TEMP PROPERTY VALUE (get from database later)
    

    property_value = 500000


    roi = calculate_roi(
        net_profit,
        property_value
    )



    
    # STORE GENERATED REPORT
    

    create_report(

        "Monthly Financial Report",

        "01/07/2026",

        "31/07/2026",

        total_income,

        total_expenses,

        total_expenses,

        net_profit,

        roi,

        "Financial report generated automatically."

    )



    print("Report successfully generated.")

