import random

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


def MonetaryAdd(Number1, Number2):
    """Adds two monetary values together with correct rounding for USD. (2 decimal places)

    Args:
        Number1 (Int, String, Decimal(Common/Class)): First Number to be added
        Number2 (Int, String, Decimal(Common/Class)): Second Number to be added

    Returns:
        Float: Sum of the two numbers
    """
    if not type(Number1) == Decimal:
        Number1 = Decimal(Number1)
    if not type(Number2) == Decimal:
        Number2 = Decimal(Number2)

    Number1.add(Number2)
    return round(Number1.__float__(), 2)


def MonetarySubtract(Number1, Number2):
    """Subtracts two monetary values together with correct rounding for USD. (2 decimal places)

    Args:
        Number1 (Int, String, Decimal(Common/Class)): First Number to be subtracted
        Number2 (Int, String, Decimal(Common/Class)): Second Number to be subtracted

    Returns:
        Float: Difference of the two numbers
    """
    if not type(Number1) == Decimal:
        Number1 = Decimal(Number1)
    if not type(Number2) == Decimal:
        Number2 = Decimal(Number2)

    Number1.subtract(Number2)
    return round(Number1.__float__(), 2)


def MonetaryMultiply(Number1, Number2):
    """Multiplies two monetary values together with correct rounding for USD. (2 decimal places)

    Args:
        Number1 (Int, String, Decimal(Common/Class)): First Number to be multiplied
        Number2 (Int, String, Decimal(Common/Class)): Second Number to be multiplied

    Returns:
        Float: Product of the two numbers
    """
    if not type(Number1) == Decimal:
        Number1 = Decimal(Number1)
    if not type(Number2) == Decimal:
        Number2 = Decimal(Number2)

    Number1.multiply(Number2)
    return round(Number1.__float__(), 2)


def MonetaryDivide(Number1, Number2):
    """Divides two monetary values together with correct rounding for USD. (2 decimal places)

    Args:
        Number1 (Int, String, Decimal(Common/Class)): First Number to be divided
        Number2 (Int, String, Decimal(Common/Class)): Second Number to be divided

    Returns:
        Float: Quotient of the two numbers
    """
    if not type(Number1) == Decimal:
        Number1 = Decimal(Number1)
    if not type(Number2) == Decimal:
        Number2 = Decimal(Number2)

    Number1.divide(Number2, 10)
    return round(Number1.__float__(), 2)


def MonetarySummation(List):
    """Sums a list of monetary values together with correct rounding for USD. (2 decimal places)

    Args:
        List (List[Int, String(May Include a $, Skipped if "NA"), Decimal(Common/Class)]): List of numbers to be summed

    Returns:
        Float: Sum of the numbers in the list
    """

    Sum = Decimal()
    for Number in List:
        if Number == "NA":
            continue
        if not type(Number) == Decimal:
            if type(Number) == str:  # If the number is a string
                Number = Decimal(Number.replace("$", ""))  # Remove the dollar sign if it is present
            Number = Decimal(Number)
        Sum.add(Number)
    return round(Sum.__float__(), 2)


def MonetaryAverage(List):
    """Finds the average of a list of monetary values together with correct rounding for USD. (2 decimal places)

    Args:
        List (List[Int, String, Decimal(Common/Class)]): List of numbers to be averaged

    Returns:
        Float: Average of the numbers in the list
    """
    Sum = Decimal(0)
    for Number in List:
        if not type(Number) == Decimal:
            Number = Decimal(Number)
        Sum = Sum.add(Number)
    return round(Sum.divide(len(List)).__float__(), 2)


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

    print(returnRows)
    return returnRows
