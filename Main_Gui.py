import os
import tinydb
import tkinter
from guizero import App, Text, TextBox, CheckBox, Combo, PushButton, ListBox
from datetime import datetime
from New_Order_Window import NewOrder
from Google_Sheets_Sync import RebuildProductsFromSheets
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


def NewOrderWindow():  # open new order window
    NewOrder(app)
    UpdateScreen()  # reload listbox of tasks or orders


def LoadUnfulfilledOrders():

    open_orders = orders.search((tinydb.Query(
    ).order_status == 'OPEN') & (tinydb.Query().process_status == 'UTILIZE'))  # get all open orders and ignore shell holders
    return open_orders  # return open orders


def DisplayOrders(orders):
    displayvals = []  # list of strings to display
    for i in range(len(orders)):  # for each order
        displayvals.append(orders[i]['order_number'] +
                           ", " + orders[i]['order_name'])  # add order number and name to list

    return displayvals


def ShowOpenOrders():
    openorders = LoadUnfulfilledOrders()  # load open orders
    visualdata = DisplayOrders(openorders)  # get visual data
    listbox.clear()  # clear listbox
    for i in visualdata:  # for each order
        listbox.append(i)  # add to listbox
    welcome_message.value = "Welcome to Laser OMS, " + \
        str(len(openorders)) + ' unfulfilled orders.'  # update message screen


def LoadTasks():
    try:
        openorders = orders.search((tinydb.Query().order_status.any == 'OPEN') & (
            tinydb.Query().process_status.any == 'UTILIZE'))  # get all open orders and ignore shell holders
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
            openorders[i]['task_name'] = openorders[i]['order_number'] + \
                ', ' + openorders[i]['order_name']  # set name in task format
            tasks.append(openorders[i])  # add to tasks
        max_priority = 0  # max priority
        min_priority = 100  # min priority
        for i in range(len(tasks)):  # find max and min priority
            if tasks[i]['task_priority'] > max_priority:
                max_priority = tasks[i]['task_priority']
            if tasks[i]['task_priority'] < min_priority:
                min_priority = tasks[i]['task_priority']
        if max_priority > 75:  # if there is are priorities above and below 75
            # add high priority placeholder
            tasks.append({'task_name': 'High Priority', 'task_priority': 101})
        if max_priority > 50 and min_priority < 75:
            # add medium priority placeholder
            tasks.append({'task_name': 'Medium Priority', 'task_priority': 76})
        if max_priority > 25 and min_priority < 50:
            # add low priority placeholder
            tasks.append({'task_name': 'Low Priority', 'task_priority': 25})
        tasks = tasks.sort(key=lambda x: x['task_priority'])
        return tasks, len(openorders)
    except:
        return None, 0


def DisplayTasks():
    tasks, openorders = LoadTasks()  # load tasks
    if(tasks == None):
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

    welcome_message.value = "Welcome to Laser OMS, " + str(openorders) + ' unfulfilled orders.'  # update message screen


def DisplayAllOrders():
    # get all open orders and ignore shell holders
    allorders = orders.search(tinydb.Query().process_status == 'UTILIZE')
    visualdata = DisplayOrders(allorders)  # get visual data
    listbox.clear()  # clear listbox
    for i in visualdata:  # for each order
        listbox.append(i)  # add to listbox
    welcome_message.value = "Welcome to Laser OMS, " + \
        str(len(allorders)) + ' unfulfilled orders.'  # update message screen


def UpdateScreen():  # update the screen based on the selected display option
    if view_option.value == "Open Orders":
        ShowOpenOrders()
    elif view_option.value == "Tasks":
        DisplayTasks()
    elif view_option.value == "All Orders":
        DisplayAllOrders()


def PrintPackingSlips():
    for i in range(len(listbox.value)):  # for each selected order
        temp = listbox.value[i].split(',')  # split orders by comma
        if type(temp[0]) == int:  # make sure order number is selected and not a task
            PackingSlip.GeneratePackingSlip(temp[0], orders)  # generate image
            PackingSlip.PrintPackingSlip(temp[0], orders)  # print image


def MarkFulfilled():
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

        UpdateScreen()  # update screen


def CreateExpense():  # create expense via expense form
    #New_Expense_Window.NewExpense(app, expenses)
    pass


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
    #New_Task_Window.NewTask(app, tasks)
    UpdateScreen()


def ViewListings():  # view
    #Listing_Database_Window.ListingDisplay(app, products)
    pass


def RebuildProducts():
    RebuildProductsFromSheets(products, pricing_styles)


try:
    database = tinydb.TinyDB(
        '../OMS-Data.json', storage=CachingMiddleware(JSONStorage))
    orders = database.table('Orders')
    tasks = database.table('Tasks')
    expenses = database.table('Expenses')
    products = database.table('Products')
    pricing_styles = database.table('Product_Pricing_Styles')
    order_items = database.table('Order_Items')

    app = App(title="Laser OMS", layout="grid", width=680, height=600)
    app.tk.call('wm', 'iconphoto', app.tk._w,
                tkinter.PhotoImage(file='./Icon.png'))

    welcome_message = Text(app, text="Welcome to Laser OMS, - unfulfilled orders.",
                           size=15, font="Times New Roman", grid=[0, 0, 4, 1])
    listbox = ListBox(app, items=[], multiselect=True, width=400,
                      height=200, scrollbar=True, grid=[0, 1, 4, 5])

    # view options
    view_option = Combo(app, options=["Tasks", "Open Orders", "All Orders"],
                        command=UpdateScreen, grid=[5, 3, 1, 1], selected="Tasks")
    reload = PushButton(app, text='Reload Grid',
                        command=UpdateScreen, grid=[5, 2, 1, 1])

    UpdateScreen()

    # options
    new_order_button = PushButton(
        app, text='New Order', command=NewOrderWindow, grid=[0, 7, 1, 1])
    new_expense = PushButton(app, text='New Expense',
                             command=CreateExpense, grid=[1, 7, 1, 1])
    new_task_button = PushButton(
        app, text='New Task', command=NewTask, grid=[2, 7, 1, 1])
    more_details = PushButton(app, text='More Details',
                              command=ShowDetails, grid=[3, 7, 1, 1])

    fufill_button = PushButton(
        app, text='Mark as Fulfilled', command=MarkFulfilled, grid=[0, 8, 1, 1])
    print_button = PushButton(app, text='Print Slips',
                              command=PrintPackingSlips, grid=[1, 8, 1, 1])
    #ship_button = PushButton(app,text='Ship Order',command=ship_orders,grid=[2,8,1,1])

    pricing_button = PushButton(
        app, text='Update Pricing', command=RebuildProducts, grid=[0, 9, 1, 1])
    #stats_button = PushButton(app,text='Financial Statistics',command=stats_run,grid=[1,9,1,1])
    #listingdataview_button = PushButton(app,text='Listing Database',command=view_listings,grid=[2,9,1,1])

    app.display()
except Exception as e:
    print(e)
    database.close()
finally:
    database.close()
