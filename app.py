from flask import Flask, render_template, request, redirect, url_for, session, flash

from database.models import create_user, check_user


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

            session["email"] = user["email"]

            session["name"] = user["name"]


            return redirect(url_for("dashboard"))


        else:

            flash("Incorrect email or password")

            return redirect(url_for("login"))



    # SHOW LOGIN PAGE

    return render_template("login.html")



# DASHBOARD PAGE
@app.route("/dashboard")
def dashboard():

    # PREVENT ACCESS WITHOUT LOGIN
    if "logged_in" not in session:
        return redirect(url_for("login"))


    return render_template("dashboard.html")



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



# RUN WEBSITE
if __name__ == "__main__":
    app.run(debug=True)


