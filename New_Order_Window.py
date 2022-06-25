from guizero import Text, TextBox, CheckBox, Combo, PushButton, ListBox, Window
from datetime import datetime
import difflib as dl
from Item_Object import Item
from Order_Object import Order
import Order_Manipulator, Cache_Handler, PackingSlip#, ShippingHandler


#recalculate price fields based on user inputs
def price_update():
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global products, baseprice, wordpress_price, etsy_price, editboromarket_price
    global realitems, pricing_style
    global window2

    #print(products)
    #print(item1.value)
    autofill1 = dl.get_close_matches(item1.value, products) #find closest mastch to existing products to fix typoes
    item1.value = autofill1[0] #apply match
    realitems[0].changeProduct(autofill1[0]) #set to item object to pull pricing values
    realitems[0].changeQuantity(int(item_quant1.value)) #apply quantity value
    item_price1.value = "$" + str(realitems[0].getPrice(pricing_style)/100) #recalculate price for display
    autofill2 = dl.get_close_matches(item2.value, products) #repeat  #to be dynamic in update
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
    totalnumber = 0
    for item in realitems: #find total
        totalnumber += item.getPrice(pricing_style)
    total.value = "Total: $" + str(totalnumber/100)


def export(): #create final object and save it
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global products, baseprice, wordpress_price, etsy_price, editboromarket_price
    global realitems
    global window2
    
    last_order_number = 0 #find the last order number so we dont repeat
    try:
        with open("../Last_Order.txt", "r+") as f:
            last_order_number = int(f.read().strip())
            f.truncate(0)
            f.seek(0)
            f.write(str(last_order_number + 1)) #save the next number for next time
            f.close()
    except:
        print("Unable to read last order number")

    order = Order()
    order.setOrderNumber(last_order_number+1) #apply all data to order object
    order.setOrderDate(datetime.today().strftime('%m-%d-%Y'))
    order.setOrderName(purchase_name.value)
    order.setOrderAddress(adress.value, adress2.value, city.value, state.value, zip_code.value)
    #order.setOrderPhone()
    #order.setOrderEmail(email.value)
    price_update()
    new_items = []
    for item in realitems: #copy over all non-empty items into order
        if item.isNonEmpty():
            new_items.append(item)
    order.setOrderItems(new_items)
    order.changeOrderPricingStyle(pricing_style)
    order.calculateTotal() #make sure every price is correct and recalculated
    order.changeOrderStatus("Open")

    Order_Manipulator.SaveOrder(order) #save order to disk
    Cache_Handler.AddOpenOrder(order) #add to caches to keep track of stats
    Cache_Handler.AddYearOrder(order)
    Cache_Handler.AddRevenueOrder(order)
    
    if choose_export.value == 1: #if export selected send order to packing slip gen and printer
        PackingSlip.GeneratePackingSlip(order)
        PackingSlip.PrintPackingSlip(order)
        
    if choose_ship.value == 1: #ship in comming updatge
        #ShipppingHandler.ShipOrder(order)
        pass

    window2.destroy() #close
    return order

def makePrices():#pull prices into memory to reduce disk access
    try:
        with open("../Items.txt", "r") as f:
            products = []
            baseprice = []
            wordpress_price = []
            etsy_price = []
            editboromarket_price = []
            data = f.read().split("\n")
            f.close()
            for line in data:
                if(not line == ""):
                    prices = line.split(',')
                    products.append(prices[0]) #to be dynamic
                    baseprice.append(prices[1])
                    wordpress_price.append(prices[3])
                    etsy_price.append(prices[4])
                    editboromarket_price.append(prices[5])
                
            return products, baseprice, wordpress_price, etsy_price, editboromarket_price
    except OSError:
        print("Failed To Read Item File")
        return 0, 0, 0, 0, 0
        
def update_pricing_options(): #select pricing style for options
    global pricing_style
    if pricing_option_button.value == "Base":
        pricing_style = "Base"
    elif pricing_option_button.value == "WordPress":
        pricing_style = "Wordpress"
    elif pricing_option_button.value == "Etsy":
        pricing_style = "Etsy"
    elif pricing_option_button.value == "Edin. Mark.":
        pricing_style = "EditBoroMarket"
    price_update()

def NewOrder(main_window): #Main GUI for new order
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global products, baseprice, wordpress_price, etsy_price, editboromarket_price
    global realitems, pricing_style
    global window2
    pricing_style = "Base"
    realitems = []

    products, baseprice, wordpress_price, etsy_price, editboromarket_price = makePrices()

    for i in range(0,5): #make the five blank items to show
        realitems.append(Item())

    #make GUIZero window
    window2 = Window(main_window, title="New Order", layout="grid", width=1100,height=700)
    welcome_message = Text(window2,text='Generate New Order.', size=18, font="Times New Roman", grid=[1,0])

    #Data Fields
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
