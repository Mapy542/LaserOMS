import os
import tinydb
import tkinter
from guizero import App, Text, TextBox, CheckBox, Combo, PushButton, ListBox
from datetime import datetime
from New_Order_Window import NewOrder
from New_Expense_Window import NewExpense
from Google_Sheets_Sync import RebuildProductsFromSheets
from Settings_Window import Settings, VerifySettings
import PackingSlip
#import ShippingHandler
#import Finance_Window
#import Details
import New_Task_Window
#import New_Expense_Window
#import Listing_Database_Window
import tinydb
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import traceback


def NewOrderWindow():  # open new order window
    NewOrder(app, database)
    UpdateScreen(database)  # reload listbox of tasks or orders


def ShowOpenOrders():
    listbox.clear()  # clear listbox
    for i in VisualData:  # for each order
        listbox.append(i)  # add to listbox
    WelcomeMessage.value = "Welcome to Laser OMS, " + \
        str(len(OpenOrders)) + ' unfulfilled orders.'  # update message screen


def LoadTasks(database):
    TaskTable = database.table('Tasks')  # get tasks table
    orders = database.table('Orders')  # get orders table
    settings = database.table('Settings')  # get settings table

    tasks = TaskTable.search(
        tinydb.Query().process_status == 'UTILIZE')  # get all tasks
    OpenOrders = orders.search((tinydb.Query().order_status == 'OPEN') & (
        tinydb.Query().process_status == 'UTILIZE'))  # get all open orders and ignore shell holders

    if len(OpenOrders) != 0:  # if there are open orders
        for i in range(len(OpenOrders)):  # for each open order
            dates = OpenOrders[i]['order_date'].split('-')  # split date
            dates = [int(i) for i in dates]  # convert to int
            # create datetime object
            d1 = datetime(year=dates[2], month=dates[0], day=dates[1])
            d2 = datetime.now()  # get current date
            delta = d2 - d1  # get difference
            priority = delta.days * 5 + 50  # calculate priority
            if priority > 100:  # if priority is greater than 100
                priority = 100  # set to 100
            # set priority in task format
            OpenOrders[i]['task_priority'] = priority
            OpenOrders[i]['task_name'] = str(OpenOrders[i]['order_number']) + \
                ', ' + OpenOrders[i]['order_name']  # set name in task format
            tasks.append(OpenOrders[i])  # add to tasks

    # if there are tasks
    if tasks != [] and settings.search(tinydb.Query().setting_name == "Show_Task_Priority")[0]["setting_value"] == "True":
        MaxPriority = 0  # max priority
        MinimumPriority = 100  # min priority
        for i in range(len(tasks)):  # find max and min priority
            if int(tasks[i]['task_priority']) > MaxPriority:
                MaxPriority = int(tasks[i]['task_priority'])
            if int(tasks[i]['task_priority']) < MinimumPriority:
                MinimumPriority = int(tasks[i]['task_priority'])
            tasks[i]['task_priority'] = int(
                tasks[i]['task_priority'])  # convert to int
        if MaxPriority > 75:  # if there is are priorities above and below 75
            # add high priority placeholder
            tasks.append({'task_name': 'High Priority', 'task_priority': 101})
        if MaxPriority > 50 and MinimumPriority < 75:
            # add medium priority placeholder
            tasks.append({'task_name': 'Medium Priority', 'task_priority': 76})
        if MaxPriority > 25 and MinimumPriority < 50:
            # add low priority placeholder
            tasks.append({'task_name': 'Low Priority', 'task_priority': 25})

        tasks.sort(key=lambda x: x['task_priority'])
    return tasks, len(OpenOrders)


def DisplayTasks(database):
    tasks, OpenOrders = LoadTasks(database)  # load tasks
    if (tasks == []):  # if there are no tasks
        WelcomeMessage.value = "Welcome to Laser OMS, 0 unfulfilled orders."
        listbox.clear()
        return
    TaskList = []
    for i in range(len(tasks)):  # for each task
        TaskList.append(tasks[i]['task_name'])  # add name to list

    TaskList.reverse()  # reverse list

    listbox.clear()  # clear listbox
    for i in TaskList:  # for each task
        listbox.append(i)  # add to listbox

    WelcomeMessage.value = "Welcome to Laser OMS, " + \
        str(OpenOrders) + ' unfulfilled orders.'  # update message screen


def DisplayAllOrders(database):
    # get all open orders and ignore shell holders
    orders = database.table('Orders')
    AllOrders = orders.search(tinydb.Query().process_status == 'UTILIZE')
    VisualData = DisplayOrders(AllOrders)  # get visual data
    listbox.clear()  # clear listbox
    for i in VisualData:  # for each order
        listbox.append(i)  # add to listbox
    WelcomeMessage.value = "Welcome to Laser OMS, " + \
        str(len(AllOrders)) + ' unfulfilled orders.'  # update message screen


def UpdateScreen(database):  # update the screen based on the selected display option
    if ViewOptionDropDown.value == "Open Orders":
        ShowOpenOrders(database)
    elif ViewOptionDropDown.value == "Tasks":
        DisplayTasks(database)
    elif ViewOptionDropDown.value == "All Orders":
        DisplayAllOrders(database)


def PrintPackingSlips(database):
    for i in range(len(listbox.value)):  # for each selected order
        temp = listbox.value[i].split(',')  # split orders by comma
        if type(temp[0]) == int:  # make sure order number is selected and not a task
            PackingSlip.GeneratePackingSlip(temp[0], orders)  # generate image
            PackingSlip.PrintPackingSlip(temp[0], orders)  # print image


def MarkFulfilled(database):
    orders = database.table('Orders')  # get orders table
    tasks = database.table('Tasks')  # get tasks table

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
            trimmed = SingleOrder.split(',')[0]  # get order number
            orders.update({'order_status': 'FULFILLED'}, tinydb.Query(
            ).order_number == int(trimmed))  # update order status

        # deal with tasks
        for SingleTask in SelectedTasks:  # for each selected task
            # remove task from database
            tasks.remove(tinydb.Query().task_name == SingleTask)

        UpdateScreen(database)  # update screen


def CreateExpense():  # create expense via expense form
    NewExpense(app, database)


def StatsWindow():  # display financial stats window
    #Finance_Window.FinancesDisplay(app, orders, expenses)
    pass


def ShowDetails():
    # sort between orders and tasks
    SelectedData = listbox.value
    SelectedOrders = []
    SelectedTasks = []
    for order in SelectedData:
        if order[0].isdigit():
            SelectedOrders.append(order.split(',')[0])  # get order number
        else:
            SelectedTasks.append(order)

    for OrderNumber in SelectedOrders:  # for each selected order
        # Details.OrderDetails(app, OrderNumber, orders)  # display order details
        pass
    for TaskName in SelectedTasks:  # for each selected task
        # Details.TaskDetails(app, TaskName, tasks)  # display task details
        pass


def NewTask():  # create new task via task form
    New_Task_Window.NewTask(app, database)
    UpdateScreen(database)


def ViewListings():  # view
    #Listing_Database_Window.ListingDisplay(app, products)
    pass


def RebuildProducts():  # rebuild products from sheets
    RebuildProductsFromSheets(app, database)  # rebuild products from sheets


def SettingsWindow():  # display settings window
    Settings(app, database)


try:
    database = tinydb.TinyDB(
        '../OMS-Data.json', storage=CachingMiddleware(JSONStorage))  # load database (use memory cache)

    app = App(title="Laser OMS", layout="grid",
              width=680, height=600)  # create app
    app.tk.call('wm', 'iconphoto', app.tk._w,
                tkinter.PhotoImage(file='./Icon.png'))  # set icon

    WelcomeMessage = Text(app, text="Welcome to Laser OMS, - unfulfilled orders.",
                          size=15, font="Times New Roman", grid=[0, 0, 4, 1])  # welcome message
    listbox = ListBox(app, items=[], multiselect=True, width=400,
                      height=200, scrollbar=True, grid=[0, 1, 4, 5])  # listbox

    # view options
    ViewOptionDropDown = Combo(app, options=["Tasks", "Open Orders", "All Orders"], grid=[
        5, 3, 1, 1], selected="Tasks")
    reload = PushButton(app, text='Reload Grid',
                        command=UpdateScreen, grid=[5, 2, 1, 1], args=[database])

    # options
    new_order_button = PushButton(
        app, text='New Order', command=NewOrderWindow, grid=[0, 7, 1, 1])
    new_expense = PushButton(app, text='New Expense',
                             command=CreateExpense, grid=[1, 7, 1, 1])
    new_task_button = PushButton(
        app, text='New Task', command=NewTask, grid=[2, 7, 1, 1])
    more_details = PushButton(app, text='More Details',
                              command=ShowDetails, grid=[3, 7, 1, 1])

    fulfill_button = PushButton(
        app, text='Mark as Fulfilled', command=MarkFulfilled, grid=[0, 8, 1, 1], args=[database])
    print_button = PushButton(app, text='Print Slips',
                              command=PrintPackingSlips, grid=[1, 8, 1, 1])
    #ship_button = PushButton(app,text='Ship Order',command=ship_orders,grid=[2,8,1,1])

    pricing_button = PushButton(
        app, text='Update Pricing', command=RebuildProducts, grid=[0, 9, 1, 1])
    #stats_button = PushButton(app,text='Financial Statistics',command=stats_run,grid=[1,9,1,1])
    #ListingDataView_button = PushButton(app,text='Listing Database',command=view_listings,grid=[2,9,1,1])

    SettingsButton = PushButton(
        app, text='Settings', command=SettingsWindow, grid=[3, 9, 1, 1])

    SettingsCheck = VerifySettings(database)  # verify settings
    if SettingsCheck:  # if settings are invalid
        GoToSettings = app.yesno(
            "Settings Conflict", "Settings configuration error detected. Would you like to go to settings now?")
        # ask user if they want to go to settings
        if GoToSettings:
            SettingsWindow()

    UpdateScreen(database)  # update screen

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
