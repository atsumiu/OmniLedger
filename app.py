from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from database.models import create_user, check_user, create_property, create_transaction


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


#DASHBOARD
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


    totalIncome = get_total_income(userID)

    totalExpenses = get_total_expenses(userID)

    netProfit = get_net_profit(userID)



    return render_template(

        "dashboard.html",

        properties=properties,

        totalIncome=totalIncome,

        totalExpenses=totalExpenses,

        netProfit=netProfit

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




        # FINANCIAL INFORMATION


        try:

            weeklyRent = float(request.form["weeklyRent"] or 0)

            propertyValue = float(request.form["propertyValue"] or 0)

            purchasePrice = float(request.form["purchasePrice"] or 0)


        except ValueError:

            flash("Financial values must only contain numbers.", "error")

            return redirect(url_for("add_property"))




        # CHECK NEGATIVE VALUES


        if weeklyRent < 0 or propertyValue < 0 or purchasePrice < 0:

            flash("Financial values cannot be negative.", "error")

            return redirect(url_for("add_property"))





        bankAccount = request.form["bankAccount"].strip()

        notes = request.form["notes"].strip()

        transactionType = request.form["transactionType"]

        transactionCategory = request.form["transactionCategory"]

        transactionDate = request.form["transactionDate"]

        transactionDescription = request.form["transactionDescription"].strip()


        try:

            transactionAmount = float(request.form["transactionAmount"] or 0)


        except ValueError:

            flash("Transaction amount must be a number.", "error")

            return redirect(url_for("add_property"))




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


        if transactionAmount > 0:


            create_transaction(

                propertyID,

                transactionType,

                transactionCategory,

                transactionAmount,

                transactionDate,

                bankAccount,

                transactionDescription,

                ""

            )



        flash("Property successfully added!", "success")

        return redirect(url_for("dashboard"))



    




    return render_template("add_property.html")


# RUN WEBSITE
if __name__ == "__main__":
    app.run(debug=True)



