from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm
from io import BytesIO


def generate_report_pdf(report_data):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading3"],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=5
    )

    normal_style = ParagraphStyle(
        "NormalReport",
        parent=styles["Normal"],
        fontSize=9
    )

    right_style = ParagraphStyle(
        "Right",
        parent=normal_style,
        alignment=TA_RIGHT
    )

    story = []


    report_type = report_data.get(
        "reportType",
        "profit_loss"
    )

    report_titles = {
        "profit_loss": "Profit & Loss Statement",
        "cash_flow": "Cash Flow Statement",
        "rental_statement": "Rental Property Statement",
        "transactions": "Expense & Transaction Report",
        "tax_summary": "Tax & GST Summary",
        "property_performance": "Property Performance Report",
        "portfolio_summary": "Portfolio Summary",
        "balance_sheet": "Balance Sheet"
    }

    report_title = report_titles.get(
        report_type,
        "Financial Report"
    )

    total_income = report_data.get(
        "totalIncome",
        0
    ) or 0

    total_expenses = report_data.get(
        "totalExpenses",
        0
    ) or 0

    total_bills = report_data.get(
        "totalBills",
        0
    ) or 0

    net_profit = report_data.get(
        "netProfit",
        0
    ) or 0

    gst = report_data.get(
        "gst",
        0
    ) or 0

    rental_roi = report_data.get(
        "rentalROI",
        0
    ) or 0

    total_roi = report_data.get(
        "totalROI",
        0
    ) or 0

    income_breakdown = report_data.get(
        "incomeBreakdown",
        {}
    ) or {}

    expense_breakdown = report_data.get(
        "expenseBreakdown",
        {}
    ) or {}

    transactions = report_data.get(
        "transactions",
        []
    ) or []

    cash_flow = report_data.get(
        "cashFlow",
        {}
    ) or {}

    balance_sheet = report_data.get(
        "balanceSheet",
        {}
    ) or {}



    story.append(
        Paragraph(
            "OMNILEDGER",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Financial Management System",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            report_title,
            section_style
        )
    )

    story.append(
        Spacer(1, 5)
    )

    # PROPERTY INFORMATION

    property_id = report_data.get(
        "propertyID",
        "all"
    )

    if property_id == "all":

        property_name = "All Properties"

    else:

        property_information = report_data.get(
            "propertyInformation"
        )

        if property_information:

            property_name = property_information[2]

        else:

            property_name = property_id

    start_date = report_data.get(
        "startDate",
        "-"
    )

    end_date = report_data.get(
        "endDate",
        "-"
    )

    information_data = [
        [
            Paragraph(
                "<b>Property</b>",
                normal_style
            ),
            Paragraph(
                str(property_name),
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Reporting Period</b>",
                normal_style
            ),
            Paragraph(
                f"{start_date} - {end_date}",
                normal_style
            )
        ]
    ]

    information_table = Table(
        information_data,
        colWidths=[
            45 * mm,
            115 * mm
        ]
    )

    information_table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(
        information_table
    )

    story.append(
        Spacer(1, 10)
    )

    # PROFIT

    if report_type == "profit_loss":

        story.append(
            Paragraph(
                "Income",
                section_style
            )
        )

        income_data = [
            [
                "Description",
                "Amount"
            ]
        ]

        if income_breakdown:

            for category, amount in income_breakdown.items():

                income_data.append([
                    str(category),
                    f"${amount:,.2f}"
                ])

        else:

            income_data.append([
                "Recorded Income",
                f"${total_income:,.2f}"
            ])

        income_data.append([
            "Total Income",
            f"${total_income:,.2f}"
        ])

        income_table = Table(
            income_data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        income_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    "Helvetica-Bold"
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            income_table
        )

        story.append(
            Paragraph(
                "Expenses",
                section_style
            )
        )

        expense_data = [
            [
                "Description",
                "Amount"
            ]
        ]

        if expense_breakdown:

            for category, amount in expense_breakdown.items():

                expense_data.append([
                    str(category),
                    f"${amount:,.2f}"
                ])

        else:

            expense_data.append([
                "Recorded Expenses",
                f"${total_expenses:,.2f}"
            ])

        expense_data.append([
            "Total Expenses",
            f"${total_expenses:,.2f}"
        ])

        expense_table = Table(
            expense_data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        expense_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    "Helvetica-Bold"
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            expense_table
        )

        story.append(
            Spacer(1, 10)
        )

        profit_data = [
            [
                Paragraph(
                    "<b>Net Profit / (Loss)</b>",
                    normal_style
                ),
                Paragraph(
                    f"<b>${net_profit:,.2f}</b>",
                    right_style
                )
            ]
        ]

        profit_table = Table(
            profit_data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        profit_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.lightgrey
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(
            profit_table
        )

    # CASH FLOW

    elif report_type == "cash_flow":

        cash_inflow = cash_flow.get(
            "cash_inflow",
            total_income
        ) or 0

        cash_outflow = cash_flow.get(
            "cash_outflow",
            total_expenses
        ) or 0

        net_cash_flow = cash_flow.get(
            "net_cash_flow",
            net_profit
        ) or 0

        story.append(
            Paragraph(
                "Cash Flow Summary",
                section_style
            )
        )

        data = [
            [
                "Description",
                "Amount"
            ],
            [
                "Cash Inflows",
                f"${cash_inflow:,.2f}"
            ],
            [
                "Cash Outflows",
                f"${cash_outflow:,.2f}"
            ],
            [
                "Net Cash Flow",
                f"${net_cash_flow:,.2f}"
            ]
        ]

        table = Table(
            data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            table
        )

    # RENTAL STATEMENT

    elif report_type == "rental_statement":

        story.append(
            Paragraph(
                "Rental Property Performance",
                section_style
            )
        )

        data = [
            [
                "Description",
                "Amount"
            ],
            [
                "Rental Income",
                f"${total_income:,.2f}"
            ],
            [
                "Property Expenses",
                f"${total_expenses:,.2f}"
            ],
            [
                "Total Bills",
                f"${total_bills:,.2f}"
            ],
            [
                "Net Rental Result",
                f"${net_profit:,.2f}"
            ]
        ]

        table = Table(
            data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            table
        )

    # TRANSACTIONS 
    elif report_type == "transactions":

        story.append(
            Paragraph(
                "Transaction Summary",
                section_style
            )
        )

        income_count = 0
        expense_count = 0

        for transaction in transactions:

            if transaction[2] == "Income":

                income_count += 1

            elif transaction[2] == "Expense":

                expense_count += 1

        summary_data = [
            [
                "Description",
                "Value"
            ],
            [
                "Total Income",
                f"${total_income:,.2f}"
            ],
            [
                "Total Expenses",
                f"${total_expenses:,.2f}"
            ],
            [
                "Net Position",
                f"${net_profit:,.2f}"
            ],
            [
                "Transactions Recorded",
                str(len(transactions))
            ],
            [
                "Income Transactions",
                str(income_count)
            ],
            [
                "Expense Transactions",
                str(expense_count)
            ]
        ]

        summary_table = Table(
            summary_data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        summary_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            summary_table
        )

    # TAX 

    elif report_type == "tax_summary":

        gst_summary = report_data.get(
            "gstSummary",
            {}
        ) or {}

        gst_income = gst_summary.get(
            "gst_on_income",
            0
        ) or 0

        gst_expenses = gst_summary.get(
            "gst_on_expenses",
            0
        ) or 0

        net_gst = gst_summary.get(
            "net_gst",
            gst
        ) or 0

        story.append(
            Paragraph(
                "Tax & GST Summary",
                section_style
            )
        )

        data = [
            [
                "Description",
                "Amount"
            ],
            [
                "Total Income",
                f"${total_income:,.2f}"
            ],
            [
                "Total Expenses",
                f"${total_expenses:,.2f}"
            ],
            [
                "GST on Income",
                f"${gst_income:,.2f}"
            ],
            [
                "GST on Expenses",
                f"${gst_expenses:,.2f}"
            ],
            [
                "Net GST Position",
                f"${net_gst:,.2f}"
            ],
            [
                "Net Profit",
                f"${net_profit:,.2f}"
            ]
        ]

        table = Table(
            data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            table
        )

    # PROPERTY PERFORMANCE

    elif report_type == "property_performance":

        property_information = report_data.get(
            "propertyInformation"
        )

        property_value = 0
        purchase_price = 0

        if property_information:

            property_value = (
                property_information[11] or 0
            )

            purchase_price = (
                property_information[12] or 0
            )

        data = [
            [
                "Description",
                "Value"
            ],
            [
                "Rental Income",
                f"${total_income:,.2f}"
            ],
            [
                "Property Expenses",
                f"${total_expenses:,.2f}"
            ],
            [
                "Net Property Income",
                f"${net_profit:,.2f}"
            ],
            [
                "Property Value",
                f"${property_value:,.2f}"
            ],
            [
                "Purchase Price",
                f"${purchase_price:,.2f}"
            ],
            [
                "Rental ROI",
                f"{rental_roi:.2f}%"
            ],
            [
                "Total ROI",
                f"{total_roi:.2f}%"
            ]
        ]

        table = Table(
            data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            table
        )

    # PORTFOLIO SUMMARY

    elif report_type == "portfolio_summary":

        story.append(
            Paragraph(
                "Portfolio Financial Overview",
                section_style
            )
        )

        data = [
            [
                "Description",
                "Amount"
            ],
            [
                "Total Portfolio Income",
                f"${total_income:,.2f}"
            ],
            [
                "Total Portfolio Expenses",
                f"${total_expenses:,.2f}"
            ],
            [
                "Total Bills",
                f"${total_bills:,.2f}"
            ],
            [
                "Portfolio Net Profit",
                f"${net_profit:,.2f}"
            ],
            [
                "Transactions Recorded",
                str(len(transactions))
            ]
        ]

        table = Table(
            data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            table
        )

    # BALANCE SHEET
    elif report_type == "balance_sheet":

        assets = balance_sheet.get(
            "assets",
            0
        ) or 0

        liabilities = balance_sheet.get(
            "liabilities",
            0
        ) or 0

        equity = balance_sheet.get(
            "equity",
            0
        ) or 0

        data = [
            [
                "Description",
                "Amount"
            ],
            [
                "Total Assets",
                f"${assets:,.2f}"
            ],
            [
                "Total Liabilities",
                f"${liabilities:,.2f}"
            ],
            [
                "Total Equity",
                f"${equity:,.2f}"
            ]
        ]

        table = Table(
            data,
            colWidths=[
                110 * mm,
                50 * mm
            ]
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(
            table
        )


    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Generated by OmniLedger",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            "For financial management and review purposes",
            subtitle_style
        )
    )

    document.build(
        story
    )

    buffer.seek(0)

    return buffer