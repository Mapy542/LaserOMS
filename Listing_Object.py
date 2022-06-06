from Bill_Of_Material_Object import BOM
import math, Pricing_Styles_Handler

#costs are in cents for python int handling
#weight is in lbs. go merica

#MACROS TODO
# [M] = insert foot board price of maple
# use operations in cost
#example: [M]*.6+[BW]*.2 + 3  //  .6 board feet of maple plus .2 board feet of walnut plus 3 addditional cost

class Listing:
    def __init__(self, name="", product_cost = 0, shipping_cost = 0, base_price = 0, revenue = 0, materials_discription = "", materials_cost = "", worktime = 0, machine_depreciation = 0, packagin_cost = 0, weight = 0, hourly_wage = 0, BOM = BOM(), otherpricestyles = []):
        self.name = name
        self.product_cost = product_cost
        self.shipping_cost = shipping_cost
        self.base_price = base_price
        self.revenue = revenue
        self.materials_discription = materials_discription
        self.materials_cost = materials_cost
        self.worktime = worktime
        self.machine_depreciation = machine_depreciation
        self.packagin_cost = packagin_cost
        self.weight = weight
        self.hourly_wage = hourly_wage
        self.BOM = BOM
        self.otherpricestyles = otherpricestyles


    def __str__(self):
        return f"{self.name} - {self.base_price}"

    def getName(self):
        return self.name

    def getProductCost(self):
        return self.product_cost

    def getShippingCost(self):
        return self.shipping_cost

    def getBasePrice(self):
        return self.base_price

    def getRevenue(self):
        return self.revenue

    def getMaterialsDiscription(self):
        return self.materials_discription

    def getMaterialsCost(self):
        return self.materials_cost

    def getWorktime(self):
        return self.worktime

    def getMachineDepreciation(self):
        return self.machine_depreciation

    def getPackagingCost(self):
        return self.packagin_cost

    def getWeight(self):
        return self.weight

    def getHourlyWage(self):
        return self.hourly_wage

    def getBOM(self):
        return self.BOM

    def setName(self, name):
        self.name = name

    def setMaterialsDiscription(self, materials_discription):
        self.materials_discription = materials_discription

    def setMaterialsCost(self, materials_cost):
        self.materials_cost = materials_cost

    def setWorktime(self, worktime):
        self.worktime = worktime

    def setMachineDepreciation(self, machine_depreciation):
        self.machine_depreciation = machine_depreciation

    def setPackagingCost(self, packagin_cost):
        self.packagin_cost = packagin_cost

    def setWeight(self, weight):
        self.weight = weight

    def setHourlyWage(self, hourly_wage):
        self.hourly_wage = hourly_wage

    def setBOM(self, BOM):
        self.BOM = BOM

    def getOtherPriceStyles(self):
        return self.otherpricestyles

    def recalculateOtherPriceStyles(self):
        self.otherpricestyles = Pricing_Styles_Handler.Recalculate(self.base_price)
        return self.otherpricestyles

    def recalculateProductCost(self):
        self.product_cost = self.machine_depreciation + self.materials_cost + self.worktime * self.hourly_wage
        return self.product_cost

    def recalculateShippingCost(self): #aproximates shipping cost from weight based on USPS prices
        self.shipping_cost = self.weight  * 2 + 700 + self.packagin_cost
        return self.shipping_cost

    def recalculateBasePrice(self):
        self.base_price = math.ceil( self.product_cost / 100 * 1.2 ) * 100
        return self.base_price

    def recalculateRevenue(self):
        self.revenue = self.base_price - self.product_cost - self.shipping_cost
        return self.revenue

    def recalculateAllCosts(self):
        self.recalculateProductCost()
        self.recalculateShippingCost()
        self.recalculateBasePrice()
        self.recalculateRevenue()
        self.recalculateOtherPriceStyles()
        return self.product_cost, self.shipping_cost, self.base_price, self.revenue