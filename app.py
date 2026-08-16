from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    send_file
)

from utils.ai_helper import (
    ensure_user_dir,
    extract_text_from_file,
    build_context,
    generate_reply
)

from utils.propradar import search_omniledger_property

from datetime import datetime
import os
from werkzeug.utils import secure_filename
import requests
import time

from utils.pdf_generator import generate_report_pdf


from utils.report_generator import (
    create_financial_report,
    generate_and_save_report
)


from utils.calculations import (
    calculate_rental_roi,
    calculate_total_roi
)
from utils.ai_helper import (
    ensure_user_dir,
    extract_text_from_file,
    build_context,
    generate_reply
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
    get_report,
    get_report_transactions,
    get_total_income,
    get_total_expenses,
    get_net_profit
)


app = Flask(__name__)
app.secret_key = "omniledger_secret_key"

def load_openai_key():
    try:
        key_file = os.path.join('instance', 'ai_key.txt')
        if os.path.isfile(key_file):
            with open(key_file, 'r', encoding='utf-8') as f:
                k = f.read().strip()
                if k:
                    os.environ['OPENAI_API_KEY'] = k
    except Exception:
        pass

load_openai_key()


DOMAIN_BASE = os.environ.get("DOMAIN_BASE", "https://api.domain.com.au")
DOMAIN_KEY = os.environ.get("DOMAIN_API_KEY")
DOMAIN_CACHE = {}
DOMAIN_CACHE_TTL = 3600  

def domain_get(path, params=None):

    headers = {}

    if DOMAIN_KEY:

        headers["X-API-Key"] = DOMAIN_KEY

    resp = requests.get(DOMAIN_BASE + path, headers=headers, params=params, timeout=10)

    resp.raise_for_status()

    return resp.json()


@app.route('/api/domain/suburb/<state>/<suburb>')
def domain_suburb(state, suburb):

    key = ("suburb:" + state + ":" + suburb).lower()

    now = time.time()

    cached = DOMAIN_CACHE.get(key)

    if cached and (now - cached[0]) < DOMAIN_CACHE_TTL:
        return jsonify(cached[1])

    try:
        data = domain_get("/v2/suburbPerformanceStatistics/" + state + "/" + suburb)

    except requests.HTTPError as e:
        return jsonify({'error': 'domain api error', 'details': str(e)}), 502

    DOMAIN_CACHE[key] = (now, data)

    return jsonify(data)


@app.route('/api/market/local/<state>/<suburb>')
def market_local(state, suburb):
    if 'userID' not in session:
        return jsonify({'error':'not authenticated'}), 401

    userID = session['userID']

    from datetime import date, timedelta

    today = date.today()
    months = []
    for i in range(11, -1, -1):
        m = (today.replace(day=1) - timedelta(days= i*30))
        months.append(m.strftime('%Y-%m'))

    income_series = {m:0 for m in months}
    expense_series = {m:0 for m in months}

    props = get_properties(userID)
    matching = []
    for p in props:
        addr = (p['propertyAddress'] or '').lower()
        if suburb.lower() in addr:
            matching.append(p['propertyID'])

    if not matching:
        return jsonify({'source':'local','message':'no properties match this suburb','periods':months,'income':list(income_series.values()),'expenses':list(expense_series.values())})

    for pid in matching:
        txs = get_report_transactions(userID, pid)
        for t in txs:
            ds = t[5]
            ym = None
            try:
                if len(ds) >= 10 and ds[4] == '-':
                    ym = ds[:7]
                elif len(ds) >= 10 and ds[2] == '-':
                    parts = ds.split('-')
                    ym = parts[2] + "-" + parts[1]
            except Exception:
                ym = None
            if ym and ym in income_series:
                if t[2] == 'Income':
                    income_series[ym] += t[4]
                elif t[2] == 'Expense':
                    expense_series[ym] += t[4]

    return jsonify({
        'source':'local',
        'periods': months,
        'income': [round(income_series[m],2) for m in months],
        'expenses': [round(expense_series[m],2) for m in months]
    })


@app.route('/api/domain/address')
def domain_address():
    q = request.args.get('q') or request.args.get('query')
    if not q:
        return jsonify({'error':'missing query'}), 400

    key = "addr:" + q.lower()
    now = time.time()
    cached = DOMAIN_CACHE.get(key)
    if cached and (now - cached[0]) < DOMAIN_CACHE_TTL:
        return jsonify(cached[1])

    try:
        data = domain_get('/v1/addressLocators', params={'q': q})
    except requests.HTTPError as e:
        return jsonify({'error':'domain api error','details':str(e)}), 502

    DOMAIN_CACHE[key] = (now, data)
    return jsonify(data)


@app.route('/ai-analytics')
def ai_analytics():
    if 'userID' not in session:
        return redirect(url_for('login'))
    userID = session['userID']
    properties = get_properties(userID)
    return render_template('ai_analytics.html', properties=properties)


@app.route('/api/ai-upload', methods=['POST'])
def api_ai_upload():
    if 'userID' not in session:
        return jsonify({'error':'not authenticated'}), 401
    userID = session['userID']
    f = request.files.get('file')
    if not f or not f.filename:
        return jsonify({'error':'no file uploaded'}), 400
    filename = secure_filename(f.filename)
    user_dir = ensure_user_dir(userID)
    save_path = os.path.join(user_dir, filename)
    f.save(save_path)
    summary = extract_text_from_file(save_path)
    return jsonify({'filename': filename, 'summary': summary})


@app.route('/api/ai-uploads', methods=['GET'])
def api_ai_uploads():
    if 'userID' not in session:
        return jsonify({'error':'not authenticated'}), 401
    userID = session['userID']
    user_dir = os.path.join('uploads', 'ai', str(userID))
    files = []
    if os.path.isdir(user_dir):
        for fn in sorted(os.listdir(user_dir)):
            fp = os.path.join(user_dir, fn)
            if os.path.isfile(fp):
                files.append({'filename': fn})
    return jsonify({'files': files})


@app.route('/api/ai-download/<filename>')
def api_ai_download(filename):
    if 'userID' not in session:
        return redirect(url_for('login'))
    userID = session['userID']
    safe = secure_filename(filename)
    path = os.path.join('uploads', 'ai', str(userID), safe)
    if not os.path.isfile(path):
        return jsonify({'error':'not found'}), 404
    return send_file(path, as_attachment=True)


@app.route('/api/propradar/property/<propertyID>')
def api_propradar_property(propertyID):

    if 'userID' not in session:
        return jsonify({'error': 'not authenticated'}), 401

    userID = session['userID']

    property_data = get_property(
        propertyID,
        userID
    )

    if property_data is None:
        return jsonify({
            'error': 'property not found'
        }), 404

    try:

        propradar_data = search_omniledger_property(
            property_data
        )

        return jsonify({
            'success': True,
            'property': dict(property_data),
            'propradar': propradar_data
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():

    if 'userID' not in session:
        return jsonify({
            'error': 'not authenticated'
        }), 401

    userID = session['userID']

    data = request.get_json() or {}

    message = data.get('message')

    property_id = data.get('propertyID')


    ctx = build_context(
        userID,
        property_id
    )


    if property_id:

        property_data = get_property(
            property_id,
            userID
        )

        if property_data:

            try:

                propradar_data = search_omniledger_property(
                    property_data
                )

                ctx["propradar"] = propradar_data

            except Exception as e:

                ctx["propradar"] = {
                    "available": False,
                    "error": str(e)
                }


    reply = generate_reply(
        message,
        ctx
    )

    return jsonify({
        'reply': reply
    })


@app.route('/api/nominatim/search')
def nominatim_search():
    q = request.args.get('q') or request.args.get('query')
    if not q:
        return jsonify({'error':'missing query'}), 400

    key = "nominatim:" + q.lower()
    now = time.time()
    cached = DOMAIN_CACHE.get(key)
    if cached and (now - cached[0]) < DOMAIN_CACHE_TTL:
        return jsonify(cached[1])

    params = {
        'q': q,
        'format': 'json',
        'addressdetails': 1,
        'limit': 12
    }

    headers = {
        'User-Agent': 'OmniLedger/1.0 (contact: you@example.com)'
    }

    try:
        resp = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as e:
        return jsonify({'error':'nominatim error','details':str(e)}), 502

    DOMAIN_CACHE[key] = (now, data)
    return jsonify(data)


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


    if "userID" not in session:

        return redirect(
            url_for("login")
        )


    userID = session["userID"]


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


#HELP
@app.route("/help")
def help_page():

    if "userID" not in session:
        return redirect(url_for("login"))

    return render_template("help.html")

# REPORTS

@app.route("/reports")
def reports():

    if "userID" not in session:
        return redirect(
            url_for("login")
        )

    userID = session["userID"]

    properties = get_properties(
        userID
    )

    reports = get_reports(
        userID
    )

    return render_template(
        "reports.html",
        properties=properties,
        reports=reports,
        totalIncome=0,
        totalExpenses=0,
        netProfit=0
    )


# STATISTICS
@app.route("/statistics")
def statistics():
    if "userID" not in session:
        return redirect(url_for("login"))

    userID = session["userID"]

    property_filter = request.args.get('property', 'all')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    grouping = request.args.get('grouping', 'monthly')  
    prop_type_filter = request.args.get('propertyType', 'all')
    tx_type_filter = request.args.get('transactionType', 'all')
    category_filter = request.args.get('category', 'all')

    properties = get_properties(userID)
    property_types = sorted(list({p['propertyType'] or 'Unknown' for p in properties}))
    if prop_type_filter != 'all':
        properties = [p for p in properties if (p['propertyType'] or '') == prop_type_filter]

    transactions = get_report_transactions(userID, property_filter or 'all', start_date, end_date)

    categories = sorted(list({(t[3] or 'Uncategorized') for t in transactions}))

    from datetime import datetime as _dt

    def parse_tx_date(s):
        if not s:
            return None
        try:
            if len(s) >= 10 and s[4] == '-':
                return _dt.strptime(s[:10], '%Y-%m-%d').date()
            if len(s) >= 10 and s[2] == '-':
                parts = s.split('-')
                return _dt.strptime(parts[0] + '-' + parts[1] + '-' + parts[2][:4], '%d-%m-%Y').date()
        except Exception:
            return None

    def period_key_for_date(d):
        if d is None:
            return None
        if grouping == 'monthly':
            return d.strftime('%Y-%m')
        if grouping == 'quarterly':
            q = (d.month - 1) // 3 + 1
            return f"{d.year}-Q{q}"
        if grouping == 'yearly':
            return d.strftime('%Y')
        return d.strftime('%Y-%m')

    from datetime import date, timedelta
    today = date.today()

    periods = []
    labels = []
    if start_date and end_date:
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date()
            ed = datetime.strptime(end_date, '%Y-%m-%d').date()
        except Exception:
            sd = today.replace(day=1) - timedelta(days=365)
            ed = today
    else:
        ed = today
        sd = (today.replace(day=1) - timedelta(days=365))



    if grouping == 'monthly':
        cur = sd.replace(day=1)
        while cur <= ed:
            ym = cur.strftime('%Y-%m')
            periods.append(ym)
            labels.append(cur.strftime('%b %y'))


            if cur.month == 12:
                cur = cur.replace(year=cur.year+1, month=1)
            else:
                cur = cur.replace(month=cur.month+1)

    elif grouping == 'quarterly':
        start_q = ((sd.month - 1) // 3) + 1
        cur_year = sd.year
        cur_q = start_q
        while True:
            key = f"{cur_year}-Q{cur_q}"
            periods.append(key)
            labels.append(f"Q{cur_q} {str(cur_year)[2:]}")
    
            if cur_q == 4:
                cur_q = 1
                cur_year += 1
            else:
                cur_q += 1

            quarter_end_month = (cur_q - 1) * 3 + 3
    
            if _dt(cur_year, quarter_end_month, 1).date() > ed:
               
                if period_key_for_date(sd) not in periods and periods == []:
                    pass
                break

    elif grouping == 'yearly':
        y = sd.year

        while y <= ed.year:

            key = str(y)

            periods.append(key)

            labels.append(key)

            y += 1
    
    
    else:
        cur = sd.replace(day=1)

        while cur <= ed:

            ym = cur.strftime('%Y-%m')

            periods.append(ym)

            labels.append(cur.strftime('%b %y'))

            if cur.month == 12:

                cur = cur.replace(year=cur.year+1, month=1)

            else:

                cur = cur.replace(month=cur.month+1)


    income_map = {p:0.0 for p in periods}

    expense_map = {p:0.0 for p in periods}

    inflow_map = {p:0.0 for p in periods}

    outflow_map = {p:0.0 for p in periods}

    tx_count_map = {p:0 for p in periods}

    tx_count_income_map = {p:0 for p in periods}

    tx_count_expense_map = {p:0 for p in periods}

    income_break = {}
    expense_break = {}


    for t in transactions:
        tx_type = t[2]
        category = t[3] or 'Uncategorized'
        amount = float(t[4] or 0)
        tx_date = parse_tx_date(t[5])
        key = period_key_for_date(tx_date)
        if category_filter != 'all' and category != category_filter:
            continue
        if tx_type_filter != 'all' and tx_type != tx_type_filter:
            continue

        if key and key in income_map:
            if tx_type == 'Income':
                income_map[key] += amount
                inflow_map[key] += amount
                income_break[category] = income_break.get(category, 0.0) + amount
            elif tx_type == 'Expense':
                expense_map[key] += amount
                outflow_map[key] += amount
                expense_break[category] = expense_break.get(category, 0.0) + amount
            tx_count_map[key] = tx_count_map.get(key, 0) + 1
            if tx_type == 'Income':
                tx_count_income_map[key] = tx_count_income_map.get(key, 0) + 1
            elif tx_type == 'Expense':
                tx_count_expense_map[key] = tx_count_expense_map.get(key, 0) + 1

   
    income_series = [round(income_map[p],2) for p in periods]

    expense_series = [round(expense_map[p],2) for p in periods]

    profit_series = [round(income_series[i] - expense_series[i],2) for i in range(len(periods))]

    inflow_series = [round(inflow_map[p],2) for p in periods]

    outflow_series = [round(outflow_map[p],2) for p in periods]

    net_cash_series = [round(inflow_series[i] - outflow_series[i],2) for i in range(len(periods))]

    tx_count_series = [tx_count_map[p] for p in periods]

    tx_count_income_series = [tx_count_income_map[p] for p in periods]

    tx_count_expense_series = [tx_count_expense_map[p] for p in periods]

    
    expense_items = sorted(expense_break.items(), key=lambda x: x[1], reverse=True)

    expense_labels = [it[0] for it in expense_items]

    expense_values = [round(it[1],2) for it in expense_items]

   

    income_items = sorted(income_break.items(), key=lambda x: x[1], reverse=True)

    income_labels = [it[0] for it in income_items]

    income_values = [round(it[1],2) for it in income_items]


    
    prop_performance = []

    rental_rois = []

    total_rois = []

    def row_val(row, key, default=0):

        try:

            v = row[key]

            return v if v is not None else default

        except Exception:

            return default

    for p in get_properties(userID):
        pid = p['propertyID']

        pname = p['propertyAddress'] or pid
     
        prop_txs = get_report_transactions(userID, pid, start_date, end_date)

        prop_income = 0.0

        prop_expenses = 0.0

        for tx in prop_txs:

            tx_type = tx[2]

            cat = tx[3] or 'Uncategorized'

            amt = float(tx[4] or 0)

            if category_filter != 'all' and cat != category_filter:

                continue

            if tx_type_filter != 'all' and tx_type != tx_type_filter:

                continue

            if tx_type == 'Income':

                prop_income += amt

            elif tx_type == 'Expense':

                prop_expenses += amt

        net = prop_income - prop_expenses

        weekly = row_val(p, 'weeklyRent', 0)

        purchase = row_val(p, 'purchasePrice', 0)

        prop_value = row_val(p, 'propertyValue', 0)

        rental_roi = calculate_rental_roi(weekly, prop_expenses, purchase)

        total_roi = calculate_total_roi(prop_value, purchase, weekly, prop_expenses)

        prop_performance.append({'propertyID': pid, 'label': pname, 'income': round(prop_income,2), 'expenses': round(prop_expenses,2), 'net': round(net,2)})

        rental_rois.append({'propertyID': pid, 'label': pname, 'rental_roi': rental_roi})

        total_rois.append({'propertyID': pid, 'label': pname, 'total_roi': total_roi})



    # KPIs
    total_income = sum(income_series)

    total_expenses = sum(expense_series)

    net_profit = total_income - total_expenses

    avg_roi = 0

    if rental_rois:
        avg_roi = round(sum([r['rental_roi'] for r in rental_rois]) / len(rental_rois),2)

    return render_template(
        "statistics.html",
        properties=properties,
        property_types=property_types,
        categories=categories,
        periods=periods,
        period_labels=labels,
        income_series=income_series,
        expense_series=expense_series,
        profit_series=profit_series,
        inflow_series=inflow_series,
        outflow_series=outflow_series,
        net_cash_series=net_cash_series,
        tx_count_series=tx_count_series,
        tx_count_income_series=tx_count_income_series,
        tx_count_expense_series=tx_count_expense_series,
        expense_break_labels=expense_labels,
        expense_break_values=expense_values,
        income_break_labels=income_labels,
        income_break_values=income_values,
        prop_performance=prop_performance,
        rental_rois=rental_rois,
        total_rois=total_rois,
        totalIncome=total_income,
        totalExpenses=total_expenses,
        netProfit=net_profit,
        avgROI=avg_roi,
        property_filter=property_filter,
        start_date=start_date,
        end_date=end_date,
        grouping=grouping,
        prop_type_filter=prop_type_filter,
        tx_type_filter=tx_type_filter,
        category_filter=category_filter
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


    # GET FORM VALUES

    reportType = request.form.get(
        "reportType",
        "profit_loss"
    )


    propertyID = request.form.get(
        "property",
        "all"
    )


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


    # VALIDATE PROPERTY

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


    # GENERATE AND SAVE REPORT

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


    # SHOW GENERATED REPORT

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

        propertyInformation=report_data["propertyInformation"],

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


# DOWNLOAD REPORT PDF

@app.route("/report/<int:reportID>/download")
def download_report(reportID):

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

    # Allow optional propertyID query param when downloading a freshly generated report
    propertyID = request.args.get('propertyID', 'all')

    report_data = create_financial_report(
        userID,
        report[2],
        propertyID,
        report[3],
        report[4]
    )

    report_data["reportID"] = report[0]

    pdf = generate_report_pdf(
        report_data
    )

    filename = (
        f"OmniLedger_{report[2]}_"
        f"{report[0]}.pdf"
    )

    return send_file(
        pdf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )




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