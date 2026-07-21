# Purpose: test data and stuff
from models import *


# CREATE TEST USER

create_user(
    "test@email.com",
    "password123"
)




# CREATE TEST PROPERTY


create_property(
    "PROP001",
    "10 Example Street",
    "SSRK PTY LTD",
    "Test Tenant"
)




# CREATE TEST TRANSACTION (financial transaction storage)

create_transaction(

    "PROP001",

    "Income",

    2500,

    "20/07/2026",

    "Rent",

    "Monthly tenant payment",

    "receipt.pdf"

)




# DISPLAY DATABASE CONTENTS (records saved properly)

print("USERS:")

print(get_users())



print("\nPROPERTIES:")

print(get_properties())



print("\nTRANSACTIONS:")

print(get_transactions())



