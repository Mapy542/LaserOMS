import os, tkinter
from guizero import App, Text, TextBox, CheckBox, Combo, PushButton, ListBox
from datetime import datetime, date, timedelta
from New_Order_Window import NewOrder
from New_Expence_Window import Expence
from Task_Object import Task
from Update_Prices_Window import SyncSheetItems
import Order_Manipulator, Cache_Handler, PackingSlip, ShippingHandler, Finance_Window, Details, New_Task_Window, New_Expence_Window
from Order_Object import Order
from Item_Object import Item

def stats_run(): #Open the window to veiw financial statistics
    Finance_Window.FinancesDisplay(app)

def new_order(): #launche new order GUI
    NewOrder(app)
    updatescreen() #apply changes when a new order is there to the main listbox

def loadUnfufilledOrders(): #used in displaying orders
    openorders = Order_Manipulator.BulkLoadOrder(Cache_Handler.GetOpenOrders())
    return openorders

def displayOrders(orders): #parse orders for view
    displayvals = []
    for i in range(len(orders)):
        displayvals.append(orders[i].getOrderNumber() + ', ' + orders[i].getOrderName())
        print(displayvals)
    return displayvals

def showOpenOrders(): #display only open orders
    openorders = loadUnfufilledOrders()
    visualdata = displayOrders(openorders)
    print(openorders)
    listbox.clear()
    for i in visualdata:
        listbox.append(i)
    welcome_message.value = "Welcome to Laser OMS, " + str(len(openorders)) + ' unfufilled orders.'

def loadTasks(): #pull current tasks and combine with open orders
    openorders = Order_Manipulator.BulkLoadOrder(Cache_Handler.GetOpenOrders())
    print(openorders)
    orderpriority = []
    for i in range(len(openorders)): #create order priority based on length of time of open-ness
        dates = openorders[i].getOrderDate().split("-")
        dates = [int(days) for days in dates]
        print(dates)
        d1 = datetime(year=dates[2],month=dates[0],day=dates[1])
        d2 = datetime.now()
        delta = d2 - d1
        priority = delta.days * 5 + 50 #bare minimum of 50 priority plus 5 prioirty per day. #ideal scale is  0 -100
        openorders[i].priority = priority
        orderpriority.append(priority)

    coupled_orders = []
    for i in range(len(openorders)):
        coupled_orders.append([openorders[i], orderpriority[i]])

    #print(coupled_orders)

    coupled_orders.sort(key=lambda x: x[1]) #who is lambda???
    
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

def display_tasks(): #displays all tasks including open orders
    tasks = loadTasks()
    task_list = []
    for i in range(len(tasks)):
        if(tasks[i].isOrder()): #heres where it all went wrong
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
    open_orders = Cache_Handler.GetOpenOrders()
    welcome_message.value = "Welcome to Laser OMS, " + str(len(open_orders)) + ' unfufilled orders.'

def display_all_orders(): #show all orders for posterity i guess  or to edit/view them
    orders = Order_Manipulator.BulkLoadOrder(Cache_Handler.GetAllOrders())
    visualdata = displayOrders(orders)
    listbox.clear()
    for i in visualdata:
        listbox.append(i)


def updatescreen(): #change what to show in listbox
    if view_option.value == "Open Orders":
        showOpenOrders()
    elif view_option.value == "Tasks":
        display_tasks()
    elif view_option.value == "All Orders":
        display_all_orders()

def print_slips(): #take selected order(s) and run generate packing slip and print slip for each
    trimmed_orders=[]
    for i in range(len(listbox.value)):
        temp = listbox.value[i].split(',')
        trimmed_orders.append(Order_Manipulator.LoadOrder(temp[0]))
    for i in range(len(trimmed_orders)):
        PackingSlip.GeneratePackingSlip(trimmed_orders[i])
        PackingSlip.PrintPackingSlip(trimmed_orders[i])

def mark_fufilled(): #take order and change status to fufilled and remove from open order cache
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
        Cache_Handler.RemoveOpenOrder(trimmed)
        order = Order_Manipulator.LoadOrder(trimmed)
        order.changeOrderStatus('Fulfilled')
        Order_Manipulator.SaveOrder(order)
    
    #deal with tasks
    for single_task in selected_tasks:
        Order_Manipulator.DeleteTask(single_task)
    updatescreen()

def create_expence(): #run new expence GUI
    New_Expence_Window.NewExpense(app)

def stats_run(): #open stats GUI #WIP
    Finance_Window.FinancesDisplay(app)

def show_details(): #run show details for given task or order
    selected_data = listbox.value
    selected_orders = []
    selected_tasks = []
    for order in selected_data:
        if order[0].isdigit():
            selected_orders.append(order.split(',')[0])
        else:
            selected_tasks.append(order)

    for ordernum in selected_orders:
        Details.OrderDetails(app, ordernum)

    for tasknum in selected_tasks:
        Details.TaskDetails(app, tasknum)

def new_task():
    New_Task_Window.NewTask(app)
    updatescreen()

#create GUIZero App
app = App(title="Laser OMS", layout="grid", width=680,height=600)
app.tk.call('wm', 'iconphoto', app.tk._w, tkinter.PhotoImage(file='./Icon.png')) #:D icon more like i can't

welcome_message = Text(app, text="Welcome to Laser OMS, - unfufilled orders.", size=15, font="Times New Roman",grid=[0,0,4,1])
listbox = ListBox(app, items=[],multiselect=True,width=400,height=200,scrollbar=True,grid=[0,1,4,5])

#view options
view_option = Combo(app, options=["Tasks","Open Orders", "All Orders"], command=updatescreen, grid=[5,3,1,1], selected="Tasks")
reload = PushButton(app,text='Reload Grid',command=updatescreen,grid=[5,2,1,1])

updatescreen() #show inital stuff

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
