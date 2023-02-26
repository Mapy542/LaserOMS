from guizero import Text, TextBox, CheckBox, Combo, PushButton, ListBox, Window
from datetime import datetime
import difflib as dl
import tinydb
import PackingSlip
import random


# Makes a list of random UIDs (double check that they are not already in the database)
def MakeUIDs(order_items, ItemCount):
    allUIDs = []
    order_items = order_items.all()  # Get all items in the order
    for item in order_items:
        allUIDs.append(item['item_UID'])  # Add all UIDs to a list
    returnUIDs = []
    for i in range(ItemCount):
        UID = random.randint(1000000, 9999999)  # Generate a random UID
        while UID in allUIDs:  # If the UID is already in the database, generate a new one
            UID = random.randint(1000000, 9999999)  # Generate a random UID
        returnUIDs.append(UID)
    return returnUIDs  # Return the list of UIDs


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


def PriceUpdate():
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total

    global window2, product_names, styles, products

    # Get the closest match to the item name
    autofill1 = dl.get_close_matches(item1.value, product_names)
    item1.value = autofill1[0]  # Set the item name to the closest match
    item1_data = products.search((tinydb.Query().product_name == item1.value) & (
        tinydb.Query().process_status == "UTILIZE"))  # Get the data for the item
    # Set the price to the price of the item times the quantity
    ItemPrice1.value = "$" + \
        str(int(item1_data[0][PricingOptionButton.value.replace(
            " ", "_")]) * int(ItemQuantity1.value))

    autofill2 = dl.get_close_matches(item2.value, product_names)
    item2.value = autofill2[0]
    item2_data = products.search((tinydb.Query().product_name == item2.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    ItemPrice2.value = "$" + \
        str(int(item2_data[0][PricingOptionButton.value.replace(
            " ", "_")]) * int(ItemQuantity2.value))

    autofill3 = dl.get_close_matches(item3.value, product_names)
    item3.value = autofill3[0]
    item3_data = products.search((tinydb.Query().product_name == item3.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    ItemPrice3.value = "$" + \
        str(int(item3_data[0][PricingOptionButton.value.replace(
            " ", "_")]) * int(ItemQuantity3.value))

    autofill4 = dl.get_close_matches(item4.value, product_names)
    item4.value = autofill4[0]
    item4_data = products.search((tinydb.Query().product_name == item4.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    ItemPrice4.value = "$" + \
        str(int(item4_data[0][PricingOptionButton.value.replace(
            " ", "_")]) * int(ItemQuantity4.value))

    autofill5 = dl.get_close_matches(item5.value, product_names)
    item5.value = autofill5[0]
    item5_data = products.search((tinydb.Query().product_name == item5.value) & (
        tinydb.Query().process_status == "UTILIZE"))
    ItemPrice5.value = "$" + \
        str(int(item5_data[0][PricingOptionButton.value.replace(
            " ", "_")]) * int(ItemQuantity5.value))

    TotalNumber = 0
    for item in [ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4, ItemPrice5]:  # Add up all the prices
        TotalNumber += int(item.value.replace("$", "")
                           )  # Add up all the prices
    # Set the Total to the sum of all the prices
    Total.value = "Total: $" + str(TotalNumber)


def export():
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total, ChooseExportCheckBox, ChooseShippingCheckBox, finish
    global window2, styles, product_names, products, orders, order_items, DateField, ForwardDataBase

    OrderNumber = MakeOrderID(orders)  # Make a unique order ID

    ItemCount = 0
    for item in [item1, item2, item3, item4, item5]:  # Count the number of items
        if item.value != 'Empty' and item.value != '':  # Count the number of items
            ItemCount += 1

    # Make a list of UIDs for the order items
    itemsUIDs = MakeUIDs(order_items, ItemCount)

    orders.insert({'order_number': OrderNumber, 'order_name': PurchaseName.value,
                   'order_address': address.value, 'order_address2': address2.value, 'order_city': city.value,
                   'order_state': state.value, 'order_zip': ZipCode.value, 'order_items_UID': itemsUIDs, 'order_date': DateField.value,
                   'order_status': 'OPEN', 'process_status': 'UTILIZE'})  # Insert the order into the database

    PriceUpdate()
    ItemQuantities = [ItemQuantity1.value, ItemQuantity2.value, ItemQuantity3.value,
                      ItemQuantity4.value, ItemQuantity5.value]  # Make a list of the quantities
    ItemIncrement = 0
    UIDIncrement = 0
    # Insert the order items into the database
    for item in [item1, item2, item3, item4, item5]:
        if item.value != 'Empty' and item.value != '':  # Insert the order items into the database
            # Get the data for the item
            product = products.search(
                tinydb.Query().product_name == item.value)
            order_items.insert({'item_UID': itemsUIDs[UIDIncrement], 'item_name': product[0]['product_name'], 'item_quantity': int(ItemQuantities[ItemIncrement]),
                                'item_unit_price': int(product[0][PricingOptionButton.value.replace(" ", "_")]), 'product_snapshot': product[0]})  # Insert the order item into the database
            UIDIncrement += 1
            ItemIncrement += 1

    if ChooseExportCheckBox.value == 1:  # If the user wants to export the order
        PackingSlip.GeneratePackingSlip(ForwardDataBase, OrderNumber)
        PackingSlip.PrintPackingSlip(ForwardDataBase, OrderNumber)

    if ChooseShippingCheckBox.value == 1:  # If the user wants to ship the order
        # ShippingHandler.ShipOrder(order)
        pass

    window2.destroy()  # Close the window


def SelectedProductFill(event):  # Fill the product name in the widget
    global widget, window3
    ItemsList = event.widget  # Get the listbox
    widget.value = ItemsList.value  # Set the widget to the selected item
    window3.destroy()  # Close the window
    PriceUpdate()  # Update the prices


def DropDownSelection(event):  # Select a product from the dropdown
    global window2, product_names, widget, window3
    widget = event.widget  # Get the widget
    window3 = Window(window2, title="Select Product", layout="grid",
                     width=400, height=400)  # Create a new window
    title = Text(window3, text="Select Product", grid=[0, 0])  # Create a title
    ItemsList = ListBox(window3, items=product_names, grid=[
                        0, 1], scrollbar=True, width=350, height=350)  # Create a listbox
    # When the user double clicks an item, run the SelectedProductFill function
    ItemsList.when_double_clicked = SelectedProductFill


def NewOrder(main_window, database):
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total, ChooseExportCheckBox, ChooseShippingCheckBox, finish
    global window2, styles, product_names, products, orders, order_items, DateField, ForwardDataBase

    products = database.table('Products')  # Get the products table
    ForwardDataBase = database  # Set the forward database to the database
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
    ActiveStyles = product_pricing_styles.search(
        tinydb.Query().process_status == 'UTILIZE')  # Get all the active styles
    for style in ActiveStyles:
        styles.append(style['style_name'])

    window2 = Window(main_window, title="New Order",
                     layout="grid", width=1100, height=700)  # Create a new window
    WelcomeMessage = Text(window2, text='Generate New Order.',
                          size=18, font="Times New Roman", grid=[1, 0])  # Create a welcome message

    PurchaseNameText = Text(
        window2, text='Buyer Name', size=15, font="Times New Roman", grid=[0, 1])  # Buyer name
    PurchaseName = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    AddressText = Text(window2, text='Address', size=15,
                       font="Times New Roman", grid=[0, 3])
    address = TextBox(window2, grid=[1, 3], width=60)
    AddressText2 = Text(window2, text='Line 2', size=15,
                        font="Times New Roman", grid=[0, 4])
    Address2 = TextBox(window2, grid=[1, 4], width=60)
    CityText = Text(window2, text='City', size=15,
                    font="Times New Roman", grid=[0, 5])
    city = TextBox(window2, grid=[1, 5], width=30)
    StateText = Text(window2, text='State', size=15,
                     font="Times New Roman", grid=[0, 6])
    state = TextBox(window2, grid=[1, 6], width=10)
    ZipText = Text(window2, text='Zip Code', size=15,
                   font="Times New Roman", grid=[0, 7])
    ZipCode = TextBox(window2, grid=[1, 7], width=10)
    # items header
    ItemsMessage = Text(window2, text='Include Items',
                        size=18, font="Times New Roman", grid=[1, 8])

    PricingOptionButton = Combo(
        window2, options=styles, command=PriceUpdate, grid=[2, 7])
    # items
    item1 = TextBox(window2, width=30, grid=[0, 9], text='Empty')
    item1.when_double_clicked = DropDownSelection
    ItemQuantity1 = TextBox(
        window2, grid=[1, 9], width=10, command=PriceUpdate, text='0')
    ItemPrice1 = Text(window2, text='0', size=15,
                      font="Times New Roman", grid=[2, 9])

    item2 = TextBox(window2, width=30, grid=[0, 10], text='Empty')
    item2.when_double_clicked = DropDownSelection
    ItemQuantity2 = TextBox(
        window2, grid=[1, 10], width=10, command=PriceUpdate, text='0')
    ItemPrice2 = Text(window2, text='0', size=15,
                      font="Times New Roman", grid=[2, 10])

    item3 = TextBox(window2, width=30, grid=[0, 11], text='Empty')
    item3.when_double_clicked = DropDownSelection
    ItemQuantity3 = TextBox(
        window2, grid=[1, 11], width=10, command=PriceUpdate, text='0')
    ItemPrice3 = Text(window2, text='0', size=15,
                      font="Times New Roman", grid=[2, 11])

    item4 = TextBox(window2, width=30, grid=[0, 12], text='Empty')
    item4.when_double_clicked = DropDownSelection
    ItemQuantity4 = TextBox(
        window2, grid=[1, 12], width=10, command=PriceUpdate, text='0')
    ItemPrice4 = Text(window2, text='0', size=15,
                      font="Times New Roman", grid=[2, 12])

    item5 = TextBox(window2, width=30, grid=[0, 13], text='Empty')
    item5.when_double_clicked = DropDownSelection
    ItemQuantity5 = TextBox(
        window2, grid=[1, 13], width=10, command=PriceUpdate, text='0')
    ItemPrice5 = Text(window2, text='0', size=15,
                      font="Times New Roman", grid=[2, 13])

    # Total
    Total = Text(window2, text='Total: $0', size=18,
                 font="Times New Roman", grid=[2, 19])

    DateText = Text(window2, text='Order Date: ', size=15,
                    font="Times New Roman", grid=[0, 18])
    DateField = TextBox(
        window2, grid=[1, 18], width=15, text=datetime.today().strftime('%m-%d-%Y'))

    # Export Options
    ChooseExportCheckBox = CheckBox(window2, text="Export Order", grid=[1, 19])
    ChooseShippingCheckBox = CheckBox(window2, text="Ship Order", grid=[1, 20])
    finish = PushButton(window2, command=export, text='Save', grid=[0, 19])
