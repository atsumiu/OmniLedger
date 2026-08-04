from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from utils.calculations import (
    calculate_rental_roi,
    calculate_total_roi
)
from database.models import (
    create_user,
    check_user,
    create_property,
    create_transaction,
    get_property,
    get_transactions,
    update_property,
    get_property_expenses,
    get_property_income
)

# CREATING FLASK
app = Flask(__name__)

# STORE LOGIN SESSION
app.secret_key = "omniledger_secret_key"


# LOGIN 

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":


        email = request.form["email"]

        password = request.form["password"]

        user = check_user(email, password)


        if user:


            session["logged_in"] = True
            session["userID"] = user["userID"]
            session["name"] = user["name"]
            session["email"] = user["email"]

            return redirect(url_for("dashboard"))


        else:

            flash("Incorrect email or password", "error")

            return redirect(url_for("login"))



    # SHOW LOGIN PAGE

    return render_template("login.html")


# DASHBOARD
# DASHBOARD
@app.route("/dashboard")
def dashboard():

    from database.models import (
        get_properties,
        get_total_income,
        get_total_expenses,
        get_net_profit
    )

    userID = session["userID"]

    properties = get_properties(userID)

    total_income = get_total_income(userID)

    total_expenses = get_total_expenses(userID)

    net_profit = get_net_profit(userID)


    return render_template(
        "dashboard.html",
        properties=properties,
        totalIncome=total_income,
        totalExpenses=total_expenses,
        netProfit=net_profit
    )



# PROPERTY DETAILS
@app.route("/property/<propertyID>")
def property_details(propertyID):

    property = get_property(propertyID)

    if property is None:
        return redirect(url_for("dashboard"))

    transactions = get_transactions(propertyID)

    total_income = get_property_income(propertyID)

    total_expenses = get_property_expenses(propertyID)

    net_profit = total_income - total_expenses


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


    return render_template(
        "property_details.html",
        property=property,
        transactions=transactions,
        rentalROI=rentalROI,
        totalROI=totalROI,
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=net_profit
    )



# LOGOUT

@app.route("/logout")

def logout():

    # REMOVE USER LOGIN SESSION

    session.clear()


    # RETURN TO LOGIN PAGE

    return redirect(url_for("login"))


# CREATE ACCOUNT

@app.route("/create-account", methods=["GET", "POST"])

def create_account():


    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]


        create_user(name, email, password)


        return redirect(url_for("login"))



    return render_template("create_account.html")


# ADD PROPERTY

@app.route("/add_property", methods=["GET", "POST"])
def add_property():


    if request.method == "POST":


        # BASIC INFORMATION

        address = request.form["propertyAddress"].strip()

        propertyType = request.form["propertyType"]

        ownership = request.form["ownershipData"].strip()



        # VALIDATION - REQUIRED FIELDS

        if not address or not ownership:

            flash("Property address and ownership are required.", "error")

            return redirect(url_for("add_property"))




        # TENANT AND LEASE INFORMATION

        tenantName = request.form["tenantName"].strip()

        leaseStatus = request.form["leaseStatus"]

        leaseStart = request.form["leaseStart"]

        leaseEnd = request.form["leaseEnd"]




        # CHECK LEASE DATES

        if leaseStart and leaseEnd:

            start = datetime.strptime(leaseStart, "%Y-%m-%d")

            end = datetime.strptime(leaseEnd, "%Y-%m-%d")


            if end < start:

                flash("Lease end date cannot be before lease start date.", "error")

                return redirect(url_for("add_property"))




        # FINANCIAL INFORMATION (OPTIONAL)

        try:

            weeklyRent = float(request.form.get("weeklyRent", 0) or 0)

            propertyValue = float(request.form.get("propertyValue", 0) or 0)

            purchasePrice = float(request.form.get("purchasePrice", 0) or 0)


        except ValueError:

            flash("Financial values must only contain numbers.", "error")

            return redirect(url_for("add_property"))




        # CHECK NEGATIVE VALUES


        if weeklyRent < 0 or propertyValue < 0 or purchasePrice < 0:

            flash("Financial values cannot be negative.", "error")

            return redirect(url_for("add_property"))



        bankAccount = request.form.get("bankAccount", "").strip()

        notes = request.form.get("notes", "").strip()


        # CURRENT USER

        userID = session["userID"]




        # SAVE PROPERTY


        propertyID =create_property(

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



        flash("Property successfully added!", "success")

        return redirect(url_for("dashboard"))



    # SHOW ADD PROPERTY PAGE

    return render_template("add_property.html")


# EDIT PROPERTY

@app.route("/edit_property/<propertyID>", methods=["GET", "POST"])
def edit_property(propertyID):


    property = get_property(propertyID)


    if request.method == "POST":


        propertyAddress = request.form["propertyAddress"]

        propertyType = request.form["propertyType"]

        ownershipData = request.form["ownershipData"]

        tenantName = request.form["tenantName"]

        leaseStatus = request.form["leaseStatus"]

        leaseStart = request.form["leaseStart"]

        leaseEnd = request.form["leaseEnd"]

        weeklyRent = request.form["weeklyRent"]

        bankAccount = request.form["bankAccount"]

        propertyValue = request.form["propertyValue"]

        purchasePrice = request.form["purchasePrice"]

        notes = request.form["notes"]



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


        flash("Property updated successfully!", "success")


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

@app.route("/add_transaction/<propertyID>", methods=["GET", "POST"])
def add_transaction(propertyID):


    if request.method == "POST":


        transactionType = request.form["transactionType"]

        category = request.form["category"]

        amount = float(request.form["amount"])

        date = request.form["date"]

        paymentMethod = request.form["paymentMethod"]

        description = request.form["description"]



        create_transaction(

            propertyID,

            transactionType,

            category,

            amount,

            date,

            paymentMethod,

            description,

            None

        )


        flash("Transaction successfully added!", "success")


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


# RUN WEBSITE
if __name__ == "__main__":
    app.run(debug=True)



