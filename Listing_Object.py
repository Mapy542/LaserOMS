from Bill_Of_Material_Object import BOM
import math

#costs are in cents for python int handling


class Listing:
    def __init__(self, name, product_cost, shipping_cost, base_price, revenue, materials_discription, materials_cost, worktime, machine_depreciation, packagin_cost, weight, hourly_wage, BOM ):
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


    def __str__(self):
        return f"{self.name} - {self.base_price}"

    def get_name(self):
        return self.name

    def get_product_cost(self):
        return self.product_cost

    def get_shipping_cost(self):
        return self.shipping_cost

    def get_base_price(self):
        return self.base_price

    def get_revenue(self):
        return self.revenue

    def get_materials_discription(self):
        return self.materials_discription

    def get_materials_cost(self):
        return self.materials_cost

    def get_worktime(self):
        return self.worktime

    def get_machine_depreciation(self):
        return self.machine_depreciation

    def get_packagin_cost(self):
        return self.packagin_cost

    def get_weight(self):
        return self.weight

    def get_hourly_wage(self):
        return self.hourly_wage

    def get_BOM(self):
        return self.BOM

    def set_name(self, name):
        self.name = name

    def set_product_cost(self, product_cost):
        self.product_cost = product_cost

    def set_shipping_cost(self, shipping_cost):
        self.shipping_cost = shipping_cost

    def set_base_price(self, base_price):
        self.base_price = base_price

    def set_revenue(self, revenue):
        self.revenue = revenue

    def set_materials_discription(self, materials_discription):
        self.materials_discription = materials_discription

    def set_materials_cost(self, materials_cost):
        self.materials_cost = materials_cost

    def set_worktime(self, worktime):
        self.worktime = worktime

    def set_machine_depreciation(self, machine_depreciation):
        self.machine_depreciation = machine_depreciation

    def set_packagin_cost(self, packagin_cost):
        self.packagin_cost = packagin_cost

    def set_weight(self, weight):
        self.weight = weight

    def set_hourly_wage(self, hourly_wage):
        self.hourly_wage = hourly_wage

    def set_BOM(self, BOM):
        self.BOM = BOM

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
