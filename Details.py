import difflib as dl
from datetime import datetime

import tinydb
from guizero import CheckBox, Combo, ListBox, PushButton, Text, TextBox, Window

import Common
import PackingSlip


def SnapshotFailoverSearch(itemName, products):
    """Attempts to locate item information from order item snapshots, but if it fails, searches the database.

    Args:
        itemName (String): auto-filled item name (Must be exact to match)
        products (TinyDB Table): The products table from the database

    Returns:
        List: The product data
    """

    global ItemSnapShots

    try:
        for snapshot in ItemSnapShots:
            if snapshot["product_name"] == itemName:
                return [snapshot]
        return products.search(
            (tinydb.Query().product_name == item1.value)
            & (tinydb.Query().process_status == "UTILIZE")
        )  # Get the data for the item
    except:  # If the snapshot search fails, search the database, if that fails, return an empty product with the name of the item and the price of "NA"
        return [{"product_name": itemName, PricingOptionButton.value.replace(" ", "_"): "NA"}]


def PriceUpdate():
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total

    global window2, product_names, styles, products

    # Get the closest match to the item name
    try:
        autofill1 = dl.get_close_matches(item1.value, product_names)
        item1.value = autofill1[0]  # Set the item name to the closest match

        item1_data = SnapshotFailoverSearch(item1.value, products)
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

        item2_data = SnapshotFailoverSearch(item2.value, products)
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

        item3_data = SnapshotFailoverSearch(item3.value, products)  # Get the data for the item
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

        item4_data = SnapshotFailoverSearch(item4.value, products)
        # Get the data for the item
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

        item5_data = SnapshotFailoverSearch(item5.value, products)  # Get the data for the item
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


def OrderExport():
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total, ChooseExportCheckBox, ChooseShippingCheckBox, finish, OriginalItemUIDs, OriginalOrderNumber
    global window2, styles, product_names, products, orders, order_items, DateField, ForwardDataBase

    ItemCount = 0
    for item in [item1, item2, item3, item4, item5]:  # Count the number of items
        if item.value != "Empty" and item.value != "":  # Count the number of items
            ItemCount += 1

    # Replace the / with a - to clean up the date
    DateField.value = DateField.value.replace("/", "-")

    order_items.remove(
        tinydb.Query().item_UID.one_of(OriginalItemUIDs)
    )  # Remove the old items from the database

    # Make a list of UIDs for the order items
    itemsUIDs = Common.MakeUIDs(order_items, ItemCount)

    orders.update(
        {
            "order_name": PurchaseName.value,  # Update the order in the database
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
        },
        tinydb.Query().order_number == str(OriginalOrderNumber),
    )

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
        if item.value != "Empty" and item.value != "":  # Insert the order items into the database
            # Get the data for the item
            product = SnapshotFailoverSearch(item.value, products)  # Get the data for the item
            order_items.insert(
                {
                    "item_UID": itemsUIDs[UIDIncrement],
                    "item_name": product[0]["product_name"],
                    "item_quantity": int(ItemQuantities[ItemIncrement]),
                    "item_unit_price": int(product[0][PricingOptionButton.value.replace(" ", "_")]),
                    "process_status": "UTILIZE",
                    "product_snapshot": product[0],
                }
            )  # Insert the order item into the database
            UIDIncrement += 1
            ItemIncrement += 1

    if ChooseExportCheckBox.value == 1:  # If the user wants to export the order
        PackingSlip.PrintPackingSlip(window2, ForwardDataBase, OriginalOrderNumber)

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


def EditDefaultOrder(main_window, database, OrderNumber):
    global PurchaseName, address, address2, city, state, ZipCode, PricingOptionButton, item1, item2, item3, item4, item5
    global ItemQuantity1, ItemQuantity2, ItemQuantity3, ItemQuantity4, ItemQuantity5, ItemPrice1, ItemPrice2, ItemPrice3, ItemPrice4
    global ItemPrice5, Total, ChooseExportCheckBox, ChooseShippingCheckBox, finish, OriginalOrderNumber, OriginalItemUIDs
    global window2, styles, product_names, products, orders, order_items, DateField, ForwardDataBase
    global ItemSnapShots

    products = database.table("Products")  # Get the products table
    ForwardDataBase = database  # Set the forward database to the database
    # Get the product pricing styles table
    product_pricing_styles = database.table("Product_Pricing_Styles")
    orders = database.table("Orders")  # Get the orders table
    EditableOrder = orders.search(
        (tinydb.Query().order_number == OrderNumber) & (tinydb.Query().process_status == "UTILIZE")
    )[
        0
    ]  # Get the order to edit
    # Get the original order number
    OriginalOrderNumber = EditableOrder["order_number"]
    # Get the original item UIDs
    OriginalItemUIDs = EditableOrder["order_items_UID"]
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
        main_window, title="Edit Order", layout="grid", width=1100, height=700
    )  # Create a new window
    WelcomeMessage = Text(
        window2, text="Edit Order", size=18, font="Times New Roman", grid=[1, 0]
    )  # Create a welcome message

    PurchaseNameText = Text(
        window2, text="Buyer Name", size=15, font="Times New Roman", grid=[0, 1]
    )  # Buyer name
    PurchaseName = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    AddressText = Text(window2, text="Address", size=15, font="Times New Roman", grid=[0, 3])
    address = TextBox(window2, grid=[1, 3], width=60)
    AddressText2 = Text(window2, text="Line 2", size=15, font="Times New Roman", grid=[0, 4])
    address2 = TextBox(window2, grid=[1, 4], width=60)
    CityText = Text(window2, text="City", size=15, font="Times New Roman", grid=[0, 5])
    city = TextBox(window2, grid=[1, 5], width=30)
    StateText = Text(window2, text="State", size=15, font="Times New Roman", grid=[0, 6])
    state = TextBox(window2, grid=[1, 6], width=10)
    ZipText = Text(window2, text="Zip Code", size=15, font="Times New Roman", grid=[0, 7])
    ZipCode = TextBox(window2, grid=[1, 7], width=10)
    # items header
    ItemsMessage = Text(window2, text="Include Items", size=18, font="Times New Roman", grid=[1, 8])

    PricingOptionButton = Combo(window2, options=styles, command=PriceUpdate, grid=[2, 7])
    # items
    item1 = TextBox(window2, width=30, grid=[0, 9], text="Empty")
    item1.when_double_clicked = DropDownSelection
    ItemQuantity1 = TextBox(window2, grid=[1, 9], width=10, command=PriceUpdate, text="0")
    ItemPrice1 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 9])

    item2 = TextBox(window2, width=30, grid=[0, 10], text="Empty")
    item2.when_double_clicked = DropDownSelection
    ItemQuantity2 = TextBox(window2, grid=[1, 10], width=10, command=PriceUpdate, text="0")
    ItemPrice2 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 10])

    item3 = TextBox(window2, width=30, grid=[0, 11], text="Empty")
    item3.when_double_clicked = DropDownSelection
    ItemQuantity3 = TextBox(window2, grid=[1, 11], width=10, command=PriceUpdate, text="0")
    ItemPrice3 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 11])

    item4 = TextBox(window2, width=30, grid=[0, 12], text="Empty")
    item4.when_double_clicked = DropDownSelection
    ItemQuantity4 = TextBox(window2, grid=[1, 12], width=10, command=PriceUpdate, text="0")
    ItemPrice4 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 12])

    item5 = TextBox(window2, width=30, grid=[0, 13], text="Empty")
    item5.when_double_clicked = DropDownSelection
    ItemQuantity5 = TextBox(window2, grid=[1, 13], width=10, command=PriceUpdate, text="0")
    ItemPrice5 = Text(window2, text="0", size=15, font="Times New Roman", grid=[2, 13])

    # Total
    Total = Text(window2, text="Total: $0", size=18, font="Times New Roman", grid=[2, 19])

    DateText = Text(window2, text="Order Date: ", size=15, font="Times New Roman", grid=[0, 18])
    DateField = TextBox(window2, grid=[1, 18], width=15, text=datetime.today().strftime("%m-%d-%Y"))

    PurchaseName.value = EditableOrder["order_name"]
    address.value = EditableOrder["order_address"]
    address2.value = EditableOrder["order_address2"]
    city.value = EditableOrder["order_city"]
    state.value = EditableOrder["order_state"]
    ZipCode.value = EditableOrder["order_zip"]
    DateField.value = EditableOrder["order_date"]
    UIDs = EditableOrder["order_items_UID"]

    try:
        PricingOptionButton.value = EditableOrder["order_pricing_style"].replace(
            "_", " "
        )  # Set the pricing option to the one in the database
    except KeyError:
        PricingOptionButton.value = styles[
            0
        ]  # Set the pricing option to the first one if it is not set

    items = []
    for uid in UIDs:
        item = order_items.search(
            (tinydb.Query().item_UID == uid) & (tinydb.Query().process_status == "UTILIZE")
        )[0]
        items.append(item)

    ItemSnapShots = [item["product_snapshot"] for item in items]  # Get the snapshots for the items

    if len(items) > 0:
        item1.value = items[0]["item_name"]
        ItemQuantity1.value = items[0]["item_quantity"]
    if len(items) > 1:
        item2.value = items[1]["item_name"]
        ItemQuantity2.value = items[1]["item_quantity"]
    if len(items) > 2:
        item3.value = items[2]["item_name"]
        ItemQuantity3.value = items[2]["item_quantity"]
    if len(items) > 3:
        item4.value = items[3]["item_name"]
        ItemQuantity4.value = items[3]["item_quantity"]
    if len(items) > 4:
        item5.value = items[4]["item_name"]
        ItemQuantity5.value = items[4]["item_quantity"]
    PriceUpdate()

    # Export Options
    ChooseExportCheckBox = CheckBox(window2, text="Export Order", grid=[1, 19])
    ChooseShippingCheckBox = CheckBox(window2, text="Ship Order", grid=[1, 20])
    finish = PushButton(window2, command=OrderExport, text="Save", grid=[0, 19])


def ViewEasyCartOrder(main_window, database, OrderNumber):
    orders = database.table("Orders")  # Get the orders table
    Order = orders.search(
        (tinydb.Query().order_number == OrderNumber) & (tinydb.Query().process_status == "UTILIZE")
    )[
        0
    ]  # Get the order to edit
    order_items = database.table("Order_Items")  # Get the order items table

    window2 = Window(
        main_window, title="View EasyCart Order", layout="grid", width=900, height=650
    )  # Create a new window
    WelcomeMessage = Text(
        window2,
        text="View EasyCart Order",
        size=18,
        font="Times New Roman",
        grid=[0, 0, 2, 1],
    )  # Create a welcome message

    PurchaseNameText = Text(
        window2, text="Buyer Name", size=15, font="Times New Roman", grid=[0, 1]
    )  # Buyer name
    PurchaseName = Text(window2, grid=[1, 1], size=15, font="Times New Roman", text="Buyer Name")
    # shipping info
    AddressText = Text(window2, text="Address", size=15, font="Times New Roman", grid=[0, 3])
    address = Text(window2, grid=[1, 3], size=15, font="Times New Roman", text="Line 1")
    AddressText2 = Text(window2, text="Line 2", size=15, font="Times New Roman", grid=[0, 4])
    address2 = Text(window2, grid=[1, 4], size=15, font="Times New Roman", text="Line 2")
    CityText = Text(window2, text="City", size=15, font="Times New Roman", grid=[0, 5])
    city = Text(window2, grid=[1, 5], size=15, font="Times New Roman", text="City")
    StateText = Text(window2, text="State", size=15, font="Times New Roman", grid=[0, 6])
    state = Text(window2, grid=[1, 6], size=15, font="Times New Roman", text="State")
    ZipText = Text(window2, text="Zip Code", size=15, font="Times New Roman", grid=[0, 7])
    ZipCode = Text(window2, grid=[1, 7], size=15, font="Times New Roman", text="Zip Code")
    # items header
    ItemsMessage = Text(window2, text="Items", size=18, font="Times New Roman", grid=[1, 8])

    ItemInfoListBox = ListBox(
        window2, items=[], grid=[0, 9, 4, 5], width=400, height=370, scrollbar=True
    )

    # whole right side listbox
    OrderInfoListBox = ListBox(
        window2, items=[], grid=[6, 0, 4, 30], width=400, height=600, scrollbar=True
    )

    PurchaseName.value = Order["order_name"]
    address.value = Order["order_address"]
    address2.value = Order["order_address2"]
    city.value = Order["order_city"]
    state.value = Order["order_state"]
    ZipCode.value = Order["order_zip"]

    EasyCartData = Order["easy_cart_snapshot"]
    Keys = list(EasyCartData.keys())
    for key in Keys:
        if EasyCartData[key] == "":
            continue
        OrderInfoListBox.append("    " + key + " : " + str(EasyCartData[key]))

    UIDs = Order["order_items_UID"]
    for uid in UIDs:
        item = order_items.search(
            (tinydb.Query().item_UID == uid) & (tinydb.Query().process_status == "UTILIZE")
        )[0]
        ItemKeys = list(item.keys())
        for key in ItemKeys:
            if item[key] == "":
                continue
            if key == "product_snapshot":  # if the key is the product snapshot, add the SubKeys
                SubKeys = list(item[key].keys())
                for SubKey in SubKeys:
                    if item[key][SubKey] == "":
                        continue
                    ItemInfoListBox.append("        " + SubKey + " : " + str(item[key][SubKey]))
                continue

            ItemInfoListBox.append("    " + key + " : " + str(item[key]))
        # add a blank line between items
        ItemInfoListBox.append("")


def ViewEtsyOrder(main_window, database, OrderNumber):
    orders = database.table("Orders")  # Get the orders table
    Order = orders.search(
        (tinydb.Query().order_number == OrderNumber) & (tinydb.Query().process_status == "UTILIZE")
    )[
        0
    ]  # Get the order to edit
    order_items = database.table("Order_Items")  # Get the order items table

    window2 = Window(
        main_window, title="View Etsy Order", layout="grid", width=900, height=650
    )  # Create a new window
    WelcomeMessage = Text(
        window2,
        text="View Etsy Order",
        size=18,
        font="Times New Roman",
        grid=[0, 0, 2, 1],
    )  # Create a welcome message

    PurchaseNameText = Text(
        window2, text="Buyer Name", size=15, font="Times New Roman", grid=[0, 1]
    )  # Buyer name
    PurchaseName = Text(window2, grid=[1, 1], size=15, font="Times New Roman", text="Buyer Name")
    # shipping info
    AddressText = Text(window2, text="Address", size=15, font="Times New Roman", grid=[0, 3])
    address = Text(window2, grid=[1, 3], size=15, font="Times New Roman", text="Line 1")
    AddressText2 = Text(window2, text="Line 2", size=15, font="Times New Roman", grid=[0, 4])
    address2 = Text(window2, grid=[1, 4], size=15, font="Times New Roman", text="Line 2")
    CityText = Text(window2, text="City", size=15, font="Times New Roman", grid=[0, 5])
    city = Text(window2, grid=[1, 5], size=15, font="Times New Roman", text="City")
    StateText = Text(window2, text="State", size=15, font="Times New Roman", grid=[0, 6])
    state = Text(window2, grid=[1, 6], size=15, font="Times New Roman", text="State")
    ZipText = Text(window2, text="Zip Code", size=15, font="Times New Roman", grid=[0, 7])
    ZipCode = Text(window2, grid=[1, 7], size=15, font="Times New Roman", text="Zip Code")
    # items header
    ItemsMessage = Text(window2, text="Items", size=18, font="Times New Roman", grid=[1, 8])

    ItemInfoListBox = ListBox(
        window2, items=[], grid=[0, 9, 4, 5], width=400, height=370, scrollbar=True
    )

    # whole right side listbox
    OrderInfoListBox = ListBox(
        window2, items=[], grid=[6, 0, 4, 30], width=400, height=600, scrollbar=True
    )

    PurchaseName.value = Order["order_name"]
    address.value = Order["order_address"]
    address2.value = Order["order_address2"]
    city.value = Order["order_city"]
    state.value = Order["order_state"]
    ZipCode.value = Order["order_zip"]

    EtsyData = Order["etsy_snapshot"]
    Keys = list(EtsyData.keys())
    for key in Keys:
        if EtsyData[key] == "":
            continue
        OrderInfoListBox.append("    " + key + " : " + str(EtsyData[key]))

    UIDs = Order["order_items_UID"]
    for uid in UIDs:
        item = order_items.search(
            (tinydb.Query().item_UID == uid) & (tinydb.Query().process_status == "UTILIZE")
        )[0]
        ItemKeys = list(item.keys())
        for key in ItemKeys:
            if item[key] == "":
                continue
            if key == "product_snapshot":  # if the key is the product snapshot, add the SubKeys
                SubKeys = list(item[key].keys())
                for SubKey in SubKeys:
                    if item[key][SubKey] == "":
                        continue
                    ItemInfoListBox.append("        " + SubKey + " : " + str(item[key][SubKey]))
                continue

            ItemInfoListBox.append("    " + key + " : " + str(item[key]))
        # add a blank line between items
        ItemInfoListBox.append("")


def EditOrder(main_window, database, OrderNumber):
    orders = database.table("Orders")
    Order = orders.search(
        (tinydb.Query().order_number == str(OrderNumber))
        & (tinydb.Query().process_status == "UTILIZE")
    )[0]

    try:  # test if the order is an easy cart order
        Order = Order["easy_cart_order"]
        ViewEasyCartOrder(main_window, database, OrderNumber)
        return
    except KeyError:
        pass

    try:  # test if the order is an etsy order
        Order = Order["etsy_order"]
        ViewEtsyOrder(main_window, database, OrderNumber)
        return
    except KeyError:
        pass

    # If the order is not an easy cart order or an etsy order, it is a custom order
    # is modifiable in details
    EditDefaultOrder(main_window, database, OrderNumber)
    return


def TaskExport(database):  # Export data to database
    global finish, name, description, priority, StartName
    global window2
    tasks = database.table("Tasks")

    if name.value == StartName:  # If the task name is the same as the original, update the task
        tasks.update(
            {
                "task_name": name.value,
                "task_description": description.value,
                "task_priority": priority.value,
                "process_status": "UTILIZE",
            },
            tinydb.Query().task_name == name.value,
        )
    else:  # If the task name is different, remove the old task and add a new one
        tasks.remove(
            (tinydb.Query().task_name == StartName) & (tinydb.Query().process_status == "UTILIZE")
        )
        tasks.insert(
            {
                "task_name": name.value,
                "task_description": description.value,
                "task_priority": priority.value,
                "process_status": "UTILIZE",
            }
        )
    window2.destroy()  # Close window


def CancelTask():
    global window2

    # Ask user if they are sure they want to cancel
    result = window2.yesno("Cancel", "Are you sure you want to cancel?")
    if result == True:  # If user is sure, close window
        window2.destroy()


def EditTask(main_window, database, TaskName):  # Create new task window
    global finish, name, description, priority, StartName
    global window2

    tasks = database.table("Tasks")
    EditingTask = tasks.search(
        (tinydb.Query().task_name == TaskName) & (tinydb.Query().process_status == "UTILIZE")
    )
    StartName = EditingTask[0]["task_name"]

    window2 = Window(main_window, title="Edit Task", layout="grid", width=1100, height=700)
    welcome_message = Text(window2, text="Edit Task", size=18, font="Times New Roman", grid=[1, 0])

    name_text = Text(window2, text="Task Name", size=15, font="Times New Roman", grid=[0, 1])
    name = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    description_text = Text(
        window2, text="Description", size=15, font="Times New Roman", grid=[0, 3]
    )
    description = TextBox(window2, grid=[1, 3], width=60, multiline=True, height=15)
    priority_text = Text(window2, text="Priority", size=15, font="Times New Roman", grid=[0, 7])
    priority = TextBox(window2, grid=[1, 7], width=10, text="0")
    # items header

    finish = PushButton(window2, command=TaskExport, text="Save", grid=[0, 19], args=[database])
    cancel = PushButton(window2, command=CancelTask, text="Cancel", grid=[1, 19])

    name.value = EditingTask[0]["task_name"]
    description.value = EditingTask[0]["task_description"]
    priority.value = EditingTask[0]["task_priority"]
