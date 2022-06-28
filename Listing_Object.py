from Bill_Of_Material_Object import BOM

#costs are in cents for python int handling


#todo:
#add aditional data necessary to manage API sync

class Listing:
    def __init__(self, name="", base_price = 0, revenue = 0, profit = 0, BOM = BOM(), otherpricestyles = []):
        self.name = name
        self.base_price = base_price
        self.revenue = revenue
        self.profit = profit
        self.BOM = BOM
        self.otherpricestyles = otherpricestyles


    def __str__(self):
        return f"{self.name} - {self.base_price}"

    def getName(self):
        return self.name

    def getBasePrice(self):
        return self.base_price

    def getRevenue(self):
        return self.revenue

    def getProfit(self):
        return self.profit

    def getBOM(self):
        return self.BOM

    def getOtherPriceStyles(self):
        return self.otherpricestyles

    def setName(self, name):
        self.name = name

    def setBasePrice(self, base_price):
        self.base_price = base_price

    def setRevenue(self, revenue):
        self.revenue = revenue

    def setProfit(self, profit):
        self.profit = profit
        
    def setBOM(self, BOM):
        self.BOM = BOM

    def setOtherPriceStyles(self, otherpricestyles):
        self.otherpricestyles = otherpricestyles
