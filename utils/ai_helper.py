import os
import json
import csv
import re

from utils.propradar import (
    get_suburb_stats,
    get_recent_sales,
    get_suburb_listings,
    get_suburb_price_history,
    get_market_cycle,
    get_suburb_rankings
)


UPLOAD_DIR = os.path.join("uploads", "ai")


def ensure_user_dir(user_id):

    path = os.path.join(
        UPLOAD_DIR,
        str(user_id)
    )

    os.makedirs(
        path,
        exist_ok=True
    )

    return path




def extract_text_from_file(path):

    lower = path.lower()

    try:

        if lower.endswith(".csv"):

            with open(
                path,
                newline="",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                reader = csv.reader(f)

                rows = list(reader)

                columns = rows[0] if rows else []

                sample = rows[1:6]

            return (
                f"CSV file '{os.path.basename(path)}' "
                f"with {len(rows) - 1} rows. "
                f"Columns: {columns}. "
                f"Sample rows: {sample}"
            )


        if lower.endswith(".json"):

            with open(
                path,
                encoding="utf-8",
                errors="ignore"
            ) as f:

                data = json.load(f)

            if isinstance(data, dict):

                keys = list(data.keys())

            else:

                keys = "array"


            return (
                f"JSON file '{os.path.basename(path)}' "
                f"with top-level keys: {keys}"
            )


        if lower.endswith(".txt") or lower.endswith(".md"):

            with open(
                path,
                encoding="utf-8",
                errors="ignore"
            ) as f:

                text = f.read(2000)

            return (
                f"Text file '{os.path.basename(path)}' "
                f"excerpt: {text[:1000]}"
            )


        with open(
            path,
            encoding="utf-8",
            errors="ignore"
        ) as f:

            text = f.read(2000)

        return (
            f"File '{os.path.basename(path)}' "
            f"excerpt: {text[:1000]}"
        )


    except Exception as e:

        return (
            f"Could not read file "
            f"{os.path.basename(path)}: {e}"
        )


# BUILD CONTEXT

def build_context(user_id, property_id=None):

    from database.models import (
        get_properties,
        get_property,
        get_property_income,
        get_property_expenses,
        get_report_transactions
    )

    context = []

    try:

        properties = get_properties(user_id)

        for property_row in properties:

            pid = property_row[0]

            if property_id and str(property_id) != str(pid):

                continue

            address = property_row[2] or pid

            property_type = property_row[3] or "Unknown"

            weekly_rent = property_row[9] or 0

            property_value = property_row[11] or 0

            purchase_price = property_row[12] or 0

            income = get_property_income(pid)

            expenses = get_property_expenses(pid)

            transactions = get_report_transactions(
                user_id,
                pid
            )

            net_profit = income - expenses

            if income > 0:

                profit_margin = (
                    net_profit / income
                ) * 100

            else:

                profit_margin = 0

            annual_rent = weekly_rent * 52

            if purchase_price > 0:

                rental_roi = (
                    (annual_rent - expenses)
                    / purchase_price
                ) * 100

            else:

                rental_roi = 0

            capital_growth = (
                property_value - purchase_price
            )

            if net_profit > 0:

                profitability = "Profitable"

            elif net_profit < 0:

                profitability = "Operating at a loss"

            else:

                profitability = "Break-even"


            text = f"""
PROPERTY: {address}

Property ID: {pid}
Property Type: {property_type}

Purchase Price: ${purchase_price:,.2f}
Current Property Value: ${property_value:,.2f}
Weekly Rent: ${weekly_rent:,.2f}
Estimated Annual Rent: ${annual_rent:,.2f}

Total Income: ${income:,.2f}
Total Expenses: ${expenses:,.2f}
Net Profit: ${net_profit:,.2f}

Profit Margin: {profit_margin:.2f}%
Rental ROI: {rental_roi:.2f}%

Capital Growth: ${capital_growth:,.2f}

Number of Transactions: {len(transactions)}

Profitability Status: {profitability}
""".strip()


            context.append({

                "source": "property",

                "id": pid,

                "text": text,

                "data": {

                    "address": address,

                    "income": income,

                    "expenses": expenses,

                    "net_profit": net_profit,

                    "profit_margin": profit_margin,

                    "rental_roi": rental_roi,

                    "capital_growth": capital_growth,

                    "purchase_price": purchase_price,

                    "property_value": property_value,

                    "weekly_rent": weekly_rent,

                    "transactions": len(transactions)

                }

            })

    except Exception as e:

        print(
            "AI PROPERTY CONTEXT ERROR:",
            e
        )

    return context


# FIND PROPERTY

def find_property(message, context):

    message_lower = message.lower()

    for item in context:

        if item.get("source") != "property":

            continue

        data = item.get("data", {})

        address = str(
            data.get("address", "")
        ).lower()

        pid = str(
            item.get("id", "")
        ).lower()

        if address and address in message_lower:

            return item

        if pid and pid in message_lower:

            return item

    return None




AUSTRALIAN_STATES = {

    "nsw": "NSW",
    "new south wales": "NSW",

    "vic": "VIC",
    "victoria": "VIC",

    "qld": "QLD",
    "queensland": "QLD",

    "sa": "SA",
    "south australia": "SA",

    "wa": "WA",
    "western australia": "WA",

    "tas": "TAS",
    "tasmania": "TAS",

    "act": "ACT",
    "australian capital territory": "ACT",

    "nt": "NT",
    "northern territory": "NT"
}


def detect_state(message):

    low = message.lower()

    for name, code in AUSTRALIAN_STATES.items():

        if re.search(
            r"\b" + re.escape(name) + r"\b",
            low
        ):

            return code


    location_defaults = {

        # NSW
        "sydney": "NSW",
        "parramatta": "NSW",
        "newcastle": "NSW",
        "wollongong": "NSW",

        # VIC
        "melbourne": "VIC",
        "richmond": "VIC",
        "pascoe vale": "VIC",
        "coburg": "VIC",
        "brunswick": "VIC",
        "footscray": "VIC",
        "preston": "VIC",
        "reservoir": "VIC",

        # QLD
        "brisbane": "QLD",
        "gold coast": "QLD",
        "sunshine coast": "QLD",

        # SA
        "adelaide": "SA",

        # WA
        "perth": "WA",

        # TAS
        "hobart": "TAS",

        # ACT
        "canberra": "ACT",

        # NT
        "darwin": "NT"
    }



    for location in sorted(
        location_defaults,
        key=len,
        reverse=True
    ):

        if re.search(
            r"\b" + re.escape(location) + r"\b",
            low
        ):

            return location_defaults[location]


    return None


def extract_suburb(message, state):

    if not state:

        return None

    low = message.lower()

    # Remove common question words.

    cleaned = re.sub(
        r"\b(what|is|are|the|median|house|unit|property|"
        r"price|prices|much|how|recent|sold|sales|"
        r"properties|currently|for|sale|in|of|"
        r"market|growth|has|have|been|"
        r"quickly|fast|selling|rental|yield)\b",
        " ",
        low
    )

    # Remove the state name.

    for name, code in AUSTRALIAN_STATES.items():

        if code == state:

            cleaned = re.sub(
                r"\b" + re.escape(name) + r"\b",
                " ",
                cleaned
            )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()

    if not cleaned:

        return None

    # Usually the remaining meaningful words form
    # the suburb.

    words = cleaned.split()

    if len(words) > 4:

        words = words[-3:]

    suburb = " ".join(words).strip()

    return suburb.title() if suburb else None


def format_currency(value):

    if value is None:

        return "N/A"

    try:

        return f"${float(value):,.0f}"

    except:

        return str(value)



def handle_market_question(message):

    low = message.lower()

    state = detect_state(message)

    if not state:

        return None


    suburb = extract_suburb(
        message,
        state
    )

    if not suburb:

        return (
            "I can search PropRadar for Australian property "
            "market information, but I need a suburb and state.\n\n"
            "For example:\n"
            "- What is the median house price in Richmond VIC?\n"
            "- What are recent house sales in Pascoe Vale VIC?"
        )



    if (
        "median" in low
        or "average house price" in low
        or "average property price" in low
        or "how much are houses" in low
        or "how much is a house" in low
        or "house prices" in low
    ):

        try:

            data = get_suburb_stats(
                state,
                suburb
            )

            print("PROPRADAR RAW SUBURB DATA:")
            print(json.dumps(data, indent=2))

            medians = data.get("medians", {})

            house_price = (
                medians.get("house_price")
                or medians.get("house")
                or data.get("median_house_price")
                or data.get("house_median")
            )

            unit_price = (
                medians.get("unit_price")
                or medians.get("unit")
                or data.get("median_unit_price")
                or data.get("unit_median")
            )

            if house_price is None:

                return (
                    f"PropRadar did not return a median house "
                    f"price for {suburb}, {state}."
                )


            return (

                f"### Property Prices – {suburb}, {state}\n\n"

                f"**Median house price:** "
                f"{format_currency(house_price)}\n\n"

                f"**Median unit price:** "
                f"{format_currency(unit_price)}\n\n"

                "This information was retrieved from "
                "PropRadar's suburb market data."
            )


        except Exception as e:

            print(
                "PROPRADAR MEDIAN ERROR:",
                e
            )

            return (
                f"I couldn't retrieve PropRadar's market "
                f"data for {suburb}, {state} right now."
            )


    if (
        "recent sales" in low
        or "recently sold" in low
        or "sold properties" in low
        or "recent sold" in low
    ):

        try:

            data = get_recent_sales(
                state,
                suburb,
                months=12,
                limit=10
            )

            sold = data.get(
                "sold",
                []
            )

            if not sold:

                return (
                    f"PropRadar did not return recent "
                    f"sold records for {suburb}, {state}."
                )


            response = (
                f"### Recent Property Sales – "
                f"{suburb}, {state}\n\n"
            )


            for property_item in sold:

                address = property_item.get(
                    "address",
                    "Unknown address"
                )

                price = property_item.get(
                    "sold_price"
                )

                date = property_item.get(
                    "sold_date",
                    "Unknown date"
                )

                property_type = property_item.get(
                    "property_type",
                    "Property"
                )

                response += (
                    f"**{address}**\n"
                    f"- Type: {property_type}\n"
                    f"- Sold for: {format_currency(price)}\n"
                    f"- Sold date: {date}\n\n"
                )


            return response


        except Exception as e:

            print(
                "PROPRADAR SALES ERROR:",
                e
            )

            return (
                f"I couldn't retrieve recent sales "
                f"for {suburb}, {state} from PropRadar."
            )



    if (
        "currently for sale" in low
        or "currently on the market" in low
        or "listings" in low
        or "properties for sale" in low
        or "houses for sale" in low
    ):

        try:

            data = get_suburb_listings(
                state,
                suburb,
                property_type="House",
                limit=10
            )

            listings = data.get(
                "listings",
                []
            )

            if not listings:

                return (
                    f"PropRadar did not return current "
                    f"house listings for {suburb}, {state}."
                )


            response = (
                f"### Houses Currently For Sale – "
                f"{suburb}, {state}\n\n"
            )


            for listing in listings:

                address = listing.get(
                    "address",
                    "Unknown address"
                )

                low_price = listing.get(
                    "asking_price_low"
                )

                high_price = listing.get(
                    "asking_price_high"
                )

                if low_price and high_price:

                    price = (
                        f"{format_currency(low_price)} – "
                        f"{format_currency(high_price)}"
                    )

                else:

                    price = format_currency(
                        low_price or high_price
                    )


                response += (
                    f"**{address}**\n"
                    f"- Asking price: {price}\n"
                    f"- Type: {listing.get('property_type', 'House')}\n"
                    f"- Bedrooms: {listing.get('bedrooms', 'N/A')}\n\n"
                )


            return response


        except Exception as e:

            print(
                "PROPRADAR LISTINGS ERROR:",
                e
            )

            return (
                f"I couldn't retrieve current listings "
                f"for {suburb}, {state} from PropRadar."
            )



    if (
        "growth" in low
        or "grown" in low
        or "increased" in low
        or "price change" in low
    ):

        try:

            data = get_suburb_stats(
                state,
                suburb
            )

            growth = data.get(
                "growth",
                {}
            )

            house_growth = growth.get(
                "house",
                {}
            )

            one_year = house_growth.get(
                "1y_pct"
            )

            five_year = house_growth.get(
                "5y_pct"
            )

            ten_year = house_growth.get(
                "10y_pct"
            )


            return (

                f"### House Price Growth – "
                f"{suburb}, {state}\n\n"

                f"- 1 year: **{one_year}%**\n"
                f"- 5 years: **{five_year}%**\n"
                f"- 10 years: **{ten_year}%**\n\n"

                "These figures come from PropRadar's "
                "suburb statistics."
            )


        except Exception as e:

            print(
                "PROPRADAR GROWTH ERROR:",
                e
            )

            return (
                f"I couldn't retrieve price growth "
                f"data for {suburb}, {state}."
            )



    if (
        "sell quickly" in low
        or "selling quickly" in low
        or "selling fast" in low
        or "days on market" in low
        or "how fast" in low
    ):

        try:

            data = get_suburb_stats(
                state,
                suburb
            )

            dynamics = data.get(
                "market_dynamics",
                {}
            )

            days = dynamics.get(
                "house_days_on_market"
            )


            return (

                f"### Selling Speed – "
                f"{suburb}, {state}\n\n"

                f"**Median days on market for houses:** "
                f"{days}\n\n"

                "A lower number generally indicates that "
                "properties are selling more quickly. "
                "This is based on PropRadar's suburb data."
            )


        except Exception as e:

            print(
                "PROPRADAR MARKET SPEED ERROR:",
                e
            )

            return (
                f"I couldn't retrieve selling-speed "
                f"data for {suburb}, {state}."
            )


    if (
        "rental yield" in low
        or "rental yields" in low
        or "yield" in low
    ):

        try:

            data = get_suburb_stats(
                state,
                suburb
            )

            yields = data.get(
                "yields",
                {}
            )

            house_yield = yields.get(
                "house_gross_pct"
            )

            unit_yield = yields.get(
                "unit_gross_pct"
            )


            return (

                f"### Rental Yield – "
                f"{suburb}, {state}\n\n"

                f"**House gross rental yield:** "
                f"{house_yield}%\n\n"

                f"**Unit gross rental yield:** "
                f"{unit_yield}%\n\n"

                "These are suburb-level figures from "
                "PropRadar."
            )


        except Exception as e:

            print(
                "PROPRADAR YIELD ERROR:",
                e
            )

            return (
                f"I couldn't retrieve rental-yield "
                f"data for {suburb}, {state}."
            )


    return None



def generate_property_analysis(property_data):

    address = property_data["address"]

    income = property_data["income"]

    expenses = property_data["expenses"]

    profit = property_data["net_profit"]

    margin = property_data["profit_margin"]

    rental_roi = property_data["rental_roi"]

    capital_growth = property_data["capital_growth"]

    transactions = property_data["transactions"]


    if profit > 0:

        status = "profitable"

        explanation = (
            "income exceeds recorded expenses"
        )

    elif profit < 0:

        status = "not currently profitable"

        explanation = (
            "recorded expenses exceed income"
        )

    else:

        status = "breaking even"

        explanation = (
            "income and expenses are equal"
        )


    response = (

        f"### {address} – Profitability Analysis\n\n"

        f"**Overall result:** "
        f"{address} is **{status}** based on the "
        f"financial records currently stored in OmniLedger.\n\n"

        f"**Financial performance**\n"
        f"- Total income: **${income:,.2f}**\n"
        f"- Total expenses: **${expenses:,.2f}**\n"
        f"- Net profit: **${profit:,.2f}**\n"
        f"- Profit margin: **{margin:.2f}%**\n\n"

        f"**Property performance**\n"
        f"- Rental ROI: **{rental_roi:.2f}%**\n"
        f"- Capital growth: **${capital_growth:,.2f}**\n"
        f"- Recorded transactions: **{transactions}**\n\n"

        f"**Why?**\n"
        f"The property is {status} because "
        f"{explanation}.\n\n"

        f"**Note:** This analysis is based only on "
        f"the financial information recorded in OmniLedger. "
        f"It should not be treated as professional financial advice."
    )

    return response



def generate_portfolio_analysis(context):

    properties = [

        item for item in context

        if item.get("source") == "property"

    ]

    if not properties:

        return (
            "There are no properties with available "
            "financial data to analyse."
        )


    total_income = sum(
        item["data"]["income"]
        for item in properties
    )

    total_expenses = sum(
        item["data"]["expenses"]
        for item in properties
    )

    total_profit = (
        total_income -
        total_expenses
    )


    best_property = max(
        properties,
        key=lambda x:
        x["data"]["net_profit"]
    )

    worst_property = min(
        properties,
        key=lambda x:
        x["data"]["net_profit"]
    )


    response = (

        "### Portfolio Financial Analysis\n\n"

        f"**Total income:** "
        f"${total_income:,.2f}\n\n"

        f"**Total expenses:** "
        f"${total_expenses:,.2f}\n\n"

        f"**Net portfolio profit:** "
        f"${total_profit:,.2f}\n\n"

        f"**Highest-performing property:** "
        f"{best_property['data']['address']} "
        f"with a net profit of "
        f"${best_property['data']['net_profit']:,.2f}.\n\n"

        f"**Lowest-performing property:** "
        f"{worst_property['data']['address']} "
        f"with a net profit of "
        f"${worst_property['data']['net_profit']:,.2f}.\n\n"

        f"OmniLedger analysed "
        f"{len(properties)} properties using "
        f"the financial records stored in the database."
    )

    return response



def generate_reply(message, context):

    message = (message or "").strip()

    if not message:

        return (
            "Please enter a question about your "
            "properties or financial records."
        )


    low = message.lower()


    print(
        "AI QUESTION:",
        message
    )

    print(
        "AI CONTEXT ITEMS:",
        len(context)
    )



    market_question = (

        "median" in low

        or "house price" in low

        or "house prices" in low

        or "property prices" in low

        or "recent sales" in low

        or "recently sold" in low

        or "sold properties" in low

        or "currently for sale" in low

        or "properties for sale" in low

        or "houses for sale" in low

        or "price growth" in low

        or "property growth" in low

        or "rental yield" in low

        or "sell quickly" in low

        or "days on market" in low

        or "selling fast" in low

    )


    if market_question:

        market_response = handle_market_question(
            message
        )

        if market_response:

            return market_response


    profitability_words = [

        "profitable",

        "profit",

        "making money",

        "worth it",

        "performing well",

        "performing poorly"

    ]


    if any(
        word in low
        for word in profitability_words
    ):

        property_item = find_property(
            message,
            context
        )


        if property_item:

            return generate_property_analysis(
                property_item["data"]
            )



    portfolio_words = [

        "portfolio",

        "all properties",

        "overall properties",

        "entire portfolio"

    ]


    if any(
        word in low
        for word in portfolio_words
    ):

        return generate_portfolio_analysis(
            context
        )



    if (

        "list properties" in low

        or low == "properties"

        or "show properties" in low

    ):

        properties = [

            item for item in context

            if item.get("source") == "property"

        ]


        if not properties:

            return (
                "No properties were found "
                "in your OmniLedger account."
            )


        response = "### Your Properties\n\n"


        for item in properties:

            data = item["data"]

            response += (

                f"**{data['address']}**\n"
                f"- Income: ${data['income']:,.2f}\n"
                f"- Expenses: ${data['expenses']:,.2f}\n"
                f"- Net profit: ${data['net_profit']:,.2f}\n\n"

            )


        return response




    if "income" in low:

        property_item = find_property(
            message,
            context
        )


        if property_item:

            data = property_item["data"]

            return (

                f"**{data['address']}** has recorded "
                f"income of **${data['income']:,.2f}** "
                f"in OmniLedger."
            )



    if "expense" in low or "expenses" in low:

        property_item = find_property(
            message,
            context
        )


        if property_item:

            data = property_item["data"]

            return (

                f"**{data['address']}** has recorded "
                f"expenses of **${data['expenses']:,.2f}** "
                f"in OmniLedger."
            )




    if "roi" in low:

        property_item = find_property(
            message,
            context
        )


        if property_item:

            data = property_item["data"]

            return (

                f"**{data['address']}** has a calculated "
                f"rental ROI of **{data['rental_roi']:.2f}%** "
                f"based on the current property and "
                f"transaction data."
            )



    property_item = find_property(
        message,
        context
    )


    if property_item:

        data = property_item["data"]

        return (

            f"I found **{data['address']}** in OmniLedger.\n\n"

            f"- Income: ${data['income']:,.2f}\n"
            f"- Expenses: ${data['expenses']:,.2f}\n"
            f"- Net profit: ${data['net_profit']:,.2f}\n"
            f"- Rental ROI: {data['rental_roi']:.2f}%\n"
            f"- Property value: "
            f"${data['property_value']:,.2f}"
        )



    property_count = len([

        item for item in context

        if item.get("source") == "property"

    ])


    file_count = len([

        item for item in context

        if item.get("source") == "file"

    ])


    return (

        "I couldn't identify a specific financial "
        "question from that message.\n\n"

        f"I currently have access to "
        f"**{property_count} properties** and "
        f"**{file_count} uploaded files**.\n\n"

        "Try asking something like:\n"
        "- Is Japan profitable?\n"
        "- What is the income for Japan?\n"
        "- What are the expenses for Japan?\n"
        "- What is the ROI for Japan?\n"
        "- Which properties are profitable?\n"
        "- Analyse my portfolio.\n"
        "- What is the median house price in Richmond VIC?\n"
        "- What are recent house sales in Pascoe Vale VIC?\n"
        "- What houses are currently for sale in Richmond VIC?\n"
        "- How quickly do houses sell in Sydney NSW?"
    )