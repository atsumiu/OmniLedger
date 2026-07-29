from flask import Flask, render_template, request, redirect, url_for, session, flash

from database.models import create_user, check_user, create_property


# CREATING FLASK
app = Flask(__name__)

# STORE LOGIN SESSION
app.secret_key = "omniledger_secret_key"




# LOGIN 

@app.route("/", methods=["GET", "POST"])
def login():

    # WHEN LOGIN BUTTON IS PRESSED
    if request.method == "POST":

        # GET INFORMATION TYPED IN

        email = request.form["email"]

        password = request.form["password"]


        # CHECK DATABASE FOR USER

        user = check_user(email, password)


        if user:


            session["logged_in"] = True
            session["userID"] = user["userID"]
            session["name"] = user["name"]
            session["email"] = user["email"]

            return redirect(url_for("dashboard"))


        else:

            flash("Incorrect email or password")

            return redirect(url_for("login"))



    # SHOW LOGIN PAGE

    return render_template("login.html")


#DASHBOARD
@app.route("/dashboard")
def dashboard():

    from database.models import get_properties


    properties = get_properties(session["userID"])


    return render_template(
        "dashboard.html",
        properties=properties
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


        address = request.form["propertyAddress"]

        ownership = request.form["ownershipData"]

        tenant = request.form["tenantInfo"]



        userID = session["userID"]



        create_property(

            userID,

            address,

            ownership,

            tenant

        )



        return redirect(url_for("dashboard"))



    return render_template("add_property.html")


# RUN WEBSITE
if __name__ == "__main__":
    app.run(debug=True)


