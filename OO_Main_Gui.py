import os, tkinter
from guizero import App, Text, TextBox, CheckBox, Combo, PushButton, ListBox
from datetime import datetime, date, timedelta
from Order_GUI import NewOrder
from Expence_GUI import Expence
from Task import Task
from Listing_Database_Manager import SyncSheetItems
import Order_Manipulator, Statistics_Cache_Manager, Packing_Slip_Manager, Shipping_Manager, Statistics_GUI, Modify_Data, New_Task_Window, Expence_GUI
from Order import Order
from Item import Item

def stats_run():
    Statistics_GUI.FinancesDisplay(app)

def new_order():
    NewOrder(app)
    updatescreen()

def loadUnfufilledOrders():
    openorders = Order_Manipulator.BulkLoadOrder(Statistics_Cache_Manager.GetOpenOrders())
    return openorders

def displayOrders(orders):
    displayvals = []
    for i in range(len(orders)):
        displayvals.append(orders[i].getOrderNumber() + ', ' + orders[i].getOrderName())
        print(displayvals)
    return displayvals

def showOpenOrders():
    openorders = loadUnfufilledOrders()
    visualdata = displayOrders(openorders)
    print(openorders)
    listbox.clear()
    for i in visualdata:
        listbox.append(i)
    welcome_message.value = "Welcome to Laser OMS, " + str(len(openorders)) + ' unfufilled orders.'

def loadTasks():
    openorders = Order_Manipulator.BulkLoadOrder(Statistics_Cache_Manager.GetOpenOrders())
    print(openorders)
    orderpriority = []
    for i in range(len(openorders)):
        dates = openorders[i].getOrderDate().split("-")
        dates = [int(days) for days in dates]
        print(dates)
        d1 = datetime(year=dates[2],month=dates[0],day=dates[1])
        d2 = datetime.now()
        delta = d2 - d1
        priority = delta.days * 5 + 50
        openorders[i].priority = priority
        orderpriority.append(priority)

    coupled_orders = []
    for i in range(len(openorders)):
        coupled_orders.append([openorders[i], orderpriority[i]])

    print(coupled_orders)

    coupled_orders.sort(key=lambda x: x[1])
    
    indivdualtasks = Order_Manipulator.LoadTasks()
    if indivdualtasks == None:
        tasks = []
    else:
        tasks = indivdualtasks
        
    #inject priority labels
    tasks.append(Task("Low Priority", 25))
    tasks.append(Task("Medium Priority", 50))
    tasks.append(Task("High Priority", 75))
    tasks.sort(key=lambda x: x.priority)

    #insert tasks into master list
    overall_tasks = []
    for i in range(len(tasks)):
        overall_tasks.append(tasks[i])

    #insert sort orders into tasks based on priority
    for i in range(len(coupled_orders)):
        j = 0
        if(overall_tasks[len(overall_tasks)-1].priority < coupled_orders[i][1]):
            overall_tasks.append(coupled_orders[i][0])
        else:
            while(overall_tasks[j].priority < coupled_orders[i][1]):
                j += 1
            overall_tasks.insert(j, coupled_orders[i][0])

    return overall_tasks

def display_tasks():
    tasks = loadTasks()
    task_list = []
    for i in range(len(tasks)):
        if(tasks[i].isOrder()):
            task_list.append("" + tasks[i].getOrderNumber() + ", " + tasks[i].getOrderName())
        else:
            task_list.append("" + tasks[i].getName())

    #clean up

    #clean up high medium back to back
    if(task_list[len(task_list)-1] == "High Priority" and task_list[len(task_list)-2] == "Medium Priority"):
        task_list.pop(len(task_list)-1)

    #clean up high medium back to back
    if(task_list[len(task_list)-1] == "Medium Priority" and task_list[len(task_list)-2] == "Low Priority"):
        task_list.pop(len(task_list)-1)

    #clean up high at back
    if(task_list[0] == "High Priority"):
        task_list.pop(0)

    #clean up medium at back
    if(task_list[0] == "Medium Priority"):
        task_list.pop(0)

    #clean up low at back
    if task_list[0] == "Low Priority":
        task_list.pop(0)

    task_list.reverse()

    listbox.clear()
    for i in task_list:
        listbox.append(i)
    open_orders = Statistics_Cache_Manager.GetOpenOrders()
    welcome_message.value = "Welcome to Laser OMS, " + str(len(open_orders)) + ' unfufilled orders.'

def display_all_orders():
    orders = Order_Manipulator.BulkLoadOrder(Statistics_Cache_Manager.GetAllOrders())
    visualdata = displayOrders(orders)
    listbox.clear()
    for i in visualdata:
        listbox.append(i)


def updatescreen():
    if view_option.value == "Open Orders":
        showOpenOrders()
    elif view_option.value == "Tasks":
        display_tasks()
    elif view_option.value == "All Orders":
        display_all_orders()

def print_slips():
    trimmed_orders=[]
    for i in range(len(listbox.value)):
        temp = listbox.value[i].split(',')
        trimmed_orders.append(Order_Manipulator.LoadOrder(temp[0]))
    for i in range(len(trimmed_orders)):
        Packing_Slip_Manager.GeneratePackingSlip(trimmed_orders[i])
        Packing_Slip_Manager.PrintPackingSlip(trimmed_orders[i])

def mark_fufilled():
    #sort between orders and tasks
    selected_data = listbox.value
    selected_orders = []
    selected_tasks = []
    for order in selected_data:
        if order[0].isdigit():
            selected_orders.append(order)
        else:
            selected_tasks.append(order)

    #deal with orders
    for single_order in selected_orders:
        trimmed = single_order.split(',')[0]
        Statistics_Cache_Manager.RemoveOpenOrder(trimmed)
        order = Order_Manipulator.LoadOrder(trimmed)
        order.changeOrderStatus('Fulfilled')
        Order_Manipulator.SaveOrder(order)
    
    #deal with tasks
    for single_task in selected_tasks:
        Order_Manipulator.DeleteTask(single_task)
    updatescreen()

def create_expence():
    Expence_GUI.NewExpense(app)

def stats_run():
    Statistics_GUI.FinancesDisplay(app)

def show_details():
    selected_data = listbox.value
    selected_orders = []
    selected_tasks = []
    for order in selected_data:
        if order[0].isdigit():
            selected_orders.append(order.split(',')[0])
        else:
            selected_tasks.append(order)

    for ordernum in selected_orders:
        Modify_Data.OrderDetails(app, ordernum)

    for tasknum in selected_tasks:
        Modify_Data.TaskDetails(app, tasknum)

def new_task():
    New_Task_Window.NewTask(app)
    updatescreen()


app = App(title="Laser OMS", layout="grid", width=680,height=600)
app.tk.call('wm', 'iconphoto', app.tk._w, tkinter.PhotoImage(file='./Icon.png'))

welcome_message = Text(app, text="Welcome to Laser OMS, - unfufilled orders.", size=15, font="Times New Roman",grid=[0,0,4,1])
listbox = ListBox(app, items=[],multiselect=True,width=400,height=200,scrollbar=True,grid=[0,1,4,5])

#view options
view_option = Combo(app, options=["Tasks","Open Orders", "All Orders"], command=updatescreen, grid=[5,3,1,1], selected="Tasks")
reload = PushButton(app,text='Reload Grid',command=updatescreen,grid=[5,2,1,1])

updatescreen()

#options
new_order_button = PushButton(app,text='New Order',command=new_order,grid=[0,7,1,1])
new_expence = PushButton(app,text='New Expence',command=create_expence,grid=[1,7,1,1])
new_task_button = PushButton(app,text='New Task',command=new_task,grid=[2,7,1,1])
more_details = PushButton(app,text='More Details',command=show_details,grid=[3,7,1,1])

fufill_button = PushButton(app,text='Mark as Fufilled',command=mark_fufilled,grid=[0,8,1,1])
print_button = PushButton(app,text='Print Slips',command=print_slips,grid=[1,8,1,1])
#ship_button = PushButton(app,text='Ship Order',command=ship_orders,grid=[2,8,1,1])

pricing_button = PushButton(app,text='Update Pricing',command=SyncSheetItems,grid=[0,9,1,1])
#stats_button = PushButton(app,text='Financial Statistics',command=stats_run,grid=[1,9,1,1])

app.display()
