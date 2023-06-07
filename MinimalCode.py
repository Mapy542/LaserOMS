import tinydb
from tinydb.storages import MemoryStorage

db = [
    {
        "expense_ID": 111,
        "expense_name": "LAST_EXPENSE",
        "process_status": "IGNORE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Hammer Stock",
        "expense_quantity": "1",
        "expense_unit_price": "8",
        "expense_notes": "\n",
        "expense_date": "12-12-2021",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Wood Resupply",
        "expense_quantity": "1",
        "expense_unit_price": "95",
        "expense_notes": "\n",
        "expense_date": "12-12-2021",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Resin Pan",
        "expense_quantity": "1",
        "expense_unit_price": "20",
        "expense_notes": "\n",
        "expense_date": "12-12-2021",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Wood Resupply",
        "expense_quantity": "1",
        "expense_unit_price": "350",
        "expense_notes": "\n",
        "expense_date": "12-12-2021",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Bandsaw",
        "expense_quantity": "1",
        "expense_unit_price": "250",
        "expense_notes": "\n",
        "expense_date": "12-12-2021",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Bandsaw Blades",
        "expense_quantity": "1",
        "expense_unit_price": "50",
        "expense_notes": "\n",
        "expense_date": "12-12-2021",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Word Clock Supplies",
        "expense_quantity": "1",
        "expense_unit_price": "80",
        "expense_notes": "\n",
        "expense_date": "12-12-2021",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "1/4 Spiral Endmill",
        "expense_quantity": "1",
        "expense_unit_price": "20",
        "expense_notes": "\n",
        "expense_date": "2-12-2022",
        "process_status": "UTILIZE",
        "expense_image_path": "",
    },
    {
        "expense_name": "Shipping_Label-_2878292147",
        "expense_quantity": "1",
        "expense_unit_price": "7.20",
        "expense_notes": "\n",
        "expense_date": "05-07-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Shipping_Label-_2878292147.pdf",
        "process_status": "UTILIZE",
    },
    {
        "expense_name": "Shipping_Label-_2876623213",
        "expense_quantity": "1",
        "expense_unit_price": "7.20",
        "expense_notes": "\n",
        "expense_date": "05-07-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Shipping_Label-_2876623213.pdf",
        "process_status": "UTILIZE",
    },
    {
        "expense_name": "Shipping_Label-_2882817955",
        "expense_quantity": "1",
        "expense_unit_price": "13.74",
        "expense_notes": "\n",
        "expense_date": "05-16-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Shipping_Label-_2882817955.pdf",
        "process_status": "UTILIZE",
    },
    {
        "expense_name": "Shipping_Label-_2883954451",
        "expense_quantity": "1",
        "expense_unit_price": "9.59",
        "expense_notes": "\n",
        "expense_date": "05-16-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Shipping_Label-_2883954451.pdf",
        "process_status": "UTILIZE",
    },
    {
        "expense_name": "Lowes_more_wood_and_paint",
        "expense_quantity": "1",
        "expense_unit_price": "165.11",
        "expense_notes": "\n\n",
        "expense_date": "05-18-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Lowes_more_wood_and_paint.JPG",
        "process_status": "UTILIZE",
    },
    {
        "expense_name": "Shipping_Label-_2900550648",
        "expense_quantity": "1",
        "expense_unit_price": "7.00",
        "expense_notes": "\n",
        "expense_date": "05-26-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Shipping_Label-_2900550648.pdf",
        "process_status": "UTILIZE",
    },
    {
        "expense_name": "Shipping_Label-_2908328576",
        "expense_quantity": "1",
        "expense_unit_price": "7.00",
        "expense_notes": "\n",
        "expense_date": "05-31-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Shipping_Label-_2908328576.pdf",
        "process_status": "UTILIZE",
    },
    {
        "expense_name": "Shipping_Label-_2909910334",
        "expense_quantity": "1",
        "expense_unit_price": "7.00",
        "expense_notes": "\n",
        "expense_date": "05-31-2023",
        "expense_image_path": "\\\\10.0.0.104\\LeboeufLasing\\09-LaserOMS\\LaserOMS-Images\\Shipping_Label-_2909910334.pdf",
        "process_status": "UTILIZE",
    },
]


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
            print(self.value, self.power)

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
        for i in range(len(str(abs(self.value)))):
            Digits.append(str(self.get_digit(self.value, i)))
        if self.value < 0:
            Digits.insert(0, "-")
        if self.power < 0:
            Digits.insert(len(Digits) + self.power, ".")
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
                self.value *= 10 ** (self.power - Number2.power)
                self.power -= self.power - Number2.power
            else:
                Number2.value *= 10 ** (Number2.power - self.power)
                self.power = Number2.power - (Number2.power - self.power)

        self.value += Number2.value  # Add the values
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
                self.value *= 10 ** (self.power - Number2.power)
                self.power -= self.power - Number2.power
            else:
                Number2.value *= 10 ** (Number2.power - self.power)
                self.power = Number2.power - (Number2.power - self.power)

        self.value -= Number2.value  # Subtract the values
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

        print(self.value, self.power)

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

        if self.value / Number2.value is int:  # If the value is evenly divisible
            self.value /= Number2.value
            self.power -= Number2.power
            self.Simplify()
            return self

        # Divide with accuracy given for passes of long division
        ResultantDigits = []  # List of digits in the resultant decimal

        Dividend = self.get_digit(
            self.value, 0
        )  # First digit of the dividend to be divided

        UsedAccuracy = 0  # Number of digits of accuracy used in loop
        ExtraPower = (
            -1
        )  # Power of the decimal to be added to the resultant decimal (is positive to show decimal place is moved x places to the left: 10^(-x))

        Number1Index = (
            0  # Index of the digit of the dividend that has been used in the loop
        )

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
                Number1Index += (
                    1  # Increment the index of the digit of the dividend to be used
                )
                Dividend *= 10  # Multiply the dividend by 10 to add the next digit
                Dividend += self.get_digit(
                    self.value, Number1Index
                )  # Add the next digit of the dividend to the dividend
            else:  # If there are no more digits of the dividend to be used
                ExtraPower += 1  # Increment the power of the decimal to be added to the resultant decimal
                UsedAccuracy += (
                    1  # Increment the number of digits of accuracy used in the loop
                )
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


def GetExpenseStats(database):
    expenses = database.table("Expenses")  # load all expenses

    ActiveExpenses = expenses.search((tinydb.where("process_status") == "UTILIZE"))

    YearlyExpenses = {}
    MonthlyExpenses = {}

    for expense in ActiveExpenses:  # for each expense
        year = expense["expense_date"].split("-")[2]  # get year
        if len(year) > 4:
            # cut off the time or other data included after year
            year = year[: len(year) - 4]
        year = int(year)
        month = int(expense["expense_date"].split("-")[0])  # get month

        if year not in YearlyExpenses:  # add year if not in years
            YearlyExpenses[year] = Decimal("0")
            MonthlyExpenses[year] = {}
        # add month to months if not in months
        if month not in MonthlyExpenses[year]:
            MonthlyExpenses[year][month] = Decimal("0")

        total = Decimal(expense["expense_quantity"])
        total.multiply(expense["expense_unit_price"])  # calculate total
        YearlyExpenses[year].add(total)  # add total to applicable
        MonthlyExpenses[year][month].add(total)
        print(
            MonthlyExpenses[year][month],
            expense["expense_name"],
            month,
            total.value,
            total.power,
        )

    return YearlyExpenses, MonthlyExpenses


database = tinydb.TinyDB(storage=MemoryStorage)
database.table("Expenses").insert_multiple(db)

YearlyExpenses, MonthlyExpenses = GetExpenseStats(database)

for year in MonthlyExpenses:
    for month in MonthlyExpenses[year]:
        print(year, month, MonthlyExpenses[year][month])
