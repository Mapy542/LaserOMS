import random

import guizero
import tinydb

# Common functions to be used throughout the project


def CleanedFileName(FileName):
    """Takes Path String and returns a cleaned version of the string that can be used as a file name

    Args:
        FileName (str): file name to be cleaned NOT WHOLE PATH NOR EXTENSION

    Returns:
        str: Cleaned file name
    """
    FileName = FileName.replace(" ", "_")
    FileName = FileName.replace("/", "-")
    FileName = FileName.replace("\\", "-")
    FileName = FileName.replace(":", "-")
    FileName = FileName.replace("*", "-")
    FileName = FileName.replace("?", "-")
    FileName = FileName.replace('"', "-")
    FileName = FileName.replace("<", "-")
    FileName = FileName.replace(">", "-")
    FileName = FileName.replace("|", "-")
    FileName = FileName.replace(".", "-")  # Remove false file extension

    return FileName


# UID Functions
def MakeUIDs(order_items, ItemCount):
    """Makes a list of random and UNIQUE UIDs

    Args:
        order_items (TinyDB/Table/OrderItems): Table of order items to check for UIDs
        ItemCount (Int): Number of UIDs to make

    Returns:
        List[Int]: List of random and unique UIDs
    """
    allUIDs = []
    order_items = order_items.search(tinydb.Query().process_status == "UTILIZE")  # Get all items
    if order_items == []:  # If there are no items in the database, return a list of random UIDs
        returnUIDs = []
        returnUIDs.append(random.randint(1000000, 9999999))
        for i in range(ItemCount):
            UID = random.randint(1000000, 9999999)
            while UID in returnUIDs:
                UID = random.randint(1000000, 9999999)
            returnUIDs.append(UID)
        return returnUIDs
    for item in order_items:
        allUIDs.append(item["item_UID"])  # Add all UIDs to a list
    returnUIDs = []
    for i in range(ItemCount):
        UID = random.randint(1000000, 9999999)  # Generate a random UID
        while UID in allUIDs:  # If the UID is already in the database, generate a new one
            UID = random.randint(1000000, 9999999)  # Generate a random UID
        returnUIDs.append(UID)
    return returnUIDs  # Return the list of UIDs


def MakeOrderID(orders):
    """Makes a random and UNIQUE order ID

    Args:
        orders (TinyDB/Table/Orders): Table of orders to check for order IDs

    Returns:
        Int: Random and unique order ID
    """
    allIDs = []
    AvailableOrders = orders.search(tinydb.Query().process_status == "UTILIZE")  # Get all orders
    for order in AvailableOrders:
        # Add all order IDs to a list
        allIDs.append(int(order["order_number"]))
    order_ID = 112
    while order_ID in allIDs:  # If the order ID is already in the database, generate a new one
        order_ID += 1
    return order_ID


# Text Alignment Functions
def ColumnAlignment(Rows=[[], []]):
    """Aligns the columns of a list of rows by the longest string in each column

    Args:
        Rows (list, optional): Row array of columns. Defaults to [[],[]].

    Returns:
        list: Aligned rows as strings including whitespace
    """
    if Rows == [] or Rows == [[]] or Rows == [[], []]:  # If there are no rows, return an empty list
        return []

    maxLengths = []

    for i in range(len(Rows[0])):  # create a length for each column
        maxLengths.append(0)

    for row in Rows:  # find the longest string in each column
        for i in range(len(row)):
            if len(str(row[i])) > maxLengths[i]:
                maxLengths[i] = len(str(row[i]))

    returnRows = []

    for row in Rows:  # add whitespace to each string to make them the same length
        returnRow = []
        for i in range(len(row)):
            returnRow.append(str(row[i]) + " " * (maxLengths[i] - len(str(row[i]))))
        returnRows.append(" ".join(returnRow))

    return returnRows


def makeWindowFullscreen(window: guizero.Window):
    """Makes a guizero window fullscreen (No title bar/controls)

    Args:
        window (guizero.Window): Window to make fullscreen
    """
    window.tk.attributes("-fullscreen", True)
    window.tk.attributes("-topmost", True)


def maximizeWindow(window: guizero.Window):
    """Maximizes a guizero window

    Args:
        window (guizero.Window): Window to maximize
    """
    window.tk.attributes("-zoomed", True)
