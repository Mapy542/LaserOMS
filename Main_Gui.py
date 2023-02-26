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
    for i in visualdata:  # for each order
        listbox.append(i)  # add to listbox
    welcome_message.value = "Welcome to Laser OMS, " + \
        str(len(openorders)) + ' unfulfilled orders.'  # update message screen


def LoadTasks(database):
    tasktable = database.table('Tasks')  # get tasks table
    orders = database.table('Orders')  # get orders table
    settings = database.table('Settings')  # get settings table

    tasks = tasktable.search(
        tinydb.Query().process_status == 'UTILIZE')  # get all tasks
    openorders = orders.search((tinydb.Query().order_status == 'OPEN') & (
        tinydb.Query().process_status == 'UTILIZE'))  # get all open orders and ignore shell holders

    if len(openorders) != 0:  # if there are open orders
        for i in range(len(openorders)):  # for each open order
            dates = openorders[i]['order_date'].split('-')  # split date
            dates = [int(i) for i in dates]  # convert to int
            # create datetime object
            d1 = datetime(year=dates[2], month=dates[0], day=dates[1])
            d2 = datetime.now()  # get current date
            delta = d2 - d1  # get difference
            priority = delta.days * 5 + 50  # calculate priority
            if priority > 100:  # if priority is greater than 100
                priority = 100  # set to 100
            # set priority in task format
            openorders[i]['task_priority'] = priority
            openorders[i]['task_name'] = str(openorders[i]['order_number']) + \
                ', ' + openorders[i]['order_name']  # set name in task format
            tasks.append(openorders[i])  # add to tasks

    # if there are tasks
    if tasks != [] and settings.search(tinydb.Query().setting_name == "Show_Task_Priority")[0]["setting_value"] == "True":
        max_priority = 0  # max priority
        min_priority = 100  # min priority
        for i in range(len(tasks)):  # find max and min priority
            if int(tasks[i]['task_priority']) > max_priority:
                max_priority = int(tasks[i]['task_priority'])
            if int(tasks[i]['task_priority']) < min_priority:
                min_priority = int(tasks[i]['task_priority'])
            tasks[i]['task_priority'] = int(
                tasks[i]['task_priority'])  # convert to int
        if max_priority > 75:  # if there is are priorities above and below 75
            # add high priority placeholder
            tasks.append({'task_name': 'High Priority', 'task_priority': 101})
        if max_priority > 50 and min_priority < 75:
            # add medium priority placeholder
            tasks.append({'task_name': 'Medium Priority', 'task_priority': 76})
        if max_priority > 25 and min_priority < 50:
            # add low priority placeholder
            tasks.append({'task_name': 'Low Priority', 'task_priority': 25})

        tasks.sort(key=lambda x: x['task_priority'])
    return tasks, len(openorders)


def DisplayTasks(database):
    tasks, openorders = LoadTasks(database)  # load tasks
    if (tasks == []):  # if there are no tasks
        welcome_message.value = "Welcome to Laser OMS, 0 unfulfilled orders."
        listbox.clear()
        return
    task_list = []
    for i in range(len(tasks)):  # for each task
        task_list.append(tasks[i]['task_name'])  # add name to list

    task_list.reverse()  # reverse list

    listbox.clear()  # clear listbox
    for i in task_list:  # for each task
        listbox.append(i)  # add to listbox

    welcome_message.value = "Welcome to Laser OMS, " + \
        str(openorders) + ' unfulfilled orders.'  # update message screen


def DisplayAllOrders(database):
    # get all open orders and ignore shell holders
    orders = database.table('Orders')
    allorders = orders.search(tinydb.Query().process_status == 'UTILIZE')
    visualdata = DisplayOrders(allorders)  # get visual data
    listbox.clear()  # clear listbox
    for i in visualdata:  # for each order
        listbox.append(i)  # add to listbox
    welcome_message.value = "Welcome to Laser OMS, " + \
        str(len(allorders)) + ' unfulfilled orders.'  # update message screen


def UpdateScreen(database):  # update the screen based on the selected display option
    if view_option.value == "Open Orders":
        ShowOpenOrders(database)
    elif view_option.value == "Tasks":
        DisplayTasks(database)
    elif view_option.value == "All Orders":
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
    selected_data = listbox.value
    selected_orders = []
    selected_tasks = []
    for order in selected_data:
        if order[0].isdigit():  # if order number is selected
            selected_orders.append(order)
        else:
            selected_tasks.append(order)

        # deal with orders
        for single_order in selected_orders:  # for each selected order
            trimmed = single_order.split(',')[0]  # get order number
            orders.update({'order_status': 'FULFILLED'}, tinydb.Query(
            ).order_number == int(trimmed))  # update order status

        # deal with tasks
        for single_task in selected_tasks:  # for each selected task
            # remove task from database
            tasks.remove(tinydb.Query().task_name == single_task)

        UpdateScreen(database)  # update screen


def CreateExpense():  # create expense via expense form
    NewExpense(app, database)


def StatsWindow():  # display financial stats window
    #Finance_Window.FinancesDisplay(app, orders, expenses)
    pass


def ShowDetails():
    # sort between orders and tasks
    selected_data = listbox.value
    selected_orders = []
    selected_tasks = []
    for order in selected_data:
        if order[0].isdigit():
            selected_orders.append(order.split(',')[0])  # get order number
        else:
            selected_tasks.append(order)

    for ordernum in selected_orders:  # for each selected order
        # Details.OrderDetails(app, ordernum, orders)  # display order details
        pass
    for tasknum in selected_tasks:  # for each selected task
        # Details.TaskDetails(app, tasknum, tasks)  # display task details
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

    welcome_message = Text(app, text="Welcome to Laser OMS, - unfulfilled orders.",
                           size=15, font="Times New Roman", grid=[0, 0, 4, 1])  # welcome message
    listbox = ListBox(app, items=[], multiselect=True, width=400,
                      height=200, scrollbar=True, grid=[0, 1, 4, 5])  # listbox

    # view options
    view_option = Combo(app, options=["Tasks", "Open Orders", "All Orders"], grid=[
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
    #listingdataview_button = PushButton(app,text='Listing Database',command=view_listings,grid=[2,9,1,1])

    settingsbutton = PushButton(
        app, text='Settings', command=SettingsWindow, grid=[3, 9, 1, 1])

    settingscheck = VerifySettings(database)  # verify settings
    if settingscheck:  # if settings are invalid
        gotosettings = app.yesno(
            "Settings Conflict", "Settings configuration error detected. Would you like to go to settings now?")
        # ask user if they want to go to settings
        if gotosettings:
            SettingsWindow()

    UpdateScreen(database)  # update screen

    # update info screen from db every 60 seconds
    app.repeat(60000, UpdateScreen, args=[database])
    app.display()  # display app loop
except Exception as err:  # catch all errors
    # display error
    app.warn("Critcal Error", f"Unexpected {err=}, {type(err)=}")
    print(traceback.format_exc())
    database.close()  # close database
finally:
    database.close()  # close database
    # NOT CLOSED PROPERLY RESULTS IN LOSS OF CACHED CHANGES
