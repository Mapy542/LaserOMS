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

        strRep = str(self.value)

        leadingZeros = 0
        if len(strRep) < abs(self.power):
            leadingZeros = abs(self.power) - len(strRep)

        if self.power < 0:
            return "0." + "0" * leadingZeros + strRep + "0" * -self.power

        return strRep + "0" * self.power

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

    def __add__(self, Number2=0):
        """Adds the value of Number2 to the value of the decimal

        Args:
            Number2 (Int, String, Decimal): Number to be added to the decimal

        Returns:
            Decimal: Decimal with the value of Number2 added to it
        """
        if not type(Number2) == Decimal:
            Number2 = Decimal(Number2)

        selfCopy = Decimal(self)
        secondCopy = Decimal(Number2)

        if selfCopy.power < secondCopy.power:
            selfCopy.value *= 10 ** (secondCopy.power - selfCopy.power)
            selfCopy.power = secondCopy.power
        elif selfCopy.power > secondCopy.power:
            secondCopy.value *= 10 ** (selfCopy.power - secondCopy.power)
        # secondCopy.power = selfCopy.power #unnecessary

        selfCopy.value += secondCopy.value
        selfCopy.Simplify()

        return selfCopy

    def __sub__(self, Number2=0):
        """Subtracts the value of Number2 from the value of the decimal

        Args:
            Number2 (Int, String, Decimal): Number to be subtracted from the decimal

        Returns:
            Decimal: Decimal with the value of Number2 subtracted from it
        """
        if not type(Number2) == Decimal:
            Number2 = Decimal(Number2)

        otherCopy = Decimal(Number2)
        otherCopy.value *= -1

        return self.__add__(otherCopy)

    def __mul__(self, Number2=0):
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

    def __truediv__(self, Number2=1):
        """Divides the value of the decimal by the value of Number2 down to the same number of decimal places as the decimal

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal

        Returns:
            Decimal: Decimal with the value of itself divided by Number2
        """

        self.finiteDivision(Number2, Accuracy=0)

    def finiteDivision(self, Number2=1, Accuracy=2):
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

    def __eq__(self, value):
        """Checks if the value of the decimal is equal to another value

        Args:
            value (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is equal to the value, False otherwise
        """
        if not type(value) == Decimal:
            value = Decimal(value)

        self.Simplify()  # Simplify the decimals to make sure no incorrect notation affects the comparison
        value.Simplify()

        return self.value == value.value and self.power == value.power

    def __ne__(self, value):
        """Checks if the value of the decimal is not equal to another value

        Args:
            value (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is not equal to the value, False otherwise
        """
        return not self.__eq__(value)

    def __lt__(self, value):
        """Checks if the value of the decimal is less than another value

        Args:
            value (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is less than the value, False otherwise
        """
        if not type(value) == Decimal:
            value = Decimal(value)

        self.Simplify()
        value.Simplify()

        selfSign = self.value < 0
        valueSign = value.value < 0

        if selfSign and not valueSign:  # If self is negative and value is positive
            return True

        if (selfSign and valueSign and self.power > value.power) or (
            not selfSign and not valueSign and self.power < value.power
        ):  # compare the powers if both are negative or both are positive
            return True

        if self.power == value.power:
            return self.value < value.value
