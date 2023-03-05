from guizero import Window, Text, TextBox, CheckBox, Combo, PushButton, ListBox
import tinydb
import New_Expense_Window
import Google_Sheets_Sync


def GetRevenueStats(database):
    orders = database.table('Orders')
    order_items = database.table('Order_Items')

    AllOrders = orders.search(tinydb.where('process_status') == 'UTILIZE')

    YearlyRevenue = {}
    MonthlyRevenue = {}

    for order in AllOrders:
        year = order['order_date'].split('-')[2]
        if len(year) > 4:
            # cut off the time or other data included after year
            year = year[:len(year) - 4]
        month = order['order_date'].split('-')[0]

        if year not in YearlyRevenue:
            YearlyRevenue[year] = 0
            MonthlyRevenue[year] = {}
        if month not in MonthlyRevenue[year]:
            MonthlyRevenue[year][month] = 0

        ItemUIDs = order['order_items_UID']

        for uid in ItemUIDs:
            print(uid)
            Item = order_items.search(tinydb.where('item_UID') == uid)[0]
            total = float(Item['item_quantity']) * \
                float(Item['item_unit_price'])
            YearlyRevenue[year] += total
            MonthlyRevenue[year][month] += total

    return YearlyRevenue, MonthlyRevenue


def GetExpenseStats(database):
    expenses = database.table('Expenses')

    ActiveExpenses = expenses.search(
        tinydb.where('process_status') == 'UTILIZE')

    YearlyExpenses = {}
    MonthlyExpenses = {}

    for expense in ActiveExpenses:
        year = expense['expense_date'].split('-')[2]
        if len(year) > 4:
            # cut off the time or other data included after year
            year = year[:len(year) - 4]
        month = expense['expense_date'].split('-')[0]

        if year not in YearlyExpenses:
            YearlyExpenses[year] = 0
            MonthlyExpenses[year] = {}
        if month not in MonthlyExpenses[year]:
            MonthlyExpenses[year][month] = 0

        total = float(expense['expense_quantity']) * \
            float(expense['expense_unit_price'])
        YearlyExpenses[year] += total
        MonthlyExpenses[year][month] += total

    return YearlyExpenses, MonthlyExpenses


def UpdateListbox(database):
    YearlyRevenue, MonthlyRevenue = GetRevenueStats(database)
    YearlyExpenses, MonthlyExpenses = GetExpenseStats(database)

    YearlyRevenue = dict(sorted(YearlyRevenue.items(), reverse=True))

    listbox.clear()

    for i in range(len(YearlyRevenue)):
        year = list(YearlyRevenue.keys())[i]
        listbox.append(year + ":")
        listbox.append("  Revenue: " + str(YearlyRevenue[year]))
        if year in YearlyExpenses:
            listbox.append("  Expenses: " + str(YearlyExpenses[year]))
            listbox.append(
                "  Profit: " + str(YearlyRevenue[year] - YearlyExpenses[year]))
        else:
            listbox.append("  Expenses: 0")
            listbox.append("  Profit: " + str(YearlyRevenue[year]))
        listbox.append("")

        for j in range(len(MonthlyRevenue[year])):
            month = list(MonthlyRevenue[year].keys())[j]
            listbox.append("    Month: " + month)
            listbox.append("      Revenue: " +
                           str(MonthlyRevenue[year][month]))
            if year in MonthlyExpenses and month in MonthlyExpenses[year]:
                listbox.append("      Expenses: " +
                               str(MonthlyExpenses[year][month]))
                listbox.append(
                    "      Profit: " + str(MonthlyRevenue[year][month] - MonthlyExpenses[year][month]))
            else:
                listbox.append("      Expenses: 0")
                listbox.append("      Profit: " +
                               str(MonthlyRevenue[year][month]))
            listbox.append("")


def CreateExpense(window2, database):
    New_Expense_Window.NewExpense(window2, database)


def SyncSheet(app, database):
    Google_Sheets_Sync.RebuildProductsFromSheets(app, database)


def FinancesDisplay(main_window, database):
    global listbox
    global window2
    window2 = Window(main_window, title="Finances",
                     layout="grid", width=1100, height=700)

    WelcomeMessage = Text(window2, text="Finance Statistics",
                          size=15, font="Times New Roman", grid=[0, 0, 4, 1])
    listbox = ListBox(window2, items=[], multiselect=True,
                      width=800, height=500, scrollbar=True, grid=[0, 1, 4, 5])

    UpdateListbox(database)

    # options
    NewExpense = PushButton(
        window2, text='Create New Expense', command=CreateExpense, grid=[1, 8, 1, 1], args=[window2, database])

    RebuildButton = PushButton(
        window2, text='Reload', command=UpdateListbox, grid=[0, 7, 1, 1], args=[database])
    UpdatePricingButton = PushButton(window2, text='Update Pricing', command=SyncSheet, grid=[
                                     0, 8, 1, 1], args=[main_window, database])
