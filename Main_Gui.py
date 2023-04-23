import os
import tkinter
from guizero import App, Text, Combo, PushButton, ListBox, TitleBox
from datetime import datetime
from New_Order_Window import NewOrder
from New_Expense_Window import NewExpense
from Google_Sheets_Sync import RebuildProductsFromSheets
from Settings_Window import Settings, VerifySettings
from Easy_Cart_Ingest import ImportEasyCartOrders
from Etsy_Ingest import RefreshEtsyOrders, ImportAllEtsyOrders
import Auto_Update
import PackingSlip
import Finance_Window
import Details
import New_Task_Window
import Listing_Database_Window
import tinydb
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import traceback

# Main Visuals


def DisplayAllOrders(database):
    # get all open orders and ignore shell holders
    orders = database.table("Orders")
    AllOrders = orders.search(tinydb.Query().process_status == "UTILIZE")
    for item in AllOrders:
        item["order_number"] = int(item["order_number"])
    AllOrders = sorted(AllOrders, key=lambda k: k["order_number"])
    VisualData = []  # list of orders to display
    for i in range(len(AllOrders)):  # for each open order
        VisualData.append(
            str(AllOrders[i]["order_number"]) + ", " + AllOrders[i]["order_name"]
        )
    listbox.clear()  # clear listbox
    for i in VisualData:  # for each order
        listbox.append(i)  # add to listbox
    WelcomeMessage.value = (
        "Welcome to Laser OMS, " + str(len(AllOrders)) + " unfulfilled orders."
    )  # update message screen


def ShowOpenOrders(database):  # show open orders
    orders = database.table("Orders")  # get orders table
    OpenOrders = orders.search(
        (tinydb.Query().order_status == "OPEN")
        & (tinydb.Query().process_status == "UTILIZE")
    )  # get all open orders and ignore shell holders
    for item in OpenOrders:
        item["order_number"] = int(item["order_number"])
    OpenOrders = sorted(OpenOrders, key=lambda k: k["order_number"])
    VisualData = []  # list of orders to display
    for i in range(len(OpenOrders)):  # for each open order
        VisualData.append(
            str(OpenOrders[i]["order_number"]) + ", " + OpenOrders[i]["order_name"]
        )
    listbox.clear()  # clear listbox
    for i in VisualData:  # for each order
        listbox.append(i)  # add to listbox
    WelcomeMessage.value = (
        "Welcome to Laser OMS, " + str(len(OpenOrders)) + " unfulfilled orders."
    )  # update message screen


def LoadTasks(database):
    TaskTable = database.table("Tasks")  # get tasks table
    orders = database.table("Orders")  # get orders table
    settings = database.table("Settings")  # get settings table

    tasks = TaskTable.search(
        tinydb.Query().process_status == "UTILIZE"
    )  # get all tasks
    OpenOrders = orders.search(
        (tinydb.Query().order_status == "OPEN")
        & (tinydb.Query().process_status == "UTILIZE")
    )  # get all open orders and ignore shell holders

    if len(OpenOrders) != 0:  # if there are open orders
        for i in range(len(OpenOrders)):  # for each open order
            dates = OpenOrders[i]["order_date"].split("-")  # split date
            dates = [int(i) for i in dates]  # convert to int
            # create datetime object
            d1 = datetime(year=dates[2], month=dates[0], day=dates[1])
            d2 = datetime.now()  # get current date
            delta = d2 - d1  # get difference
            priority = delta.days * 5 + 50  # calculate priority
            if priority > 100:  # if priority is greater than 100
                priority = 100  # set to 100
            # set priority in task format
            OpenOrders[i]["task_priority"] = priority
            OpenOrders[i]["task_name"] = (
                str(OpenOrders[i]["order_number"]) + ", " + OpenOrders[i]["order_name"]
            )  # set name in task format
            tasks.append(OpenOrders[i])  # add to tasks

    # if there are tasks
    if (
        tasks != []
        and settings.search(tinydb.Query().setting_name == "Show_Task_Priority")[0][
            "setting_value"
        ]
        == "True"
    ):
        MaxPriority = 0  # max priority
        MinimumPriority = 100  # min priority
        for i in range(len(tasks)):  # find max and min priority
            if int(tasks[i]["task_priority"]) > MaxPriority:
                MaxPriority = int(tasks[i]["task_priority"])
            if int(tasks[i]["task_priority"]) < MinimumPriority:
                MinimumPriority = int(tasks[i]["task_priority"])
            tasks[i]["task_priority"] = int(tasks[i]["task_priority"])  # convert to int
        if MaxPriority > 75:  # if there is are priorities above and below 75
            # add high priority placeholder
            tasks.append({"task_name": "High Priority", "task_priority": 101})
        if MaxPriority > 50 and MinimumPriority < 75:
            # add medium priority placeholder
            tasks.append({"task_name": "Medium Priority", "task_priority": 76})
        if MaxPriority > 25 and MinimumPriority < 50:
            # add low priority placeholder
            tasks.append({"task_name": "Low Priority", "task_priority": 25})

        tasks.sort(key=lambda x: x["task_priority"])
    return tasks, len(OpenOrders)


def DisplayTasks(database):
    tasks, OpenOrders = LoadTasks(database)  # load tasks
    if tasks == []:  # if there are no tasks
        WelcomeMessage.value = "Welcome to Laser OMS, 0 unfulfilled orders."
        listbox.clear()
        return
    TaskList = []
    for i in range(len(tasks)):  # for each task
        TaskList.append(tasks[i]["task_name"])  # add name to list

    TaskList.reverse()  # reverse list

    listbox.clear()  # clear listbox
    for i in TaskList:  # for each task
        listbox.append(i)  # add to listbox

    WelcomeMessage.value = (
        "Welcome to Laser OMS, " + str(OpenOrders) + " unfulfilled orders."
    )  # update message screen


def UpdateScreen(database):  # update the screen based on the selected display option
    fulfill_button.enabled = True
    if ViewOptionDropDown.value == "Open Orders":
        ShowOpenOrders(database)
    elif ViewOptionDropDown.value == "Tasks":
        DisplayTasks(database)
    elif ViewOptionDropDown.value == "All Orders":
        DisplayAllOrders(database)
        fulfill_button.enabled = False


# new data entries
def NewOrderWindow():  # open new order window
    NewOrder(app, database)
    UpdateScreen(database)  # reload listbox of tasks or orders


def CreateExpense():  # create expense via expense form
    NewExpense(app, database)


def NewTask():  # create new task via task form
    New_Task_Window.NewTask(app, database)
    UpdateScreen(database)


# modify data entries
def PrintPackingSlips(database, listbox):
    values = listbox.value  # get selected orders
    for i in values:  # for each selected order
        trimmed = i.split(",")[0]  # get order number
        if trimmed.isdigit():
            PackingSlip.PrintPackingSlip(app, database, trimmed)


def MarkFulfilled(database):
    orders = database.table("Orders")  # get orders table
    tasks = database.table("Tasks")  # get tasks table

    # sort between orders and tasks
    SelectedData = listbox.value
    SelectedOrders = []
    SelectedTasks = []
    for order in SelectedData:
        if order[0].isdigit():  # if order number is selected
            SelectedOrders.append(order)
        else:
            SelectedTasks.append(order)

    # deal with orders
    for SingleOrder in SelectedOrders:  # for each selected order
        trimmed = SingleOrder.split(",")[0]  # get order number
        orders.update(
            {"order_status": "FULFILLED"},
            tinydb.Query()["order_number"] == str(trimmed),
        )  # update order status

    # deal with tasks
    for SingleTask in SelectedTasks:  # for each selected task
        # remove task from database
        tasks.remove(tinydb.Query().task_name == SingleTask)

    UpdateScreen(database)  # update screen


def ShowDetails(database):
    # sort between orders and tasks
    SelectedData = listbox.value
    SelectedOrders = []
    SelectedTasks = []
    for order in SelectedData:
        if order[0].isdigit():
            SelectedOrders.append(order.split(",")[0])  # get order number
        else:
            SelectedTasks.append(order)

    for OrderNumber in SelectedOrders:  # for each selected order
        # display order details
        Details.EditOrder(app, database, OrderNumber)
    for TaskName in SelectedTasks:  # for each selected task
        Details.EditTask(app, database, TaskName)  # display task details
        pass


def ShowDetailsWrapper():
    global database
    ShowDetails(database)


# Statistics and details
def FinanceStatistics(database):  # display financial stats window
    Finance_Window.FinancesDisplay(app, database)


def ViewListings(database):  # view
    Listing_Database_Window.ListingDisplay(app, database)


# API syncing
def RebuildProducts():  # rebuild products from sheets
    RebuildProductsFromSheets(app, database)  # rebuild products from sheets


def SyncOrders(database):  # sync orders from sheets
    settings = database.table("Settings")
    EasyCart = settings.search(tinydb.Query().setting_name == "Synchronize_Easy_Cart")[
        0
    ]["setting_value"]
    Etsy = settings.search(tinydb.Query().setting_name == "Synchronize_Etsy")[0][
        "setting_value"
    ]

    orders = 0
    if EasyCart == "True":
        orders += ImportEasyCartOrders(app, database)
    if Etsy == "True":
        orders += RefreshEtsyOrders(app, database)

    UpdateScreen(database)  # update screen
    app.info(
        "Orders Synchronized", str(orders) + " orders have been imported from APIs."
    )


# settings
def SettingsWindow():  # display settings window
    Settings(app, database)


try:
    database = tinydb.TinyDB(
        os.path.join(os.path.realpath(os.path.dirname(__file__)), "../OMS-Data.json"),
        storage=CachingMiddleware(JSONStorage),
    )  # load database (use memory cache)

    app = App(title="Laser OMS", layout="grid", width=680, height=600)  # create app
    app.tk.call(
        "wm",
        "iconphoto",
        app.tk._w,
        tkinter.PhotoImage(
            file=os.path.join(os.path.realpath(os.path.dirname(__file__)), "Icon.png")
        ),
    )  # set icon

    WelcomeMessage = Text(
        app,
        text="Welcome to Laser OMS, - unfulfilled orders.",
        size=15,
        font="Times New Roman",
        grid=[0, 0, 4, 1],
    )  # welcome message
    listbox = ListBox(
        app,
        items=[],
        multiselect=True,
        width=400,
        height=200,
        scrollbar=True,
        grid=[0, 1, 4, 5],
    )  # listbox

    listbox.when_double_clicked = ShowDetailsWrapper  # show details when double clicked

    # view options
    ViewOptionDropDown = Combo(
        app,
        options=["Tasks", "Open Orders", "All Orders"],
        grid=[5, 3, 1, 1],
        selected="Tasks",
    )
    reload = PushButton(
        app,
        text="Reload Grid",
        command=UpdateScreen,
        grid=[5, 2, 1, 1],
        args=[database],
    )

    # new options
    new_options_div = TitleBox(app, text="New", grid=[0, 7, 3, 1], layout="grid")
    new_order_button = PushButton(
        new_options_div, text="New Order", command=NewOrderWindow, grid=[0, 0, 1, 1]
    )
    new_expense = PushButton(
        new_options_div, text="New Expense", command=CreateExpense, grid=[1, 0, 1, 1]
    )
    new_task_button = PushButton(
        new_options_div, text="New Task", command=NewTask, grid=[2, 0, 1, 1]
    )

    # modify options
    modify_options_div = TitleBox(app, text="Modify", grid=[0, 8, 3, 1], layout="grid")
    more_details = PushButton(
        modify_options_div,
        text="More Details",
        command=ShowDetails,
        grid=[0, 0, 1, 1],
        args=[database],
    )
    fulfill_button = PushButton(
        modify_options_div,
        text="Mark as Fulfilled",
        command=MarkFulfilled,
        grid=[2, 0, 1, 1],
        args=[database],
    )
    print_button = PushButton(
        modify_options_div,
        text="Print Slips",
        command=PrintPackingSlips,
        grid=[1, 0, 1, 1],
        args=[database, listbox],
    )
    # ship_button = PushButton(app,text='Ship Order',command=ship_orders,grid=[2,8,1,1])

    # sync options
    sync_options_div = TitleBox(
        app, text="Synchronize", grid=[0, 9, 3, 1], layout="grid"
    )
    Product_Pricing_Sync = PushButton(
        sync_options_div,
        text="Update Pricing",
        command=RebuildProducts,
        grid=[0, 0, 1, 1],
    )
    Order_Sync = PushButton(
        sync_options_div,
        text="Synchronize Orders",
        command=SyncOrders,
        grid=[1, 0, 1, 1],
        args=[database],
    )

    # stats options
    stats_options_div = TitleBox(
        app, text="Statistics", grid=[0, 10, 3, 1], layout="grid"
    )
    ListingDataView_button = PushButton(
        stats_options_div,
        text="View All Products",
        command=ViewListings,
        grid=[0, 0, 1, 1],
        args=[database],
    )

    FinanceStatistics = PushButton(
        stats_options_div,
        text="Financial Statistics",
        command=FinanceStatistics,
        grid=[1, 0, 1, 1],
        args=[database],
    )

    SettingsButton = PushButton(
        app, text="Settings", command=SettingsWindow, grid=[3, 9, 1, 1]
    )

    SettingsCheck = VerifySettings(database)  # verify settings
    if SettingsCheck:  # if settings are invalid
        GoToSettings = app.yesno(
            "Settings Conflict",
            "Settings configuration error detected. Would you like to go to settings now?",
        )
        # ask user if they want to go to settings
        if GoToSettings:
            SettingsWindow()

    UpdateScreen(database)  # update screen
    result = Auto_Update.CheckForUpdate(app, database)  # check for updates
    if result:
        result2 = app.yesno(
            "Update Available", "An update is available. Would you like to update now?"
        )
        if result2:
            Auto_Update.UpdateSoftware(app, database)  # update software

    # update info screen from db every 60 seconds
    app.repeat(60000, UpdateScreen, args=[database])
    app.display()  # display app loop
except Exception as err:  # catch all errors
    # display error
    app.warn("Critical Error", f"Unexpected {err=}, {type(err)=}")
    print(traceback.format_exc())
    database.close()  # close database
finally:
    database.close()  # close database
    # NOT CLOSED PROPERLY RESULTS IN LOSS OF CACHED CHANGES
