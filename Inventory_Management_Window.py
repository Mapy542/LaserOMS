import tinydb
from guizero import Combo, ListBox, PushButton, Text, TextBox, TitleBox, Window

import Common


def UpdateListbox(InfoBox, database):
    """Updates the listbox with the current inventory groups

    Args:
        InfoBox (ListBox): The listbox to update
        database (TinyDB Database): The Laser OMS database
    """
    global ViewStyle

    previousValue = ViewStyle.value
    if ViewStyle.value == "Group Overview":
        ShowGroupOverview(InfoBox, database)
    else:
        ShowIndividualInventory(InfoBox, ViewStyle.value, database)

    ViewStyle.clear()
    Names = GetInventoryGroups(database)
    Names.insert(0, "Group Overview")
    for name in Names:
        ViewStyle.append(name)
    ViewStyle.value = previousValue  ##?? not sure if this is the intended behavior


def ShowGroupOverview(InfoBox, database):
    """Shows the overview of all inventory groups

    Args:
        InfoBox (ListBox): The listbox to update
        database (TinyDB Database): The Laser OMS database
    """
    inventories = database.table("Inventories")
    inventories = inventories.all()
    InfoBox.clear()
    InfoBox.append("Inventory Group Overview")

    for inventory in inventories:
        try:  # If the inventory has a pricing style, use it
            pricingOption = inventory["inventory_pricing_style"]
        except:  # If the inventory does not have a pricing style, use the default
            pricingstyles = database.table("Product_Pricing_Styles")
            pricingOption = pricingstyles.search(tinydb.where("process_status") == "UTILIZE")[0][
                "style_name"
            ]
        quantity = sum([item["item_quantity"] for item in inventory["inventory_items"]])
        value = Common.MonetarySummation(
            [
                Common.MonetaryMultiply(
                    item["item_quantity"], item["product_snapshot"][pricingOption]
                )
                for item in inventory["inventory_items"]
            ]
        )

        InfoBox.append(
            str(inventory["inventory_name"])
            + ",       Quantity: "
            + str(quantity)
            + "   Value: "
            + str(value)
        )


def ShowIndividualInventory(InfoBox, InventoryName, database):
    inventories = database.table("Inventories")

    try:
        inventory = inventories.search(tinydb.where("inventory_name") == InventoryName)[0]
    except:
        return False

    try:  # If the inventory has a pricing style, use it
        pricingOption = inventory["inventory_pricing_style"]
    except:  # If the inventory does not have a pricing style, use the default
        pricingStyles = database.table("Product_Pricing_Styles")
        pricingOption = pricingStyles.search(tinydb.where("process_status") == "UTILIZE")[0][
            "style_name"
        ]
    quantity = sum([item["item_quantity"] for item in inventory["inventory_items"]])
    value = Common.MonetarySummation(
        [
            Common.MonetaryMultiply(item["item_quantity"], item["product_snapshot"][pricingOption])
            for item in inventory["inventory_items"]
        ]
    )

    InfoBox.clear()
    InfoBox.append(
        str(inventory["inventory_name"])
        + ",       Quantity: "
        + str(quantity)
        + "   Value: "
        + str(value)
    )
    InfoBox.append("")
    for item in inventory["inventory_items"]:
        InfoBox.append(
            str(item["product_name"])
            + ",       Quantity: "
            + str(item["item_quantity"])
            + "   Value: "
            + str(
                Common.MonetaryMultiply(
                    item["item_quantity"], item["product_snapshot"][pricingOption]
                )
            )
        )


def GetInventoryGroups(database):
    """Returns a list of all Inventory Groups in the database

    Args:
        database (TinyDB Database): The Laser OMS database

    Returns:
        List of strings: List of all Inventory Group names
    """
    Inventories = database.table("Inventories")
    names = [Inventory["inventory_name"] for Inventory in Inventories.all()]
    if names == None:
        return []
    return names


def SubmitNewInventory(name, PricingStyle, popup, database):
    if name.value == None:  # If no name is entered, do not create the inventory cancel
        popup.destroy()
        return False
    if name in GetInventoryGroups(database):
        popup.error("Error", "Inventory already exists")
        return False

    inventories = database.table("Inventories")

    inventories.insert(
        {
            "inventory_name": name.value,
            "inventory_items": [],
            "inventory_pricing_style": PricingStyle.value.replace(" ", "_"),
            "process_status": "UTILIZE",
        }
    )
    popup.destroy()

    UpdateListbox(InfoBox, database)


def NewInventory(window2, database):
    """Creates a new Inventory Group

    Args:
        window2 (GuiZeroWindow): The window to display the prompt on
        database (TinyDb): The Laser OMS database
    """
    inventories = database.table("Inventories")
    pricingStyles = database.table("Product_Pricing_Styles")
    activeStyles = pricingStyles.search(tinydb.where("process_status") == "UTILIZE")
    styleNames = [style["style_name"] for style in activeStyles]

    popup = Window(window2, title="New Inventory", layout="grid", width=300, height=100)
    Text(popup, text="Inventory Name", grid=[0, 0, 1, 1])
    name = TextBox(popup, grid=[1, 0, 1, 1])
    PricingStyle = Combo(popup, options=styleNames, grid=[0, 1, 1, 1])
    Submit = PushButton(
        popup,
        text="Submit",
        grid=[1, 1, 1, 1],
        args=[name, PricingStyle, popup, database],
        command=SubmitNewInventory,
    )


def DeleteInventory(window2, database):
    """Deletes an Inventory Group

    Args:
        window2 (GuiZeroWindow): The window to display the prompt on
        database (TinyDb): The Laser OMS database
    """

    def RemoveInventory(SubWindow, InventoryCombo, database):
        SubWindow.yesno(
            "Delete Inventory", "Are you sure you want to delete " + str(InventoryCombo.value) + "?"
        )
        inventories = database.table("Inventories")
        inventories.remove(tinydb.where("inventory_name") == InventoryCombo.value)
        UpdateListbox(InfoBox, database)
        SubWindow.destroy()

    SubWindow = Window(window2, title="Delete Inventory", layout="grid", width=300, height=100)
    InventoryCombo = Combo(SubWindow, options=GetInventoryGroups(database), grid=[0, 0, 1, 1])
    Delete = PushButton(
        SubWindow,
        text="Delete",
        grid=[0, 1, 1, 1],
        args=[SubWindow, InventoryCombo, database],
        command=RemoveInventory,
    )


def ModifyInventory(window2, database, InfoBox):
    def GetProducts(database):
        products = database.table("Products")
        return products.search(tinydb.where("process_status") == "UTILIZE")

    def AddProduct(editWindow, database, ProductsListbox, Quantity):
        if ProductsListbox.value == None or ProductsListbox.value == []:
            editWindow.error("Error", "No Product Selected")
            return

        inventories = database.table("Inventories")
        inventory = inventories.search(
            tinydb.where("inventory_name") == InfoBox.value[0].split(",")[0]
        )[0]

        if ProductsListbox.value in [item["product_name"] for item in inventory["inventory_items"]]:
            for i in range(len(inventory["inventory_items"])):
                if inventory["inventory_items"][i]["product_name"] == ProductsListbox.value:
                    inventory["inventory_items"][i]["item_quantity"] += int(Quantity.value)
        else:
            products = database.table("Products")
            Snapshot = products.search(tinydb.where("product_name") == ProductsListbox.value)[0]

            inventory["inventory_items"].append(
                {
                    "product_name": ProductsListbox.value,
                    "item_quantity": int(Quantity.value),
                    "product_snapshot": Snapshot,
                }
            )

        ReloadContents(Contents, database, InfoBox)

    def ReloadContents(Contents, database, InfoBox):
        Contents.clear()
        inventories = database.table("Inventories")
        inventory = inventories.search(
            tinydb.where("inventory_name") == InfoBox.value[0].split(",")[0]
        )[0]
        for item in inventory["inventory_items"]:
            Contents.append(
                str(item["product_name"]) + ",       Quantity: " + str(item["item_quantity"])
            )

    def QuantityUpdate(editWindow, database, Contents, QuantityDeltaValue):
        if Contents.value == None or Contents.value == []:
            editWindow.error("Error", "No Product Selected")
            return

        inventories = database.table("Inventories")
        inventory = inventories.search(
            tinydb.where("inventory_name") == InfoBox.value[0].split(",")[0]
        )[0]

        for i in range(len(inventory["inventory_items"])):
            if inventory["inventory_items"][i]["product_name"] == Contents.value[0].split(",")[0]:
                if (
                    inventory["inventory_items"][i]["item_quantity"] + int(QuantityDeltaValue.value)
                    < 0
                ):
                    editWindow.error("Error", "Cannot have negative quantity")
                    return

                inventory["inventory_items"][i]["item_quantity"] += int(QuantityDeltaValue.value)

        ReloadContents(Contents, database, InfoBox)

    def RemoveItem(editWindow, database, Contents):
        if Contents.value == None or Contents.value == []:
            editWindow.error("Error", "No Product Selected")
            return

        editWindow.yesno(
            "Remove Item",
            "Are you sure you want to remove " + Contents.value[0].split(",")[0] + "?",
        )

        inventories = database.table("Inventories")
        inventory = inventories.search(
            tinydb.where("inventory_name") == InfoBox.value[0].split(",")[0]
        )[0]

        for i in range(len(inventory["inventory_items"])):
            if inventory["inventory_items"][i]["product_name"] == Contents.value[0].split(",")[0]:
                inventory["inventory_items"].pop(i)
                break

        ReloadContents(Contents, database, InfoBox)

    def closeEditWindow(editWindow, database, InfoBox):
        editWindow.destroy()
        UpdateListbox(InfoBox, database)

    if InfoBox.value == None or InfoBox.value == []:
        window2.error("Error", "No Inventory Selected")
        return

    editWindow = Window(window2, title="Add to Inventory", layout="grid", width=600, height=600)
    Contents = ListBox(
        editWindow,
        items=[],
        multiselect=True,
        width=500,
        height=200,
        scrollbar=True,
        grid=[0, 0, 4, 5],
    )
    Contents.font = "Courier"
    ReloadContents(Contents, database, InfoBox)

    addDiv = TitleBox(editWindow, text="Add to Inventory", grid=[0, 5, 2, 3], layout="grid")

    Products = [product["product_name"] for product in GetProducts(database)]
    ProductsListbox = ListBox(
        addDiv,
        items=Products,
        multiselect=False,
        width=200,
        height=200,
        scrollbar=True,
        grid=[0, 0, 2, 3],
    )
    ProductsListbox.font = "Courier"

    Quantity = TextBox(addDiv, grid=[0, 4, 1, 1], width=10, text="1")
    AddButton = PushButton(
        addDiv,
        text="Add",
        grid=[1, 4, 1, 1],
        args=[editWindow, database, ProductsListbox, Quantity],
        command=AddProduct,
    )

    modifyDiv = TitleBox(editWindow, text="Modify Inventory", grid=[2, 5, 2, 1], layout="grid")

    QuantityDeltaValue = TextBox(modifyDiv, grid=[0, 10, 1, 1], width=10, text="1")
    QuantityDelta = PushButton(
        modifyDiv,
        text="Add/Subtract Quantity",
        grid=[1, 10, 1, 1],
        args=[editWindow, database, Contents, QuantityDeltaValue],
        command=QuantityUpdate,
    )

    RemoveItemButton = PushButton(
        modifyDiv,
        text="Delete",
        grid=[0, 11, 1, 1],
        args=[editWindow, database, Contents],
        command=RemoveItem,
    )

    closebutton = PushButton(
        editWindow,
        text="Close",
        grid=[0, 8, 1, 1],
        command=closeEditWindow,
        args=[editWindow, database, InfoBox],
    )


def OrderModifyInventory(window, database, inventory_name, productsQuantity):
    """Modifies the inventory of a specific inventory group by a specific amount specified in an order

    Args:
        window (GuiZero): The window to display the prompt/errors on
        database (TinyDB): The Laser OMS database
        inventory_name (Str): The name of the inventory group to modify
        productsQuantity (List[product_name, quantity]): The product and quantity to modify the inventory by. Quantity is subtractive, but may be positive or negative


    Returns:
        Bool: True if successful, False if not
    """
    inventories = database.table("Inventories")
    try:
        inventory = inventories.search(tinydb.where("inventory_name") == inventory_name)[0]
    except:
        window.error("Error", "Inventory does not exist")
        return False
    for j in range(len(productsQuantity)):
        found = False
        for i in range(len(inventory["inventory_items"])):
            if inventory["inventory_items"][i]["product_name"] == productsQuantity[j][0]:
                if (
                    inventory["inventory_items"][i]["item_quantity"] - int(productsQuantity[j][1])
                    < 0
                ):
                    window.error(
                        "Quantity Error",
                        "Cannot have negative quantity in inventory. Check order and reconcile inventory.",
                    )
                    return False

                inventory["inventory_items"][i]["item_quantity"] -= int(productsQuantity[j][1])
                found = True
                break
        if not found:
            window.error(
                "Error",
                "Product "
                + productsQuantity[j][0]
                + " does not exist in inventory "
                + inventory_name
                + ". Ignoring product.",
            )

    return True


def ListingDisplay(main_window, database):
    global InfoBox
    global window2
    global ViewStyle
    window2 = Window(main_window, title="Inventories", layout="grid", width=1100, height=700)

    WelcomeMessage = Text(
        window2, text="Inventory Groups", size=15, font="Times New Roman", grid=[0, 0, 4, 1]
    )
    InfoBox = ListBox(
        window2,
        items=[],
        multiselect=True,
        width=1000,
        height=500,
        scrollbar=True,
        grid=[0, 1, 4, 5],
    )
    InfoBox.font = "Courier"

    Names = GetInventoryGroups(database)
    Names.insert(0, "Group Overview")

    # options
    RebuildButton = PushButton(
        window2,
        text="Reload",
        command=UpdateListbox,
        grid=[5, 2, 1, 1],
        args=[InfoBox, database],
    )
    ViewStyle = Combo(
        window2,
        options=Names,
        grid=[5, 3, 1, 1],
        selected="Group Overview",
    )

    UpdateListbox(InfoBox, database)

    # actions
    NewInventoryButton = PushButton(
        window2,
        text="New Inventory",
        command=NewInventory,
        grid=[0, 6, 1, 1],
        args=[window2, database],
    )
    DeleteInventoryButton = PushButton(
        window2,
        text="Delete Inventory",
        command=DeleteInventory,
        grid=[1, 6, 1, 1],
        args=[window2, database],
    )
    AddToInventoryButton = PushButton(
        window2,
        text="Update Inventory",
        command=ModifyInventory,
        grid=[2, 6, 1, 1],
        args=[window2, database, InfoBox],
    )
