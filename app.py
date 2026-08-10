from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from datetime import datetime

import os

from werkzeug.utils import secure_filename


from utils.report_generator import (
    create_financial_report,
    generate_and_save_report
)


from utils.calculations import (
    calculate_rental_roi,
    calculate_total_roi
)


from database.models import (
    create_user,
    check_user,

    create_property,
    get_property,
    get_properties,
    update_property,

    create_transaction,
    get_transactions,

    get_property_income,
    get_property_expenses,

    get_reports,
    get_report
)




app = Flask(__name__)

app.secret_key = "omniledger_secret_key"


# LOGIN

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = check_user(
            email,
            password
        )


        if user:

            session["logged_in"] = True

            session["userID"] = user["userID"]

            session["name"] = user["name"]

            session["email"] = user["email"]

            return redirect(
                url_for("dashboard")
            )


        else:

            flash(
                "Incorrect email or password",
                "error"
            )

            return redirect(
                url_for("login")
            )


    return render_template(
        "login.html"
    )


# DASHBOARD

@app.route("/dashboard")
def dashboard():

    # Make sure user is logged in

    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    userID = session["userID"]


    # Import financial functions here

    from database.models import (
        get_total_income,
        get_total_expenses,
        get_net_profit
    )


    properties = get_properties(
        userID
    )


    total_income = get_total_income(
        userID
    )


    total_expenses = get_total_expenses(
        userID
    )


    net_profit = get_net_profit(
        userID
    )


    return render_template(

        "dashboard.html",

        properties=properties,

        totalIncome=total_income,

        totalExpenses=total_expenses,

        netProfit=net_profit
    )


# REPORTS
@app.route("/reports")
def reports():

    userID = session["userID"]

    properties = get_properties(userID)

    reports = get_reports(userID)

    return render_template(
        "reports.html",
        properties=properties,
        reports=reports,
        totalIncome=0,
        totalExpense=0,
        netProfit=0
    )


# GENERATE REPORT

@app.route(
    "/generate_report",
    methods=["POST"]
)
def generate_report():

    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    userID = session["userID"]


    reportType = request.form.get(
        "reportType",
        "Financial Summary"
    )


    propertyID = request.form.get("property")


    startDate = request.form.get(
        "startDate"
    )


    endDate = request.form.get(
        "endDate"
    )


    # VALIDATE DATE

    if startDate and endDate:

        try:

            start = datetime.strptime(
                startDate,
                "%Y-%m-%d"
            )

            end = datetime.strptime(
                endDate,
                "%Y-%m-%d"
            )


            if end < start:

                flash(
                    "End date cannot be before start date.",
                    "error"
                )

                return redirect(
                    url_for("reports")
                )


        except ValueError:

            flash(
                "Invalid report dates.",
                "error"
            )

            return redirect(
                url_for("reports")
            )


    # VALIDATE PROP

    if propertyID != "all":

        selected_property = get_property(
            propertyID,
            userID
        )


        if selected_property is None:

            flash(
                "Selected property could not be found.",
                "error"
            )

            return redirect(
                url_for("reports")
            )


    # GENERATE & SAVE REPORT

    report_data = generate_and_save_report(

        userID,

        reportType,

        propertyID,

        startDate,

        endDate
    )


    properties = get_properties(
        userID
    )


    saved_reports = get_reports(
        userID
    )


    # SHOW REPORT

    return render_template(

        "reports.html",

        properties=properties,

        reports=saved_reports,

        report=report_data,

        totalIncome=report_data["totalIncome"],

        totalExpenses=report_data["totalExpenses"],

        netProfit=report_data["netProfit"],

        gst=report_data["gst"],

        rentalROI=report_data["rentalROI"],

        totalROI=report_data["totalROI"],

        cashFlow=report_data["cashFlow"],

        balanceSheet=report_data["balanceSheet"],

        incomeBreakdown=report_data["incomeBreakdown"],

        expenseBreakdown=report_data["expenseBreakdown"],

        transactions=report_data["transactions"],

        propertyInformation=report_data[
            "propertyInformation"
        ],

        propertyID=propertyID,

        reportType=reportType,

        startDate=startDate,

        endDate=endDate
    )


# VIEW REPORT

@app.route("/report/<int:reportID>")
def view_report(reportID):

    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    userID = session["userID"]


    report = get_report(
        reportID,
        userID
    )


    if report is None:

        flash(
            "Report could not be found.",
            "error"
        )

        return redirect(
            url_for("reports")
        )


    properties = get_properties(
        userID
    )


    saved_reports = get_reports(
        userID
    )


    return render_template(

        "reports.html",

        properties=properties,

        reports=saved_reports,

        savedReport=report
    )

#REPORT PREVIEW
@app.route("/report_preview", methods=["POST"])
def report_preview():

    userID = session["userID"]

    reportType = request.form.get("reportType")
    propertyID = request.form.get("property")
    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")

    report_data = create_financial_report(
        userID,
        reportType,
        propertyID,
        startDate,
        endDate
    )

    return jsonify({
        "totalIncome": report_data["totalIncome"],
        "totalExpenses": report_data["totalExpenses"],
        "netProfit": report_data["netProfit"],
        "totalBills": report_data["totalBills"],
        "gst": report_data["gst"],
        "rentalROI": report_data["rentalROI"],
        "totalROI": report_data["totalROI"],
        "cashFlow": report_data["cashFlow"],
        "balanceSheet": report_data["balanceSheet"],
        "incomeBreakdown": report_data["incomeBreakdown"],
        "expenseBreakdown": report_data["expenseBreakdown"],
        "transactionCount": len(report_data["transactions"])
    })

# PROPERTY DETAILS

@app.route("/property/<propertyID>")
def property_details(propertyID):

    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    userID = session["userID"]


    # Make sure property belongs to logged-in user

    property = get_property(
        propertyID,
        userID
    )


    if property is None:

        return redirect(
            url_for("dashboard")
        )


    transactions = get_transactions(
        propertyID
    )


    total_income = get_property_income(
        propertyID
    )


    total_expenses = get_property_expenses(
        propertyID
    )


    net_profit = (
        total_income
        - total_expenses
    )


    rentalROI = calculate_rental_roi(

        property["weeklyRent"] or 0,

        total_expenses,

        property["purchasePrice"] or 0
    )


    totalROI = calculate_total_roi(

        property["propertyValue"] or 0,

        property["purchasePrice"] or 0,

        property["weeklyRent"] or 0,

        total_expenses
    )


    # EXPENSE GRAPH DATA

    expense_labels = [

        transaction[3]

        for transaction in transactions

        if transaction[2] == "Expense"
    ]


    expense_amounts = [

        transaction[4]

        for transaction in transactions

        if transaction[2] == "Expense"
    ]


    has_expense_data = bool(
        expense_labels
    )


    return render_template(

        "property_details.html",

        property=property,

        transactions=transactions,

        total_income=total_income,

        total_expenses=total_expenses,

        net_profit=net_profit,

        rentalROI=rentalROI,

        totalROI=totalROI,

        expense_labels=expense_labels,

        expense_amounts=expense_amounts,

        has_expense_data=has_expense_data
    )


# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# CREATE ACCOUNT

@app.route(
    "/create-account",
    methods=["GET", "POST"]
)
def create_account():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]


        create_user(
            name,
            email,
            password
        )


        return redirect(
            url_for("login")
        )


    return render_template(
        "create_account.html"
    )


# ADD PROPERTY

@app.route(
    "/add_property",
    methods=["GET", "POST"]
)
def add_property():

    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        # BASIC INFO

        address = request.form[
            "propertyAddress"
        ].strip()


        propertyType = request.form[
            "propertyType"
        ]


        ownership = request.form[
            "ownershipData"
        ].strip()


        # REQUIRED FIELDS

        if not address or not ownership:

            flash(
                "Property address and ownership are required.",
                "error"
            )

            return redirect(
                url_for("add_property")
            )


        tenantName = request.form[
            "tenantName"
        ].strip()


        leaseStatus = request.form[
            "leaseStatus"
        ]


        leaseStart = request.form[
            "leaseStart"
        ]


        leaseEnd = request.form[
            "leaseEnd"
        ]


        # LEASE DATES

        if leaseStart and leaseEnd:

            start = datetime.strptime(
                leaseStart,
                "%Y-%m-%d"
            )


            end = datetime.strptime(
                leaseEnd,
                "%Y-%m-%d"
            )


            if end < start:

                flash(
                    "Lease end date cannot be before lease start date.",
                    "error"
                )

                return redirect(
                    url_for("add_property")
                )


        try:

            weeklyRent = float(
                request.form.get(
                    "weeklyRent",
                    0
                ) or 0
            )


            propertyValue = float(
                request.form.get(
                    "propertyValue",
                    0
                ) or 0
            )


            purchasePrice = float(
                request.form.get(
                    "purchasePrice",
                    0
                ) or 0
            )


        except ValueError:

            flash(
                "Financial values must only contain numbers.",
                "error"
            )

            return redirect(
                url_for("add_property")
            )


        if (
            weeklyRent < 0
            or propertyValue < 0
            or purchasePrice < 0
        ):

            flash(
                "Financial values cannot be negative.",
                "error"
            )

            return redirect(
                url_for("add_property")
            )


        bankAccount = request.form.get(
            "bankAccount",
            ""
        ).strip()


        notes = request.form.get(
            "notes",
            ""
        ).strip()


        userID = session["userID"]



        propertyID = create_property(

            userID,

            address,

            propertyType,

            ownership,

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


        flash(
            "Property successfully added!",
            "success"
        )


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "add_property.html"
    )


# EDIT PROPERTY

@app.route(
    "/edit_property/<propertyID>",
    methods=["GET", "POST"]
)
def edit_property(propertyID):

    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    userID = session["userID"]


    property = get_property(
        propertyID,
        userID
    )


    if property is None:

        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":

        propertyAddress = request.form[
            "propertyAddress"
        ]


        propertyType = request.form[
            "propertyType"
        ]


        ownershipData = request.form[
            "ownershipData"
        ]


        tenantName = request.form[
            "tenantName"
        ]


        leaseStatus = request.form[
            "leaseStatus"
        ]


        leaseStart = request.form[
            "leaseStart"
        ]


        leaseEnd = request.form[
            "leaseEnd"
        ]


        weeklyRent = request.form[
            "weeklyRent"
        ]


        bankAccount = request.form[
            "bankAccount"
        ]


        propertyValue = request.form[
            "propertyValue"
        ]


        purchasePrice = request.form[
            "purchasePrice"
        ]


        notes = request.form[
            "notes"
        ]


        update_property(

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
        )


        flash(
            "Property updated successfully!",
            "success"
        )


        return redirect(

            url_for(

                "property_details",

                propertyID=propertyID
            )
        )


    return render_template(

        "edit_property.html",

        property=property
    )


# ADD TRANSACTION

@app.route(
    "/add_transaction/<propertyID>",
    methods=["GET", "POST"]
)
def add_transaction(propertyID):

    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    userID = session["userID"]


    property = get_property(
        propertyID,
        userID
    )


    if property is None:

        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":

        transactionType = request.form[
            "transactionType"
        ]


        category = request.form[
            "category"
        ]


        try:

            amount = float(
                request.form["amount"]
            )

        except ValueError:

            flash(
                "Transaction amount must be a number.",
                "error"
            )

            return redirect(
                url_for(
                    "add_transaction",
                    propertyID=propertyID
                )
            )


        if amount < 0:

            flash(
                "Transaction amount cannot be negative.",
                "error"
            )

            return redirect(
                url_for(
                    "add_transaction",
                    propertyID=propertyID
                )
            )


        date = request.form[
            "date"
        ]


        paymentMethod = request.form[
            "paymentMethod"
        ]


        description = request.form[
            "description"
        ]


        attachment = None


        # UPLOAD RECEIPTS

        receipt = request.files.get(
            "receipt"
        )


        if receipt and receipt.filename:

            filename = secure_filename(
                receipt.filename
            )


            upload_folder = os.path.join(
                "static",
                "uploads",
                "receipts"
            )


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            filepath = os.path.join(
                upload_folder,
                filename
            )


            receipt.save(
                filepath
            )


            attachment = filename


        # SAVE TRANSACTION

        create_transaction(

            propertyID,

            transactionType,

            category,

            amount,

            date,

            paymentMethod,

            description,

            attachment
        )


        flash(
            "Transaction successfully added!",
            "success"
        )


        return redirect(

            url_for(

                "property_details",

                propertyID=propertyID
            )
        )


    return render_template(

        "add_transaction.html",

        propertyID=propertyID
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )