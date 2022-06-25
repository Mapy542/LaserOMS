from datetime import datetime

#data handling class for an expence

class Expence():
    def __init__(self, name = "", cost = 0, quantity = 0, date = datetime.today().strftime('%m-%d-%Y'), category = "", description = ""):
        self.name = name #label for expence
        self.cost = cost #cost
        self.quantity = quantity #qantity   total cost = cost * quantity
        self.date = date #date saved or paid
        self.category = category #could be sorted via category
        self.description = description #more details if needed

#basic acsessor methods
#maybe not necesary in python but JAVA Comp Sci taught me one thing

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

    def isNonEmpty(self): #used for sorting and classifying
        return not (self.name == "Empty" or self.name == "")

    def isOrder(self): #im not an order.
        return False #might be sad bit its the easiest was to sort a list of orders tasks and expences
        #its bad i know