# Purpose: put dif parts of code together

# IMPORT REPORT GENERATOR FUNCTION

from utils.report_generator import generate_report




# START APPLICATION


print("Starting OmniLedger...")


# GENERATE A REPORT

generate_report()


print("OmniLedger finished.")

# FLASK SETUP

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():

    return "Welcome to OmniLedger"


if __name__ == "__main__":
    app.run(debug=True)