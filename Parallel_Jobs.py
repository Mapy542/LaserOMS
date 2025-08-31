from decimal import *

import tinydb


def RevenueCalculations(database: tinydb.TinyDB):
    orders = database.table("Orders")  # load all orders and order items
    order_items = database.table("Order_Items")

    # find all orders. May cause issues bringing every order into ram with a large database
    AllOrders = orders.search(tinydb.where("process_status") == "UTILIZE")

    YearlyRevenue = {}
    MonthlyRevenue = {}

    for order in AllOrders:  # for each order
        year = order["order_date"].split("-")[2]  # find year
        if len(year) > 4:
            # cut off the time or other data included after year
            year = year[: len(year) - 4]
        year = int(year)  # set orders year and month for future use
        month = int(order["order_date"].split("-")[0])

        if year not in YearlyRevenue:  # add year to year dictionary if not in it
            YearlyRevenue[year] = Decimal("0")
            MonthlyRevenue[year] = {}
        # add month to year in monthly revenue if not in it.
        if month not in MonthlyRevenue[year]:
            MonthlyRevenue[year][month] = Decimal("0")

        ItemUIDs = order["order_items_UID"]  # find order items

        for uid in ItemUIDs:  # for each order item
            Item = order_items.search(tinydb.where("item_UID") == uid)[0]  # lookup item
            total = Decimal(Item["item_quantity"])
            total *= Decimal(Item["item_unit_price"])  # calculate total
            total = total.quantize(Decimal("0.01"), ROUND_HALF_EVEN)  # round total
            YearlyRevenue[year] += total  # apply total where applicable.
            MonthlyRevenue[year][month] += total

    # convert to string for json serialization
    for year in YearlyRevenue:
        YearlyRevenue[year] = str(YearlyRevenue[year])
        for month in MonthlyRevenue[year]:
            MonthlyRevenue[year][month] = str(MonthlyRevenue[year][month])

    transient = {
        "transient_name": "Revenue_Calculations",
        "yearly_revenue": YearlyRevenue,
        "monthly_revenue": MonthlyRevenue,
    }
    return transient


def ExpenseCalculations(database: tinydb.TinyDB):
    def VerifyExpenseColumns(database):
        expenses = database.table("Expenses")
        # make sure every expense has required fields for later comparisons
        expenses.update({"expense_image_path": ""}, (~(tinydb.Query().expense_image_path.exists())))
        # add image_path field if it does not exist on the expense

    expenses = database.table("Expenses")  # load all expenses
    # make sure expenses can be compared from settings
    VerifyExpenseColumns(database)
    settings = database.table("Settings")  # find settings
    ShowNonImageExpenses = settings.search(
        (tinydb.Query().setting_name == "Show_Expenses_Without_Image_Verification")
        & (tinydb.Query().process_status == "UTILIZE")
    )[0]["setting_value"]

    if ShowNonImageExpenses == "True":  # if show all expenses
        ActiveExpenses = expenses.search((tinydb.where("process_status") == "UTILIZE"))
    else:  # show expenses only with images
        ActiveExpenses = expenses.search(
            (tinydb.where("process_status") == "UTILIZE")
            & (~(tinydb.where("expense_image_path") == ""))
        )

    YearlyExpenses = {}
    MonthlyExpenses = {}

    for expense in ActiveExpenses:  # for each expense
        year = expense["expense_date"].split("-")[2]  # get year
        if len(year) > 4:
            # cut off the time or other data included after year
            year = year[: len(year) - 4]
        year = int(year)
        month = int(expense["expense_date"].split("-")[0])  # get month

        if year not in YearlyExpenses:  # add year if not in years
            YearlyExpenses[year] = Decimal("0")
            MonthlyExpenses[year] = {}
        # add month to months if not in months
        if month not in MonthlyExpenses[year]:
            MonthlyExpenses[year][month] = Decimal("0")

        total = Decimal(expense["expense_quantity"]) * Decimal(expense["expense_unit_price"])
        total = total.quantize(Decimal("0.01"), ROUND_HALF_EVEN)  # round total
        YearlyExpenses[year] += total  # add total to year
        MonthlyExpenses[year][month] += total  # add total to month

    # convert to string for json serialization
    for year in YearlyExpenses:
        YearlyExpenses[year] = str(YearlyExpenses[year])
        for month in MonthlyExpenses[year]:
            MonthlyExpenses[year][month] = str(MonthlyExpenses[year][month])

    transient = {
        "transient_name": "Expense_Calculations",
        "yearly_expenses": YearlyExpenses,
        "monthly_expenses": MonthlyExpenses,
    }
    return transient
