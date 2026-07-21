# IMPORT FLASK
from flask import Flask, render_template, request, redirect, url_for, session


# CREATING FLASK
app = Flask(__name__)

# STORE LOGIN SESSION
app.secret_key = "omniledger_secret_key"


# TEMP USER ACCOUNT
USER_EMAIL = "admin@omniledger.com"
USER_PASSWORD = "12345"


# LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():

    # WHEN LOGIN BUTTON IS PRESSED
    if request.method == "POST":

        # GET INFORMATION TYPED IN
        email = request.form["email"]
        password = request.form["password"]


        # CHECK IF DETAILS MATCH
        if email == USER_EMAIL and password == USER_PASSWORD:

            # SAVE LOGIN STATUSS
            session["logged_in"] = True

            # SEND TO DASHBOARD
            return redirect(url_for("dashboard"))


        else:
            return "Incorrect email or password"


    # SHOW LOGIN PAGE
    return render_template("login.html")



# TEMP DASHBOARD PAGE
@app.route("/dashboard")
def dashboard():

    # PREVENT ACCESS WITHOUT LOGIN
    if "logged_in" not in session:
        return redirect(url_for("login"))


    return render_template("dashboard.html")



# RUN WEBSITE
if __name__ == "__main__":
    app.run(debug=True)