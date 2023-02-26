from guizero import Text, TextBox, CheckBox, Combo, PushButton, ListBox, Window
from datetime import datetime
import difflib as dl
import tinydb
import PackingSlip
import random


# Makes a list of random UIDs (double check that they are not already in the database)
def MakeUIDS(order_items, itemcount):
    allUIDS = []
    order_items = order_items.all()  # Get all items in the order
    for item in order_items:
        allUIDS.append(item['item_UID'])  # Add all UIDs to a list
    returnUIDS = []
    for i in range(itemcount):
        UID = random.randint(1000000, 9999999)  # Generate a random UID
        while UID in allUIDS:  # If the UID is already in the database, generate a new one
            UID = random.randint(1000000, 9999999)  # Generate a random UID
        returnUIDS.append(UID)
    return returnUIDS  # Return the list of UIDS


# Makes a unique order ID (double check that it is not already in the database)
def MakeOrderID(orders):
    allIDs = []
    orders = orders.all()  # Get all orders
    for order in orders:
        allIDs.append(order['order_ID'])  # Add all order IDs to a list
    order_ID = 111
    while order_ID in allIDs:  # If the order ID is already in the database, generate a new one
        order_ID += 1
    return order_ID


def price_update():
    global purchase_name, address, address2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total

    global window2, product_names, styles, products

    # Get the closest match to the item name
    autofill1 = dl.get_close_matches(item1.value, product_names)
    item1.value = autofill1[0]  # Set the item name to the closest match
    item1_data = products.search((tinydb.Query().product_name == item1.value) & (
        tinydb.Query().process_status == "UTILIZE"))  # Get the data for the item
    # Set the price to the price of the item times the quantity
    item_price1.value = "$" + \
        str(int(item1_data[0][pricing_option_button.value.replace(
            " ", "_")]) * int(item_quant1.value))

    autofill2 = dl.get_close_matches(item2.value, product_names)
    item2.value = autofill2[0]
    item2_data = products.search((tinydb.Query().product_name == item2.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    item_price2.value = "$" + \
        str(int(item2_data[0][pricing_option_button.value.replace(
            " ", "_")]) * int(item_quant2.value))

    autofill3 = dl.get_close_matches(item3.value, product_names)
    item3.value = autofill3[0]
    item3_data = products.search((tinydb.Query().product_name == item3.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    item_price3.value = "$" + \
        str(int(item3_data[0][pricing_option_button.value.replace(
            " ", "_")]) * int(item_quant3.value))

    autofill4 = dl.get_close_matches(item4.value, product_names)
    item4.value = autofill4[0]
    item4_data = products.search((tinydb.Query().product_name == item4.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    item_price4.value = "$" + \
        str(int(item4_data[0][pricing_option_button.value.replace(
            " ", "_")]) * int(item_quant4.value))

    autofill5 = dl.get_close_matches(item5.value, product_names)
    item5.value = autofill5[0]
    item5_data = products.search((tinydb.Query().product_name == item5.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    item_price5.value = "$" + \
        str(int(item5_data[0][pricing_option_button.value.replace(
            " ", "_")]) * int(item_quant5.value))

    totalnumber = 0
    for item in [item_price1, item_price2, item_price3, item_price4, item_price5]:  # Add up all the prices
        totalnumber += int(item.value.replace("$", "")
                           )  # Add up all the prices
    # Set the total to the sum of all the prices
    total.value = "Total: $" + str(totalnumber)


def export():
    global purchase_name, address, address2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global window2, styles, product_names, products, orders, order_items, datefield, forwarddatabase

    ordernumber = MakeOrderID(orders)  # Make a unique order ID

    itemcount = 0
    for item in [item1, item2, item3, item4, item5]:  # Count the number of items
        if item.value != 'Empty' and item.value != '':  # Count the number of items
            itemcount += 1

    # Make a list of UIDS for the order items
    itemsUIDS = MakeUIDS(order_items, itemcount)

    orders.insert({'order_number': ordernumber, 'order_name': purchase_name.value,
                   'order_address': address.value, 'order_address2': address2.value, 'order_city': city.value,
                   'order_state': state.value, 'order_zip': zip_code.value, 'order_items_UID': itemsUIDS, 'order_date': datefield.value,
                   'order_status': 'OPEN', 'process_status': 'UTILIZE'})  # Insert the order into the database

    price_update()
    itemquantities = [item_quant1.value, item_quant2.value, item_quant3.value,
                      item_quant4.value, item_quant5.value]  # Make a list of the quantities
    itemincrement = 0
    UIDIncrement = 0
    # Insert the order items into the database
    for item in [item1, item2, item3, item4, item5]:
        if item.value != 'Empty' and item.value != '':  # Insert the order items into the database
            # Get the data for the item
            product = products.search(
                tinydb.Query().product_name == item.value)
            order_items.insert({'item_UID': itemsUIDS[UIDIncrement], 'item_name': product[0]['product_name'], 'item_quantity': int(itemquantities[itemincrement]),
                                'item_unit_price': int(product[0][pricing_option_button.value.replace(" ", "_")]), 'product_snapshot': product[0]})  # Insert the order item into the database
            UIDIncrement += 1
            itemincrement += 1

    if choose_export.value == 1:  # If the user wants to export the order
        PackingSlip.GeneratePackingSlip(forwarddatabase, ordernumber)
        PackingSlip.PrintPackingSlip(forwarddatabase, ordernumber)

    if choose_ship.value == 1:  # If the user wants to ship the order
        # ShipppingHandler.ShipOrder(order)
        pass

    window2.destroy()  # Close the window


def selectproductfill(event):  # Fill the product name in the widget
    global widget, window3
    itemslist = event.widget  # Get the listbox
    widget.value = itemslist.value  # Set the widget to the selected item
    window3.destroy()  # Close the window
    price_update()  # Update the prices


def dropdownselect(event):  # Select a product from the dropdown
    global window2, product_names, widget, window3
    widget = event.widget  # Get the widget
    window3 = Window(window2, title="Select Product", layout="grid",
                     width=400, height=400)  # Create a new window
    title = Text(window3, text="Select Product", grid=[0, 0])  # Create a title
    itemslist = ListBox(window3, items=product_names, grid=[
                        0, 1], scrollbar=True, width=350, height=350)  # Create a listbox
    # When the user double clicks an item, run the selectproductfill function
    itemslist.when_double_clicked = selectproductfill


def NewOrder(main_window, database):
    global purchase_name, address, address2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global window2, styles, product_names, products, orders, order_items, datefield, forwarddatabase

    products = database.table('Products')  # Get the products table
    forwarddatabase = database  # Set the forward database to the database
    # Get the product pricing styles table
    product_pricing_styles = database.table('Product_Pricing_Styles')
    orders = database.table('Orders')  # Get the orders table
    order_items = database.table('Order_Items')  # Get the order items table

    active_products = products.search(
        tinydb.Query().process_status == 'UTILIZE')  # Get all the active products
    product_names = []
    for product in active_products:  # Get all the active product names
        # Add the product name to the list
        product_names.append(product['product_name'])

    styles = []
    activestyles = product_pricing_styles.search(
        tinydb.Query().process_status == 'UTILIZE')  # Get all the active styles
    for style in activestyles:
        styles.append(style['style_name'])

    window2 = Window(main_window, title="New Order",
                     layout="grid", width=1100, height=700)  # Create a new window
    welcome_message = Text(window2, text='Generate New Order.',
                           size=18, font="Times New Roman", grid=[1, 0])  # Create a welcome message

    purchase_name_text = Text(
        window2, text='Buyer Name', size=15, font="Times New Roman", grid=[0, 1])  # Buyer name
    purchase_name = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    address_text = Text(window2, text='Address', size=15,
                        font="Times New Roman", grid=[0, 3])
    address = TextBox(window2, grid=[1, 3], width=60)
    address_text2 = Text(window2, text='Line 2', size=15,
                         font="Times New Roman", grid=[0, 4])
    address2 = TextBox(window2, grid=[1, 4], width=60)
    city_text = Text(window2, text='City', size=15,
                     font="Times New Roman", grid=[0, 5])
    city = TextBox(window2, grid=[1, 5], width=30)
    state_text = Text(window2, text='State', size=15,
                      font="Times New Roman", grid=[0, 6])
    state = TextBox(window2, grid=[1, 6], width=10)
    zip_text = Text(window2, text='Zip Code', size=15,
                    font="Times New Roman", grid=[0, 7])
    zip_code = TextBox(window2, grid=[1, 7], width=10)
    # items header
    items_message = Text(window2, text='Include Items',
                         size=18, font="Times New Roman", grid=[1, 8])

    pricing_option_button = Combo(
        window2, options=styles, command=price_update, grid=[2, 7])
    # items
    item1 = TextBox(window2, width=30, grid=[0, 9], text='Empty')
    item1.when_double_clicked = dropdownselect
    item_quant1 = TextBox(
        window2, grid=[1, 9], width=10, command=price_update, text='0')
    item_price1 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 9])

    item2 = TextBox(window2, width=30, grid=[0, 10], text='Empty')
    item2.when_double_clicked = dropdownselect
    item_quant2 = TextBox(
        window2, grid=[1, 10], width=10, command=price_update, text='0')
    item_price2 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 10])

    item3 = TextBox(window2, width=30, grid=[0, 11], text='Empty')
    item3.when_double_clicked = dropdownselect
    item_quant3 = TextBox(
        window2, grid=[1, 11], width=10, command=price_update, text='0')
    item_price3 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 11])

    item4 = TextBox(window2, width=30, grid=[0, 12], text='Empty')
    item4.when_double_clicked = dropdownselect
    item_quant4 = TextBox(
        window2, grid=[1, 12], width=10, command=price_update, text='0')
    item_price4 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 12])

    item5 = TextBox(window2, width=30, grid=[0, 13], text='Empty')
    item5.when_double_clicked = dropdownselect
    item_quant5 = TextBox(
        window2, grid=[1, 13], width=10, command=price_update, text='0')
    item_price5 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 13])

    # Total
    total = Text(window2, text='Total: $0', size=18,
                 font="Times New Roman", grid=[2, 19])

    datetext = Text(window2, text='Order Date: ', size=15,
                    font="Times New Roman", grid=[0, 18])
    datefield = TextBox(
        window2, grid=[1, 18], width=15, text=datetime.today().strftime('%m-%d-%Y'))

    # Export Options
    choose_export = CheckBox(window2, text="Export Order", grid=[1, 19])
    choose_ship = CheckBox(window2, text="Ship Order", grid=[1, 20])
    finish = PushButton(window2, command=export, text='Save', grid=[0, 19])
