import Decimal


class Money(Decimal):
    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def add(self, value):
        self.value += value

    def subtract(self, value):
        self.value -= value

    def multiply(self, value):
        self.value *= value

    def __float__(self):
        return round(self.value, 2)
