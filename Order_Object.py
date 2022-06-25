from Item_Object import Item
from datetime import datetime

class Order(): #an object to hold order data
    def __init__(self, order_num = 0, order_date = datetime.today().strftime('%m-%d-%Y'), order_name = "", order_address = "", order_address_line_2 = "",
     order_city = "", order_state = "", order_zip = "", order_phone = "", order_email = "", 
     order_items = [], order_total = 0, order_pricing_style = "Base", order_status = ""):
        self.order_num = order_num #order id number
        self.order_date = order_date #createtion date
        self.order_name = order_name #purchaser name
        self.order_address = order_address #adress line 1
        self.order_address_line_2 = order_address_line_2 #line2
        self.order_city = order_city
        self.order_state = order_state
        self.order_zip = order_zip
        self.order_phone = order_phone
        self.order_email = order_email
        self.order_items = order_items #list of items sold (item objects)
        self.order_total = order_total # total price
        self.order_pricing_style = order_pricing_style #pricing style for reference
        self.order_status = order_status #status [open, fufiled] or whatever

    #Accessors

    def getOrderNumber(self):
        return self.order_num

    def getOrderDate(self):
        return self.order_date

    def getOrderName(self):
        return self.order_name

    def getOrderAddress(self):
        return self.order_address, self.order_address_line_2, self.order_city, self.order_state, self.order_zip

    def getOrderPhone(self):
        return self.order_phone
    
    def getOrderEmail(self):
        return self.order_email
    
    def getOrderItems(self):
        return self.order_items

    def getOrderTotal(self):
        self.calculateTotal()
        return self.order_total

    def getPricingStyle(self):
        return self.order_pricing_style

    def getOrderStatus(self):
        return self.order_status

    def changeOrderStatus(self, order_status):
        self.order_status = order_status

    def changeOrderPricingStyle(self, order_pricing_style):
        self.order_pricing_style = order_pricing_style
        self.calculateTotal()

    def addItem(self, item):
        self.order_items.append(item)
        self.calculateTotal()

    def setOrderItems(self, items):
        self.order_items = items
        self.calculateTotal()

    def setOrderEmail(self, order_email):
        self.order_email = order_email

    def setOrderPhone(self, order_phone):
        self.order_phone = order_phone

    #adress is handled by one function
    def setOrderAddress(self, order_address, order_address_line_2, order_city, order_state, order_zip):
        self.order_address = order_address
        self.order_address_line_2 = order_address_line_2
        self.order_city = order_city
        self.order_state = order_state
        self.order_zip = order_zip

    def setOrderName(self, order_name):
        self.order_name = order_name

    def setOrderDate(self, order_date):
        self.order_date = order_date

    def setOrderNumber(self, order_num):
        self.order_num = order_num

    def calculateTotal(self): #calculate total from each item
        total = 0
        for item in self.order_items:
            total += item.getPrice(self.order_pricing_style)
        self.order_total = total

    def isOrder(self): #used for sorting
        return True

