from database.models import (
    get_report_transactions,
    create_report
)

from utils.calculations import (
    calculate_rental_roi,
    calculate_total_roi,
    calculate_cash_flow,
    calculate_total_bills
)

def create_financial_report(
    userID,
    reportType,
    propertyID,
    startDate,
    endDate
):


    transactions = get_report_transactions(
        userID,
        propertyID,
        startDate,
        endDate
    )


    total_income = 0
    total_expenses = 0
    total_bills = calculate_total_bills(transactions)
    total_gst = 0

    income_breakdown = {}
    expense_breakdown = {}


    # TRANSACTIONS

    for transaction in transactions:

        transaction_type = transaction[2]
        category = transaction[3]
        amount = transaction[4]
        gst_value = transaction[9] or 0


        if transaction_type == "Income":

            total_income += amount

            if category not in income_breakdown:
                income_breakdown[category] = 0

            income_breakdown[category] += amount


        elif transaction_type == "Expense":

            total_expenses += amount

            if category not in expense_breakdown:
                expense_breakdown[category] = 0

            expense_breakdown[category] += amount



        total_gst += gst_value


    # PROFIT

    net_profit = total_income - total_expenses


    # PROPETTY & ROI DATA

    property_information = None
    rental_roi = 0
    total_roi = 0


    if propertyID and propertyID != "all":

        from database.models import get_property

        property_information = get_property(
            propertyID,
            userID
        )

        if property_information:


            weekly_rent = property_information[9] or 0
            property_value = property_information[11] or 0
            purchase_price = property_information[12] or 0

            rental_roi = calculate_rental_roi(
                weekly_rent,
                total_expenses,
                purchase_price
            )

            total_roi = calculate_total_roi(
                property_value,
                purchase_price,
                weekly_rent,
                total_expenses
            )


    cash_flow = calculate_cash_flow(transactions)


    # BALANCE SHEET

    assets = 0
    liabilities = 0
    equity = 0

    if property_information:

        property_value = property_information[11] or 0
        purchase_price = property_information[12] or 0

        assets = property_value

        liabilities = purchase_price

        equity = assets - liabilities

    balance_sheet = {

        "assets": round(assets, 2),

        "liabilities": round(liabilities, 2),

        "equity": round(equity, 2)

    }


    # REPORT DATA

    report_data = {

        "reportType": reportType,

        "propertyID": propertyID,

        "startDate": startDate,

        "endDate": endDate,

        "transactions": transactions,

        "totalIncome": total_income,

        "totalExpenses": total_expenses,

        "totalBills": total_bills,

        "netProfit": net_profit,

        "gst": total_gst,

        "rentalROI": rental_roi,

        "totalROI": total_roi,

        "cashFlow": cash_flow,

        "balanceSheet": balance_sheet,

        "assets": assets,

        "liabilities": liabilities,

        "equity": equity,

        "incomeBreakdown": income_breakdown,

        "expenseBreakdown": expense_breakdown,

        "propertyInformation": property_information
    }


    return report_data


# SAVE REPORT AND GENERATE

def generate_and_save_report(
    userID,
    reportType,
    propertyID,
    startDate,
    endDate
):

    report_data = create_financial_report(
        userID,
        reportType,
        propertyID,
        startDate,
        endDate
    )


    # SAVE TO DATABASE

    reportID = create_report(
        userID=userID,
        reportType=reportType,
        startDate=startDate,
        endDate=endDate,
        totalIncome=report_data["totalIncome"],
        totalExpense=report_data["totalExpenses"],
        totalBills=report_data["totalBills"],
        netProfit=report_data["netProfit"],
        roi=report_data["totalROI"],
        propertyID=propertyID,
        predictedInsights=""
    )


    report_data["reportID"] = reportID


    return report_data