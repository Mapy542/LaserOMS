from guizero import Text, TextBox, CheckBox, Combo, PushButton, ListBox, Window
from datetime import datetime
import difflib as dl
from Item_Object import Item
from Order_Object import Order
from Task_Object import Task
import Order_Manipulator, Cache_Handler, PackingSlip#, ShippingHandler

#edit exisitng orders and tasks
#possible expences edit to come


def price_update(): #data update for fields on order items
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish, pricing_style
    global products, baseprice, wordpress_price, etsy_price, editboromarket_price
    global realitems
    global window2

    print(products)
    print(item1.value)

    autofill1 = dl.get_close_matches(item1.value, products) #autofill from most possible correct option
    item1.value = autofill1[0]
    realitems[0].changeProduct(autofill1[0]) #update product data
    realitems[0].changeQuantity(int(item_quant1.value))
    item_price1.value = "$" + str(realitems[0].getPrice(pricing_style)/100) #other fields to display
    autofill2 = dl.get_close_matches(item2.value, products) #rense and repeat for all items #hopefully make this more dynamic
    item2.value = autofill2[0]
    realitems[1].changeProduct(autofill2[0])
    realitems[1].changeQuantity(int(item_quant2.value))
    item_price2.value = "$" + str(realitems[1].getPrice(pricing_style)/100)
    autofill3 = dl.get_close_matches(item3.value, products)
    item3.value = autofill3[0]
    realitems[2].changeProduct(autofill3[0])
    realitems[2].changeQuantity(int(item_quant3.value))
    item_price3.value = "$" + str(realitems[2].getPrice(pricing_style)/100)
    autofill4 = dl.get_close_matches(item4.value, products)
    item4.value = autofill4[0]
    realitems[3].changeProduct(autofill4[0])
    realitems[3].changeQuantity(int(item_quant4.value))
    item_price4.value = "$" + str(realitems[3].getPrice(pricing_style)/100)
    autofill5 = dl.get_close_matches(item5.value, products)
    item5.value = autofill5[0]
    realitems[4].changeProduct(autofill5[0])
    realitems[4].changeQuantity(int(item_quant5.value))
    item_price5.value = "$" + str(realitems[4].getPrice(pricing_style)/100)
    totalval = 0
    for item in realitems: #sum total and update display
        totalval += item.getPrice(pricing_style)
    total.value = "Total: $" + str(totalval/100)


def export(): #export order options into order file on save
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish, pricing_style
    global products, baseprice, wordpress_price, etsy_price, editboromarket_price
    global realitems, preorder
    global window2 # this is definetly the correct way to do it #deathtolocalvariables

    order = Order() #make blank order
    order.setOrderNumber(preorder.getOrderNumber()) #fill data from old order
    order.setOrderDate(preorder.getOrderDate())
    order.setOrderName(purchase_name.value)
    order.setOrderAddress(adress.value, adress2.value, city.value, state.value, zip_code.value) #fill data from new inputs
    #order.setOrderPhone() #N/A but co-pilot liked it so i felt bad
    #order.setOrderEmail(email.value)
    price_update() #make sure all items are parsed and correct. No bad prices
    new_items = []
    for item in realitems:
        if item.isNonEmpty():
            new_items.append(item)
    order.setOrderItems(new_items)
    order.changeOrderPricingStyle(pricing_style)
    order.calculateTotal() #make sure everything is set correctly
    #order.changeOrderStatus("Open") not a good idea i think


    Order_Manipulator.SaveOrder(order) #export order data to file
    
    
    if choose_export.value == 1: #you can do things on export
        PackingSlip.GeneratePackingSlip(order)
        PackingSlip.PrintPackingSlip(order)
        
    if choose_ship.value == 1: #i cant do shipping yet lol
        #ShipppingHandler.ShipOrder(order)
        pass

    window2.destroy() #kill me
    return order #again not yet used but you could i guess

def makePrices(): #pull data from item database so it can be memory cached rather than each item recalculating hitting it
    try:
        with open("../Items.txt", "r") as f:
            products = []
            baseprice = []
            wordpress_price = []
            etsy_price = []
            editboromarket_price = []
            for line in f:
                prices = line.split(',')
                products.append(prices[0])
                baseprice.append(prices[1])
                wordpress_price.append(prices[3])
                etsy_price.append(prices[4])
                editboromarket_price.append(prices[5])
            f.close()
            return products, baseprice, wordpress_price, etsy_price, editboromarket_price
    except OSError:
        print("Failed To Read Item File")
        return 0, 0, 0, 0, 0
        
def update_pricing_options(): #change pricing style on the fly 
    global pricing_style #to be dynamic in coming update
    if pricing_option_button.value == "Base":
        pricing_style = "Base"
    elif pricing_option_button.value == "WordPress":
        pricing_style = "Wordpress"
    elif pricing_option_button.value == "Etsy":
        pricing_style = "Etsy"
    elif pricing_option_button.value == "Edin. Mark.":
        pricing_style = "EditBoroMarket"

def OrderDetails(main_window, ordernum): #GUI to edit orders
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish, pricing_style
    global products, baseprice, wordpress_price, etsy_price, editboromarket_price
    global realitems, preorder
    global window2
    realitems = []
    pricing_style = "Base"
    products, baseprice, wordpress_price, etsy_price, editboromarket_price = makePrices()
    for i in range(0,5):
        realitems.append(Item())
    window2 = Window(main_window, title="Edit Order", layout="grid", width=1100,height=700) #look up how GUIZero and TKinter works ok
    welcome_message = Text(window2,text='Change Order.', size=18, font="Times New Roman", grid=[1,0])

    purchase_name_text = Text(window2,text='Buyer Name', size=15, font="Times New Roman", grid=[0,1])
    purchase_name = TextBox(window2,grid=[1,1], width=30)
    #shipping info
    adress_text = Text(window2,text='Adress', size=15, font="Times New Roman", grid=[0,3])
    adress = TextBox(window2,grid=[1,3], width=60)
    adress_text2 = Text(window2,text='Line 2', size=15, font="Times New Roman", grid=[0,4])
    adress2 = TextBox(window2,grid=[1,4], width=60)
    city_text = Text(window2,text='City', size=15, font="Times New Roman", grid=[0,5])
    city = TextBox(window2,grid=[1,5], width=30)
    state_text = Text(window2,text='State', size=15, font="Times New Roman", grid=[0, 6])
    state = TextBox(window2,grid=[1,6], width=10)
    zip_text = Text(window2,text='Zip Code', size=15, font="Times New Roman", grid=[0,7])
    zip_code = TextBox(window2,grid=[1,7], width=10)
    #items header
    items_message = Text(window2,text='Include Items', size=18, font="Times New Roman", grid=[1,8])
    pricing_option_button = Combo(window2,options=['Base','WordPress','Etsy','Edin. Mark.'], command=update_pricing_options, grid=[2,7])
    #items
    item1 = TextBox(window2, width=30,grid=[0,9],text='Empty')
    item_quant1 = TextBox(window2,grid=[1,9], width=10, command=price_update, text='0')
    item_price1 = Text(window2,text='0', size=15, font="Times New Roman", grid=[2,9])

    item2 = TextBox(window2, width=30,grid=[0,10],text='Empty')
    item_quant2 = TextBox(window2,grid=[1,10], width=10, command=price_update, text='0')
    item_price2 = Text(window2,text='0', size=15, font="Times New Roman", grid=[2,10])

    item3 = TextBox(window2, width=30,grid=[0,11],text='Empty')
    item_quant3 = TextBox(window2,grid=[1,11], width=10, command=price_update, text='0')
    item_price3 = Text(window2,text='0', size=15, font="Times New Roman", grid=[2,11])

    item4 = TextBox(window2, width=30,grid=[0,12],text='Empty')
    item_quant4 = TextBox(window2,grid=[1,12], width=10, command=price_update, text='0')
    item_price4 = Text(window2,text='0', size=15, font="Times New Roman", grid=[2,12])

    item5 = TextBox(window2, width=30,grid=[0,13],text='Empty')
    item_quant5 = TextBox(window2,grid=[1,13], width=10, command=price_update, text='0')
    item_price5 = Text(window2,text='0', size=15, font="Times New Roman", grid=[2,13])

    #Total
    total = Text(window2,text='Total: $0', size=18, font="Times New Roman", grid=[2,19])

    #Export Options
    choose_export = CheckBox(window2,text="Export Order", grid=[1,19])
    choose_ship = CheckBox(window2,text="Ship Order", grid=[1,20])
    finish = PushButton(window2,command=export,text='Save',grid=[0,19])


    #load order for edititng
    order = Order_Manipulator.LoadOrder(ordernum)
    preorder = order
    purchase_name.value = order.getOrderName()
    adress.value = order.getOrderAddress()[0]
    adress2.value = order.getOrderAddress()[1]
    city.value = order.getOrderAddress()[2]
    state.value = order.getOrderAddress()[3]
    zip_code.value = order.getOrderAddress()[4]
    if len(order.order_items) >= 1:
        item1.value = order.order_items[0].getProduct()
        item_quant1.value = str(order.order_items[0].getQuantity())
    if len(order.order_items) >= 2:
        item2.value = order.order_items[1].getProduct()
        item_quant2.value = str(order.order_items[1].getQuantity())
    if len(order.order_items) >= 3:
        item3.value = order.order_items[2].getProduct()
        item_quant3.value = str(order.order_items[2].getQuantity())
    if len(order.order_items) >= 4:
        item4.value = order.order_items[3].getProduct()
        item_quant4.value = str(order.order_items[3].getQuantity())  
    if len(order.order_items) >= 5:
        item5.value = order.order_items[4].getProduct()
        item_quant5.value = str(order.order_items[4].getQuantity())
    price_update()


def exporttask(): #save task after modification by overwrite
    global finish, name, discription, priority, permname
    global window2

    tasky = Task(name = name.value, discription = discription.value, priority = priority.value)
    Order_Manipulator.DeleteTask(permname)
    Order_Manipulator.SaveTask(tasky)

    window2.destroy()

def TaskDetails(main_window, taskname): #GUI window to edit a task
    global finish, name, discription, priority, permname
    global window2

    window2 = Window(main_window, title="Edit Task", layout="grid", width=1100,height=700)
    welcome_message = Text(window2,text='Task Changer', size=18, font="Times New Roman", grid=[1,0])

    name_text = Text(window2,text='Task Name', size=15, font="Times New Roman", grid=[0,1])
    name = TextBox(window2,grid=[1,1], width=30)
    #shipping info
    discription_text = Text(window2,text='Discription', size=15, font="Times New Roman", grid=[0,3])
    discription = TextBox(window2,grid=[1,3], width=60)
    prioirty_text = Text(window2,text='Priority', size=15, font="Times New Roman", grid=[0,7])
    priority = TextBox(window2,grid=[1,7], width=10)
    #items header

    finish = PushButton(window2,command=exporttask,text='Save',grid=[0,19])

    permname = "" #keep what the task was before so we can overwrite it
    tasks = Order_Manipulator.LoadTasks()
    for i in range(len(tasks)):
        if tasks[i].getName() == taskname:
            name.value = tasks[i].getName()
            permname = tasks[i].getName()
            discription.value = tasks[i].getDiscription()
            priority.value = tasks[i].getPriority()
            break


        