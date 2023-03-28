from guizero import Window, Text, Combo, PushButton, ListBox, TitleBox
import tinydb
import New_Expense_Window
import Google_Sheets_Sync
import Expense_Details_Window


def GetRevenueStats(database):
    orders = database.table('Orders')  # load all orders and order items
    order_items = database.table('Order_Items')

    # find all orders. May cause issues bringing every order into ram with a large database
    AllOrders = orders.search(tinydb.where('process_status') == 'UTILIZE')

    YearlyRevenue = {}
    MonthlyRevenue = {}

    for order in AllOrders:  # for each order
        year = order['order_date'].split('-')[2]  # find year
        if len(year) > 4:
            # cut off the time or other data included after year
            year = year[:len(year) - 4]
        year = int(year)  # set orders year and month for future use
        month = int(order['order_date'].split('-')[0])

        if year not in YearlyRevenue:  # add year to year dictionary if not in it
            YearlyRevenue[year] = 0
            MonthlyRevenue[year] = {}
        # add month to year in monthly revenue if not in it.
        if month not in MonthlyRevenue[year]:
            MonthlyRevenue[year][month] = 0

        ItemUIDs = order['order_items_UID']  # find order items

        for uid in ItemUIDs:  # for each order item
            Item = order_items.search(tinydb.where('item_UID') == uid)[
                0]  # lookup item
            total = float(Item['item_quantity']) * \
                float(Item['item_unit_price'])  # calculate total
            YearlyRevenue[year] += total  # apply total where applicable.
            MonthlyRevenue[year][month] += total

    return YearlyRevenue, MonthlyRevenue


def VerifyExpenseColumns(database):
    expenses = database.table('Expenses')
    # make sure every expense has required fields for later comparisons
    expenses.update({'expense_image_path': ''}, (~(tinydb.Query(
    ).expense_image_path.exists())))
    # add image_path field if it does not exist on the expense


def GetExpenseStats(database):
    expenses = database.table('Expenses')  # load all expenses
    # make sure expenses can be compared from settings
    VerifyExpenseColumns(database)
    settings = database.table('Settings')  # find settings
    ShowNonImageExpenses = settings.search((tinydb.Query(
    ).setting_name == 'Show_Expenses_Without_Image_Verification') & (tinydb.Query().process_status == 'UTILIZE'))[0]['setting_value']

    if ShowNonImageExpenses == 'True':  # if show all expenses
        ActiveExpenses = expenses.search(
            (tinydb.where('process_status') == 'UTILIZE'))
    else:  # show expenses only with images
        ActiveExpenses = expenses.search(
            (tinydb.where('process_status') == 'UTILIZE') & (~ (tinydb.where.expense_image_path == '')))

    YearlyExpenses = {}
    MonthlyExpenses = {}

    for expense in ActiveExpenses:  # for each expense
        year = expense['expense_date'].split('-')[2]  # get year
        if len(year) > 4:
            # cut off the time or other data included after year
            year = year[:len(year) - 4]
        year = int(year)
        month = int(expense['expense_date'].split('-')[0])  # get month

        if year not in YearlyExpenses:  # add year if not in years
            YearlyExpenses[year] = 0
            MonthlyExpenses[year] = {}
        # add month to months if not in months
        if month not in MonthlyExpenses[year]:
            MonthlyExpenses[year][month] = 0

        total = float(expense['expense_quantity']) * \
            float(expense['expense_unit_price'])  # calculate total
        YearlyExpenses[year] += total  # add total to applicable
        MonthlyExpenses[year][month] += total

    return YearlyExpenses, MonthlyExpenses


def UpdateListbox(database, ShowCombo):
    if ShowCombo.value == 'Statistics':
        ShowFinancialStats(database)
    elif ShowCombo.value == 'Expenses':
        ShowExpenses(database)


def ShowFinancialStats(database):
    YearlyRevenue, MonthlyRevenue = GetRevenueStats(
        database)  # returns 2 lists of dictionaries
    YearlyExpenses, MonthlyExpenses = GetExpenseStats(database)

    # sort yearly revenue by year descending. Most recent on top
    YearlyRevenue = dict(sorted(YearlyRevenue.items(), reverse=True))

    listbox.clear()

    # for each year available NOT INCLUDING years that have no revenue but do have expenses.
    for i in range(len(YearlyRevenue)):
        year = list(YearlyRevenue.keys())[i]  # find each year
        listbox.append(str(year) + ":")  # print year
        # print yearly revenue
        listbox.append("  Revenue: " + str(YearlyRevenue[year]))
        if year in YearlyExpenses:  # if year has applicable expenses
            # add expenses to listbox
            listbox.append("  Expenses: " + str(YearlyExpenses[year]))
            listbox.append(
                "  Profit: " + str(YearlyRevenue[year] - YearlyExpenses[year]))  # calculate and display difference in revenue and expenses
        else:  # if there are no expenses
            listbox.append("  Expenses: 0")  # display no expenses
            listbox.append("  Profit: " + str(YearlyRevenue[year]))
        listbox.append("")

        # for each month in the year
        for j in range(len(MonthlyRevenue[year])):
            month = list(MonthlyRevenue[year].keys())[j]  # find month
            listbox.append("    Month: " + str(month))  # print month
            listbox.append("      Revenue: " +
                           str(MonthlyRevenue[year][month]))  # print revenue
            # if has expenses etc
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


def ShowExpenses(database):
    listbox.clear()

    expenses = database.table('Expenses')  # load all expenses

    # make sure expenses can be compared from settings
    VerifyExpenseColumns(database)
    settings = database.table('Settings')  # find settings
    ShowNonImageExpenses = settings.search((tinydb.Query(
    ).setting_name == 'Show_Expenses_Without_Image_Verification') & (tinydb.Query().process_status == 'UTILIZE'))[0]['setting_value']

    if ShowNonImageExpenses == 'True':  # if show all expenses
        listbox.append('Check mark indicates expense has image.')
        ActiveExpenses = expenses.search(
            (tinydb.where('process_status') == 'UTILIZE'))
        ActiveExpenses = sorted(
            ActiveExpenses, key=lambda k: k['expense_date'])
        for expense in ActiveExpenses:
            if expense['expense_image_path'] == '':
                HasImage = ''
            else:
                HasImage = ', ' + u'\u2611'
            listbox.append(expense['expense_name'] + ": " + str(float(
                expense['expense_quantity']) * float(expense['expense_unit_price'])) + HasImage)

    else:  # show expenses only with images
        ActiveExpenses = expenses.search(
            (tinydb.where('process_status') == 'UTILIZE') & (~ (tinydb.where.expense_image_path == '')))
        ActiveExpenses = sorted(
            ActiveExpenses, key=lambda k: k['expense_date'])  # sort by date
        for expense in ActiveExpenses:
            listbox.append(expense['expense_name'] + ": " + str(
                float(expense['expense_quantity']) * float(expense['expense_unit_price'])))


def CreateExpense(window2, database):
    New_Expense_Window.NewExpense(window2, database)


def SyncSheet(app, database):
    Google_Sheets_Sync.RebuildProductsFromSheets(app, database)


def EditExpense():
    global listbox
    global window2
    global DatabasePassThrough
    global ShowCombo
    if listbox.value == None or ShowCombo.value == 'Statistics':  # if no expense selected
        return
    expense = listbox.value[0].split(
        ':')[0]  # get expense name from listbox
    Expense_Details_Window.ExpenseEdit(
        window2, DatabasePassThrough, expense)  # open expense edit window


def ExportExpenses(database, window2):
    pass


def FinancesDisplay(main_window, database):
    global listbox
    global window2
    global DatabasePassThrough
    global ShowCombo
    DatabasePassThrough = database

    window2 = Window(main_window, title="Finances",
                     layout="grid", width=1100, height=700)

    WelcomeMessage = Text(window2, text="Finance Statistics",
                          size=15, font="Times New Roman", grid=[0, 0, 4, 1])
    listbox = ListBox(window2, items=[], multiselect=True,
                      width=800, height=500, scrollbar=True, grid=[0, 1, 4, 5])
    listbox.when_double_clicked = EditExpense

    # options

    ShowCombo = Combo(window2, options=[
                      'Statistics', 'Expenses'], grid=[5, 3, 1, 1])
    RebuildButton = PushButton(
        window2, text='Reload', command=UpdateListbox, grid=[5, 2, 1, 1], args=[database, ShowCombo])

    SyncDiv = TitleBox(window2, text='Sync', grid=[0, 8, 3, 1])
    UpdatePricingButton = PushButton(SyncDiv, text='Update Pricing', command=SyncSheet, grid=[
                                     0, 0, 1, 1], args=[main_window, database])

    ExpensesDiv = TitleBox(window2, text='Expenses', grid=[0, 9, 3, 1])
    NewExpense = PushButton(
        ExpensesDiv, text='Create New Expense', command=CreateExpense, grid=[0, 0, 1, 1], args=[window2, database])
    EditExpenseButton = PushButton(
        ExpensesDiv, text='Edit Expense', command=EditExpense, grid=[1, 0, 1, 1])
    ExportExpensesButton = PushButton(ExpensesDiv, text='Export Expenses', command=ExportExpenses, grid=[
                                      2, 0, 1, 1], args=[database, window2])

    UpdateListbox(database, ShowCombo)
