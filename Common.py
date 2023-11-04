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


class Decimal:  # Replacement for a float that has no floating point error
    def __init__(self, Number=0):
        """
        Args:
           Number (Int, String, Decimal): Number to be held as a decimal)
        """
        self.value = 0  # Holds the value of the decimal
        self.power = 0  # Holds the power of the decimal ie  value * 10^power

        if type(Number) == int:
            self.value = Number

        elif type(Number) == str:
            if "." in Number:
                while Number[-1] == "0":  # Remove trailing zeros
                    Number = Number[:-1]  # Remove last digit

                self.power = (
                    Number.index(".") - len(Number) + 1
                )  # Negative power as decimal is less than 1
                self.value = int(Number.replace(".", ""))

            else:
                self.value = int(Number)

        elif type(Number) == Decimal:
            self.value = Number.value
            self.power = Number.power

        elif type(Number) == float:
            StringFloat = str(Number)
            if "." in StringFloat:
                self.value = int(StringFloat.replace(".", ""))
                self.power = StringFloat.index(".") - len(StringFloat) + 1
            else:
                self.value = int(StringFloat)

        else:
            print(Number)
            raise TypeError  # If the type is not supported raise an error

        self.Simplify()  # Simplify the decimal

    def Simplify(self):
        """Simplifies the decimal by removing trailing zeros

        Returns:
            Decimal: Simplified decimal
        """

        if self.value == 0:  # If the value is 0 the power is 0
            self.power = 0
            return self

        while self.value % 10 == 0:
            self.value /= 10
            self.power += 1

        self.value = int(self.value)

        return self

    def __str__(self) -> str:  # Returns the decimal as a string
        Digits = []

        if self.value == 0:  # If the value is 0 return 0
            return "0"

        if self.power > 0:  # If the power is positive multiply the value by 10^power
            MutatedValue = self.value * (10**self.power)
        else:
            MutatedValue = self.value

        for i in range(len(str(abs(MutatedValue)))):  # Add each digit to the list
            Digits.append(str(self.get_digit(MutatedValue, i)))

        if self.power < 0:  # If the power is negative add a decimal point
            Digits.insert(len(Digits) + self.power, ".")

        if self.value < 0:  # If the value is negative add a negative sign
            Digits.insert(0, "-")

        return "".join(Digits)

    def __float__(self) -> float:  # Returns the decimal as a float
        return float(self.value * 10**self.power)

    def __int__(self) -> int:  # Returns the decimal as an int
        return int(self.value * 10**self.power)

    def get_digit(self, number, n):
        """Returns the nth digit of a number

        Args:
            number (int): Number to get the digit from
            n (int): Digit to get

        Returns:
            int: nth digit of number
        """
        if n < 0:
            raise IndexError  # If n is negative raise an error

        if n >= len(str(abs(number))):
            raise IndexError  # If n is greater than the number of digits in number raise an error

        number = abs(
            number
        )  # Make the number positive so that the index does not include a negative sign

        return int(str(number)[n])

    def add(self, Number2=0):
        """Adds the value of Number2 to the value of the decimal

        Args:
            Number2 (Int, String, Decimal): Number to be added to the decimal

        Returns:
            Decimal: Decimal with the value of Number2 added to it
        """
        if not type(Number2) == Decimal:
            Number2 = Decimal(Number2)

        if (
            not self.power == Number2.power
        ):  # If the powers are not equal make them equal by multiplying by 10^difference
            if self.power > Number2.power:
                Copy1 = Decimal(self)
                Copy1.value *= 10 ** (self.power - Number2.power)
                Copy1.power = Number2.power
                Copy2 = Decimal(Number2)
            else:
                Copy2 = Decimal(Number2)
                Copy2.value *= 10 ** (Number2.power - self.power)
                Copy2.power = self.power
                Copy1 = Decimal(self)
        else:
            Copy1 = Decimal(self)
            Copy2 = Decimal(Number2)

        self.value = Copy1.value + Copy2.value
        self.power = Copy1.power
        self.Simplify()  # Simplify the decimal

        # return self

    def subtract(self, Number2=0):
        """Subtracts the value of Number2 from the value of the decimal

        Args:
            Number2 (Int, String, Decimal): Number to be subtracted from the decimal

        Returns:
            Decimal: Decimal with the value of Number2 subtracted from it
        """
        if not type(Number2) == Decimal:
            Number2 = Decimal(Number2)

        if (
            not self.power == Number2.power
        ):  # If the powers are not equal make them equal by multiplying by 10^difference
            if self.power > Number2.power:
                Copy1 = Decimal(self)
                Copy1.value *= 10 ** (self.power - Number2.power)
                Copy1.power = Number2.power
                Copy2 = Decimal(Number2)
            else:
                Copy2 = Decimal(Number2)
                Copy2.value *= 10 ** (Number2.power - self.power)
                Copy2.power = self.power
                Copy1 = Decimal(self)
        else:
            Copy1 = Decimal(self)
            Copy2 = Decimal(Number2)

        self.value = Copy1.value - Copy2.value
        self.power = Copy1.power
        self.Simplify()  # Simplify the decimal

        # return self

    def multiply(self, Number2=0):
        """Multiplies the value of the decimal by the value of Number2

        Args:
            Number2 (Int, String, Decimal): Number to be multiplied by the decimal

        Returns:
            Decimal: Decimal with the value of Number2 multiplied by it
        """
        if not type(Number2) == Decimal:  # If Number2 is not a decimal make it one
            Number2 = Decimal(Number2)

        self.value *= Number2.value  # Multiply the values
        self.power += Number2.power  # Add the powers

        self.Simplify()  # Simplify the decimal

        # return self

    def divide(self, Number2=1, Accuracy=2):
        """Divides the value of the decimal by the value of Number2

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal
            Accuracy (int, optional): Number of additional decimal places to calculate past the decimals of the two numbers. Defaults to 2.

        Returns:
            Decimal: Decimal with the value of itself divided by Number2
        """

        if not type(Number2) == Decimal:  # If Number2 is not a decimal make it one
            Number2 = Decimal(Number2)

        if Number2.value == 0:
            raise ZeroDivisionError  # If Number2 is 0 raise an error

        if self.value % Number2.value == 0:  # If the value is evenly divisible
            self.value /= Number2.value
            self.power -= Number2.power
            self.Simplify()
            return self

        # Divide with accuracy given for passes of long division
        ResultantDigits = []  # List of digits in the resultant decimal

        Dividend = self.get_digit(self.value, 0)  # First digit of the dividend to be divided

        UsedAccuracy = 0  # Number of digits of accuracy used in loop
        ExtraPower = (
            -1
        )  # Power of the decimal to be added to the resultant decimal (is positive to show decimal place is moved x places to the left: 10^(-x))

        Number1Index = 0  # Index of the digit of the dividend that has been used in the loop

        while UsedAccuracy < Accuracy:
            if Dividend == 0:  # If the dividend is 0
                break  # Break out of the loop as the division is complete

            if (
                Dividend // Number2.value >= 1
            ):  # If the dividend is wholely divisible by the divisor
                ResultantDigits.append(
                    Dividend // Number2.value
                )  # Add the result of the division to the resultant decimal
                Dividend = (
                    Dividend % Number2.value
                )  # Set the dividend to the remainder of the division
            else:  # If the dividend is not wholely divisible by the divisor
                ResultantDigits.append(0)  # Add a 0 to the resultant decimal

            if (
                Number1Index < len(str(self.value)) - 1
            ):  # If there are more digits of the dividend to be used
                Number1Index += 1  # Increment the index of the digit of the dividend to be used
                Dividend *= 10  # Multiply the dividend by 10 to add the next digit
                Dividend += self.get_digit(
                    self.value, Number1Index
                )  # Add the next digit of the dividend to the dividend
            else:  # If there are no more digits of the dividend to be used
                ExtraPower += (
                    1  # Increment the power of the decimal to be added to the resultant decimal
                )
                UsedAccuracy += 1  # Increment the number of digits of accuracy used in the loop
                Dividend *= 10  # Multiply the dividend by 10 to add a 0 to the dividend

        OriginalValue = self.value  # Store the original value of the decimal

        self.value = int(
            "".join(map(str, ResultantDigits))
        )  # Set the value of the decimal to the resultant decimal

        if (
            OriginalValue < 0 ^ Number2.value < 0
        ):  # If the original value of the decimal was negative or the divisor was negative
            self.value *= -1  # Make the resultant decimal negative

        self.power -= (
            Number2.power + ExtraPower
        )  # Set the power of the decimal to the resultant decimal

        # return self


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
