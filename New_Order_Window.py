import difflib as dl
import random
from datetime import datetime

import tinydb
from guizero import CheckBox, Combo, ListBox, PushButton, Text, TextBox, Window

import Common
import PackingSlip


def PriceUpdate():
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total

    global window2, product_names, styles, products

    # Get the closest match to the item name
    try:
        autofill1 = dl.get_close_matches(item1.value, product_names)
        item1.value = autofill1[0]  # Set the item name to the closest match

        item1_data = products.search(
            (tinydb.Query().product_name == item1.value)
            & (tinydb.Query().process_status == "UTILIZE")
        )  # Get the data for the item
        # Set the price to the price of the item times the quantity
        ItemPrice1.value = "$" + str(
            Common.MonetaryMultiply(
                item1_data[0][PricingOptionButton.value.replace(" ", "_")],
                ItemQuantity1.value,
            )
        )
    except:
        ItemPrice1.value = "NA"

    try:
        autofill2 = dl.get_close_matches(item2.value, product_names)
        item2.value = autofill2[0]  # Set the item name to the closest match

        item2_data = products.search(
            (tinydb.Query().product_name == item2.value)
            & (tinydb.Query().process_status == "UTILIZE")
        )  # Get the data for the item
        # Set the price to the price of the item times the quantity
        ItemPrice2.value = "$" + str(
            Common.MonetaryMultiply(
                item2_data[0][PricingOptionButton.value.replace(" ", "_")],
                ItemQuantity2.value,
            )
        )
    except:
        ItemPrice2.value = "NA"

    try:
        autofill3 = dl.get_close_matches(item3.value, product_names)
        item3.value = autofill3[0]  # Set the item name to the closest match

        item3_data = products.search(
            (tinydb.Query().product_name == item3.value)
            & (tinydb.Query().process_status == "UTILIZE")
        )  # Get the data for the item
        # Set the price to the price of the item times the quantity
        ItemPrice3.value = "$" + str(
            Common.MonetaryMultiply(
                item3_data[0][PricingOptionButton.value.replace(" ", "_")],
                ItemQuantity3.value,
            )
        )
    except:
        ItemPrice3.value = "NA"

    try:
        autofill4 = dl.get_close_matches(item4.value, product_names)
        item4.value = autofill4[0]  # Set the item name to the closest match

        item4_data = products.search(
            (tinydb.Query().product_name == item4.value)
            & (tinydb.Query().process_status == "UTILIZE")
        )  # Get the data for the item
        # Set the price to the price of the item times the quantity
        ItemPrice4.value = "$" + str(
            Common.MonetaryMultiply(
                item4_data[0][PricingOptionButton.value.replace(" ", "_")],
                ItemQuantity4.value,
            )
        )
    except:
        ItemPrice4.value = "NA"

    try:
        autofill5 = dl.get_close_matches(item5.value, product_names)
        item5.value = autofill5[0]  # Set the item name to the closest match

        item5_data = products.search(
            (tinydb.Query().product_name == item5.value)
            & (tinydb.Query().process_status == "UTILIZE")
        )  # Get the data for the item
        # Set the price to the price of the item times the quantity
        ItemPrice5.value = "$" + str(
            Common.MonetaryMultiply(
                item5_data[0][PricingOptionButton.value.replace(" ", "_")],
                ItemQuantity5.value,
            )
        )
    except:
        ItemPrice5.value = "NA"

    # Calculate the total
    Total.value = "Total: $" + str(
        Common.MonetarySummation(
            [
                ItemPrice1.value,
                ItemPrice2.value,
                ItemPrice3.value,
                ItemPrice4.value,
                ItemPrice5.value,
            ]
        )
    )


def export():
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total, ChooseExportCheckBox, ChooseShippingCheckBox, finish
    global window2, styles, product_names, products, orders, order_items, DateField, ForwardDataBase

    OrderNumber = Common.MakeOrderID(orders)  # Make a unique order ID

    ItemCount = 0
    for item in [item1, item2, item3, item4, item5]:  # Count the number of items
        if item.value != "Empty" and item.value != "":  # Count the number of items
            ItemCount += 1

    # Make a list of UIDs for the order items
    itemsUIDs = Common.MakeUIDs(order_items, ItemCount)

    # Replace the / with a - to clean up the date
    DateField.value = DateField.value.replace("/", "-")

    orders.insert(
        {
            "order_number": str(OrderNumber),
            "order_name": PurchaseName.value,
            "order_address": address.value,
            "order_address2": address2.value,
            "order_city": city.value,
            "order_state": state.value,
            "order_zip": ZipCode.value,
            "order_items_UID": itemsUIDs,
            "order_date": DateField.value,
            "order_pricing_style": PricingOptionButton.value.replace(" ", "_"),
            "order_status": "OPEN",
            "process_status": "UTILIZE",
        }
    )  # Insert the order into the database

    PriceUpdate()
    ItemQuantities = [
        ItemQuantity1.value,
        ItemQuantity2.value,
        ItemQuantity3.value,
        ItemQuantity4.value,
        ItemQuantity5.value,
    ]  # Make a list of the quantities
    ItemIncrement = 0
    UIDIncrement = 0
    # Insert the order items into the database
    for item in [item1, item2, item3, item4, item5]:
        if (
            item.value != "Empty" and item.value != ""
        ):  # Insert the order items into the database
            # Get the data for the item
            product = products.search(tinydb.Query().product_name == item.value)
            order_items.insert(
                {
                    "item_UID": itemsUIDs[UIDIncrement],
                    "item_name": product[0]["product_name"],
                    "item_quantity": int(ItemQuantities[ItemIncrement]),
                    "item_unit_price": int(
                        product[0][PricingOptionButton.value.replace(" ", "_")]
                    ),
                    "process_status": "UTILIZE",
                    "product_snapshot": product[0],
                }
            )  # Insert the order item into the database
            UIDIncrement += 1
            ItemIncrement += 1

    if ChooseExportCheckBox.value == 1:  # If the user wants to export the order
        PackingSlip.PrintPackingSlip(window2, ForwardDataBase, OrderNumber)

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
    window3 = Window(
        window2, title="Select Product", layout="grid", width=400, height=400
    )  # Create a new window
    title = Text(window3, text="Select Product", grid=[0, 0])  # Create a title
    ItemsList = ListBox(
        window3, items=product_names, grid=[0, 1], scrollbar=True, width=350, height=350
    )  # Create a listbox
    # When the user double clicks an item, run the SelectedProductFill function
    ItemsList.when_double_clicked = SelectedProductFill


def NewOrder(main_window, database):
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total, ChooseExportCheckBox, ChooseShippingCheckBox, finish
    global window2, styles, product_names, products, orders, order_items, DateField, ForwardDataBase

    products = database.table("Products")  # Get the products table
    ForwardDataBase = database  # Set the forward database to the database
    # Get the product pricing styles table
    product_pricing_styles = database.table("Product_Pricing_Styles")
    orders = database.table("Orders")  # Get the orders table
    order_items = database.table("Order_Items")  # Get the order items table

    active_products = products.search(
        tinydb.Query().process_status == "UTILIZE"
    )  # Get all the active products
    product_names = []
    for product in active_products:  # Get all the active product names
        # Add the product name to the list
        product_names.append(product["product_name"])

    styles = []
    ActiveStyles = product_pricing_styles.search(
        tinydb.Query().process_status == "UTILIZE"
    )  # Get all the active styles
    for style in ActiveStyles:
        styles.append(style["style_name"])

    window2 = Window(
        main_window, title="New Order", layout="grid", width=1100, height=700
    )  # Create a new window
    WelcomeMessage = Text(
        window2,
        text="Enter New Order Information",
        size=18,
        font="Times New Roman",
        grid=[1, 0],
    )  # Create a welcome message

    PurchaseNameText = Text(
        window2, text="Buyer Name", size=15, font="Times New Roman", grid=[0, 1]
    )  # Buyer name
    PurchaseName = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    AddressText = Text(
        window2, text="Address", size=15, font="Times New Roman", grid=[0, 3]
    )
    address = TextBox(window2, grid=[1, 3], width=60)
    AddressText2 = Text(
        window2, text="Line 2", size=15, font="Times New Roman", grid=[0, 4]
    )
    address2 = TextBox(window2, grid=[1, 4], width=60)
    CityText = Text(window2, text="City", size=15, font="Times New Roman", grid=[0, 5])
    city = TextBox(window2, grid=[1, 5], width=30)
    StateText = Text(
        window2, text="State", size=15, font="Times New Roman", grid=[0, 6]
    )
    state = TextBox(window2, grid=[1, 6], width=10)
    ZipText = Text(
        window2, text="Zip Code", size=15, font="Times New Roman", grid=[0, 7]
    )
    ZipCode = TextBox(window2, grid=[1, 7], width=10)
    # items header
    ItemsMessage = Text(
        window2, text="Include Items", size=18, font="Times New Roman", grid=[1, 8]
    )

    PricingOptionButton = Combo(
        window2, options=styles, command=PriceUpdate, grid=[2, 7]
    )
    # items
    item1 = TextBox(window2, width=30, grid=[0, 9], text="Empty")
    item1.when_double_clicked = DropDownSelection
    ItemQuantity1 = TextBox(
        window2, grid=[1, 9], width=10, command=PriceUpdate, text="0"
    )
    ItemPrice1 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 9])

    item2 = TextBox(window2, width=30, grid=[0, 10], text="Empty")
    item2.when_double_clicked = DropDownSelection
    ItemQuantity2 = TextBox(
        window2, grid=[1, 10], width=10, command=PriceUpdate, text="0"
    )
    ItemPrice2 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 10])

    item3 = TextBox(window2, width=30, grid=[0, 11], text="Empty")
    item3.when_double_clicked = DropDownSelection
    ItemQuantity3 = TextBox(
        window2, grid=[1, 11], width=10, command=PriceUpdate, text="0"
    )
    ItemPrice3 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 11])

    item4 = TextBox(window2, width=30, grid=[0, 12], text="Empty")
    item4.when_double_clicked = DropDownSelection
    ItemQuantity4 = TextBox(
        window2, grid=[1, 12], width=10, command=PriceUpdate, text="0"
    )
    ItemPrice4 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 12])

    item5 = TextBox(window2, width=30, grid=[0, 13], text="Empty")
    item5.when_double_clicked = DropDownSelection
    ItemQuantity5 = TextBox(
        window2, grid=[1, 13], width=10, command=PriceUpdate, text="0"
    )
    ItemPrice5 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 13])

    # Total
    Total = Text(
        window2, text="Total: $0", size=18, font="Times New Roman", grid=[2, 19]
    )

    DateText = Text(
        window2, text="Order Date: ", size=15, font="Times New Roman", grid=[0, 18]
    )
    DateField = TextBox(
        window2, grid=[1, 18], width=15, text=datetime.today().strftime("%m-%d-%Y")
    )

    # Export Options
    ChooseExportCheckBox = CheckBox(window2, text="Export Order", grid=[1, 19])
    ChooseShippingCheckBox = CheckBox(window2, text="Ship Order", grid=[1, 20])
    finish = PushButton(window2, command=export, text="Save", grid=[0, 19])
