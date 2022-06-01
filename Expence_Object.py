from datetime import datetime


class Expence():
    def __init__(self, name = "", cost = 0, quantity = 0, date = datetime.today().strftime('%m-%d-%Y'), category = "", description = ""):
        self.name = name
        self.cost = cost
        self.quantity = quantity
        self.date = date
        self.category = category
        self.description = description

    def getName(self):
        return self.name

    def getUnitCost(self):
        return self.cost

    def getTotalCost(self):
        return self.cost * self.quantity

    def getQuantity(self):
        return self.quantity

    def getDate(self):
        return self.date

    def getCategory(self):
        return self.category

    def getDiscription(self):
        return self.description

    def changeName(self, name):
        self.name = name

    def changeCost(self, cost):
        self.cost = int(cost)

    def changeQuantity(self, quantity):
        self.quantity = int(quantity)

    def changeDate(self, date):
        self.date = date

    def changeCategory(self, category):
        self.category = category

    def changeDiscription(self, description):
        self.description = description

    def __str__(self):
        return self.name + " $" + self.cost

    def isNonEmpty(self):
        return not (self.name == "Empty" or self.name == "")

    def isOrder(self):
        return False