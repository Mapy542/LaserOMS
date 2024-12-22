class Decimal:  # Replacement for a float that has no floating point error
    def __init__(self, Number=0):
        """
        Args:
           Number (Int, String, Decimal): Number to be held as a decimal)
        """
        self._mantissa = 0  # Holds the value of the decimal
        self._power = 0  # Holds the power of the decimal ie  value * 10^power

        if type(Number) == int:
            self._mantissa = Number

        elif type(Number) == str:
            if "." in Number:
                while Number[-1] == "0":  # Remove trailing zeros
                    Number = Number[:-1]  # Remove last digit

                self._power = (
                    Number.index(".") - len(Number) + 1
                )  # Negative power as decimal is less than 1
                self._mantissa = int(Number.replace(".", ""))

            else:
                self._mantissa = int(Number)

        elif type(Number) == Decimal:
            self._mantissa, self._power = Number.copyValue()

        elif type(Number) == float:
            StringFloat = str(Number)
            if "." in StringFloat:
                self._mantissa = int(StringFloat.replace(".", ""))
                self._power = StringFloat.index(".") - len(StringFloat) + 1
            else:
                self._mantissa = int(StringFloat)

        else:
            print(Number)
            raise TypeError  # If the type is not supported raise an error

        self.Simplify()  # Simplify the decimal

    def copyValue(self):
        """Returns the value of the decimal for use in copying.

        Returns:
            Tuple: Mantissa, Power of the decimal
        """
        return self._mantissa, self._power

    def Simplify(self):
        """Simplifies the decimal by removing trailing zeros

        Returns:
            Decimal: Simplified decimal
        """

        if self._mantissa == 0:  # If the value is 0 the power is 0
            self._power = 0
            return self

        while (
            self._mantissa % 10 == 0
        ):  # Remove trailing zeros until scientific notation is reached
            self._mantissa /= 10
            self._power += 1

        self._mantissa = int(
            self._mantissa
        )  # Remove any decimal places that were not removed by the previous loop

        return self

    def __str__(self) -> str:  # Returns the decimal as a string

        strRep = str(self._mantissa)

        leadingZeros = 0
        if len(strRep) < abs(self._power):
            leadingZeros = abs(self._power) - len(strRep)

        if len(strRep) - self._power < 0:
            return (
                "0."
                + "0" * leadingZeros
                + strRep
                + "0" * (-self._power - len(strRep) - leadingZeros)
            )
        else:
            return (
                strRep[: self._power]
                + "."
                + strRep[self._power :]
                + "0" * (-self._power - len(strRep) - leadingZeros)
            )

        return strRep + "0" * self._power

    def __float__(self) -> float:  # Returns the decimal as a float
        return float(self._mantissa * 10**self._power)

    def __int__(self) -> int:  # Returns the decimal as an int
        return int(self._mantissa * 10**self._power)

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

        if selfCopy._power < secondCopy._power:
            selfCopy._mantissa *= 10 ** (secondCopy._power - selfCopy._power)
            selfCopy._power = secondCopy._power
        elif selfCopy._power > secondCopy._power:
            secondCopy._mantissa *= 10 ** (selfCopy._power - secondCopy._power)
        # secondCopy._power = selfCopy._power #unnecessary

        selfCopy._mantissa += secondCopy._mantissa
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
        otherCopy._mantissa *= -1

        return self.__add__(otherCopy)

    def __mul__(self, Number2=0):
        """Multiplies the value of the decimal by the value of Number2

        Args:
            Number2 (Int, String, Decimal): Number to be multiplied by the decimal

        Returns:
            Decimal: Decimal with the value of Number2 multiplied by it
        """

        Number2Copy = Decimal(Number2)
        selfCopy = Decimal(self)

        selfCopy._mantissa *= Number2Copy._mantissa  # Multiply the values
        selfCopy._power += Number2Copy._power  # Add the powers

        selfCopy.Simplify()  # Simplify the decimal

        return selfCopy

    def __truediv__(self, Number2=1):
        """Divides the value of the decimal by the value of Number2 down to the same number of decimal places as the decimal + 2

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal

        Returns:
            Decimal: Decimal with the value of itself divided by Number2
        """

        return self.finiteDivision(Number2, Accuracy=2)

    def __floordiv__(self, Number2=1):
        """Divides the value of the decimal by the value of Number2 down to nearest whole number

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal

        Returns:
            Decimal: Decimal with the value of itself divided by Number2
        """

        quotient = self.finiteDivision(Number2, Accuracy=2)

        if quotient._power < 0:
            return Decimal(0)

        if quotient._power < len(str(quotient._mantissa)):
            quotient._mantissa = int(str(quotient._mantissa)[: quotient._power])
            quotient._power = 0

        return quotient

    def __mod__(self, Number2=1):
        """
        Returns the remainder of the division of the decimal by Number2

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal

            Returns:
                Decimal: Decimal with the value of the remainder of the division of itself by Number2
        """

        return self.__sub__(self.__floordiv__(Number2).__mul__(Number2))

    def finiteDivision(self, Number2=1, Accuracy=2):
        """Divides the value of the decimal by the value of Number2

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal
            Accuracy (int, optional): Number of additional decimal places to calculate past the decimals of the two numbers. Defaults to 2.

        Returns:
            Decimal: Decimal with the value of itself divided by Number2
        """

        Number2Copy = Decimal(Number2)
        selfCopy = Decimal(self)

        if Number2Copy._mantissa == 0:
            raise ZeroDivisionError  # If Number2 is 0 raise an error

        if selfCopy._mantissa % Number2Copy._mantissa == 0:  # If the value is evenly divisible
            selfCopy._mantissa /= Number2Copy._mantissa
            selfCopy._power -= Number2Copy._power
            selfCopy.Simplify()
            return selfCopy

        # Divide with accuracy given for passes of long division
        ResultantDigits = []  # List of digits in the resultant decimal

        Dividend = selfCopy.get_digit(
            self._mantissa, 0
        )  # First digit of the dividend to be divided

        UsedAccuracy = 0  # Number of digits of accuracy used in loop
        ExtraPower = (
            -1
        )  # Power of the decimal to be added to the resultant decimal (is positive to show decimal place is moved x places to the left: 10^(-x))

        Number1Index = 0  # Index of the digit of the dividend that has been used in the loop

        while UsedAccuracy < Accuracy:
            if Dividend == 0:  # If the dividend is 0
                break  # Break out of the loop as the division is complete

            if (
                Dividend // Number2Copy._mantissa >= 1
            ):  # If the dividend is wholely divisible by the divisor
                ResultantDigits.append(
                    Dividend // Number2Copy._mantissa
                )  # Add the result of the division to the resultant decimal
                Dividend = (
                    Dividend % Number2Copy._mantissa
                )  # Set the dividend to the remainder of the division
            else:  # If the dividend is not wholely divisible by the divisor
                ResultantDigits.append(0)  # Add a 0 to the resultant decimal

            if (
                Number1Index < len(str(selfCopy._mantissa)) - 1
            ):  # If there are more digits of the dividend to be used
                Number1Index += 1  # Increment the index of the digit of the dividend to be used
                Dividend *= 10  # Multiply the dividend by 10 to add the next digit
                Dividend += self.get_digit(
                    selfCopy._mantissa, Number1Index
                )  # Add the next digit of the dividend to the dividend
            else:  # If there are no more digits of the dividend to be used
                ExtraPower += (
                    1  # Increment the power of the decimal to be added to the resultant decimal
                )
                UsedAccuracy += 1  # Increment the number of digits of accuracy used in the loop
                Dividend *= 10  # Multiply the dividend by 10 to add a 0 to the dividend

        OriginalValue = selfCopy._mantissa  # Store the original value of the decimal

        selfCopy._mantissa = int(
            "".join(map(str, ResultantDigits))
        )  # Set the value of the decimal to the resultant decimal

        if (
            OriginalValue < 0 or Number2Copy._mantissa < 0
        ):  # If the original value of the decimal was negative or the divisor was negative
            selfCopy._mantissa *= -1  # Make the resultant decimal negative

        selfCopy._power -= (
            Number2Copy._power + ExtraPower
        )  # Set the power of the decimal to the resultant decimal

        return selfCopy

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

        return self._mantissa == value._mantissa and self._power == value._power

    def __ne__(self, value):
        """Checks if the value of the decimal is not equal to another value

        Args:
            value (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is not equal to the value, False otherwise
        """
        return not self.__eq__(value)

    def __lt__(self, Number2=1):
        """Checks if the value of the decimal is less than another value

        Args:
            Number2 (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is less than the value, False otherwise
        """

        Number2Copy = Decimal(Number2)
        selfCopy = Decimal(self)

        if selfCopy._power < Number2Copy._power:
            selfCopy._mantissa *= 10 ** (Number2Copy._power - selfCopy._power)
            selfCopy._power = Number2Copy._power
        elif selfCopy._power > Number2Copy._power:
            Number2Copy._mantissa *= 10 ** (selfCopy._power - Number2Copy._power)
            Number2Copy._power = selfCopy._power

        return selfCopy._mantissa < Number2Copy._mantissa

    def __le__(self, Number2=1):
        """Checks if the value of the decimal is less than or equal to another value

        Args:
            Number2 (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is less than or equal to the value, False otherwise
        """
        return self.__lt__(Number2) or self.__eq__(Number2)

    def __gt__(self, Number2=1):
        """Checks if the value of the decimal is greater than another value

        Args:
            Number2 (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is greater than the value, False otherwise
        """
        return not self.__le__(Number2)

    def __ge__(self, Number2=1):
        """Checks if the value of the decimal is greater than or equal to another value

        Args:
            Number2 (Int, String, Decimal): Value to be compared to the decimal

        Returns:
            Bool: True if the value of the decimal is greater than or equal to the value, False otherwise
        """
        return not self.__lt__(Number2)

    def __abs__(self):
        """Returns the absolute value of the decimal

        Returns:
            Decimal: Absolute value of the decimal
        """
        selfCopy = Decimal(self)
        selfCopy._mantissa = abs(selfCopy._mantissa)
        return selfCopy

    def __neg__(self):
        """Returns the negative value of the decimal

        Returns:
            Decimal: Negative value of the decimal
        """
        selfCopy = Decimal(self)
        selfCopy._mantissa *= -1
        return selfCopy

    def __iadd__(self, Number2=0):
        """Adds the value of Number2 to the value of the decimal

        Args:
            Number2 (Int, String, Decimal): Number to be added to the decimal

        Returns:
            Decimal: Decimal with the value of Number2 added to it
        """
        self = self.__add__(Number2)
        return self

    def __isub__(self, Number2=0):
        """Subtracts the value of Number2 from the value of the decimal

        Args:
            Number2 (Int, String, Decimal): Number to be subtracted from the decimal

        Returns:
            Decimal: Decimal with the value of Number2 subtracted from it
        """
        self = self.__sub__(Number2)
        return self

    def __imul__(self, Number2=0):
        """Multiplies the value of the decimal by the value of Number2

        Args:
            Number2 (Int, String, Decimal): Number to be multiplied by the decimal

        Returns:
            Decimal: Decimal with the value of Number2 multiplied by it
        """

        self = self.__mul__(Number2)
        return self

    def __itruediv__(self, Number2=1):
        """Divides the value of the decimal by the value of Number2 down to the same number of decimal places as the decimal + 2

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal

        Returns:
            Decimal: Decimal with the value of itself divided by Number2
        """

        self = self.finiteDivision(Number2, Accuracy=2)
        return self

    def __ifloordiv__(self, Number2=1):
        """Divides the value of the decimal by the value of Number2 down to nearest whole number

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal

        Returns:
            Decimal: Decimal with the value of itself divided by Number2
        """

        quotient = self.finiteDivision(Number2, Accuracy=2)

        if quotient._power < 0:
            self = Decimal(0)

        if quotient._power < len(str(quotient._mantissa)):
            quotient._mantissa = int(str(quotient._mantissa)[: quotient._power])
            quotient._power = 0

        self = quotient
        return self

    def __imod__(self, Number2=1):
        """
        Returns the remainder of the division of the decimal by Number2

        Args:
            Number2 (Int, String, Decimal): Number to be divided by the decimal

            Returns:
                Decimal: Decimal with the value of the remainder of the division of itself by Number2
        """

        self = self.__sub__(self.__floordiv__(Number2).__mul__(Number2))
        return self

    def round(self, Accuracy=0):
        """Rounds the decimal to the given number of decimal places

        Args:
            Accuracy (int, optional): Number of decimal places to round the decimal to. Defaults to 0.

        Returns:
            Decimal: Decimal rounded to the given number of decimal places
        """

        selfCopy = Decimal(self)

        if Accuracy < 0:
            raise ValueError  # If the accuracy is negative raise an error

        truncation = -selfCopy._power - Accuracy
        if truncation >= len(str(selfCopy._mantissa)):
            return Decimal(0)

        selfCopy._mantissa = int(str(selfCopy._mantissa)[:truncation])
        selfCopy._power += truncation

        return selfCopy


if __name__ == "__main__":
    a = Decimal("15.123456987654321")
    b = a.round(2)
    print(a)
    print(b)
