from Listing_Object import Listing

class Item():
    def __init__(self, product = "Empty", baseprice = 0, profit = 0, revenue = 0, otherpricingstyles = 0 , quantity = 0, listinginjection = None):
        self.product = product
        self.baseprice = baseprice
        self.profit = profit
        self.revenue = revenue
        self.otherpricestyles = otherpricingstyles
        self.quantity = quantity

        if listinginjection is not None:
            self.listinginjection = listinginjection
            self.product = listinginjection.getProduct()
            self.baseprice = listinginjection.getBasePrice()
            self.profit = listinginjection.getProfit()
            self.revenue = listinginjection.getRevenue()
            self.otherpricestyles = listinginjection.getOtherPriceStyles()

    def __str__(self):
        return self.product + "  $" + self.baseprice/100

    def getProduct(self):
        return self.product

    def getBasePrice(self):
        return self.baseprice

    def getProfit(self):
        return self.profit

    def getRevenue(self):
        return self.revenue

    def getOtherPriceStyles(self):
        return self.otherpricestyles

    def setProduct(self, product):
        self.product = product

    def setBasePrice(self, baseprice):
        self.baseprice = baseprice

    def setProfit(self, profit):
        self.profit = profit

    def setRevenue(self, revenue):
        self.revenue = revenue

    def setOtherPriceStyles(self, otherpricestyles):
        self.otherpricestyles = otherpricestyles

    def setQuantity(self, quantity):
        self.quantity = quantity

    def getQuantity(self):
        return self.quantity

    def setListingInjection(self, listinginjection):
        self.listinginjection = listinginjection
        self.product = listinginjection.getProduct()
        self.baseprice = listinginjection.getBasePrice()
        self.profit = listinginjection.getProfit()
        self.revenue = listinginjection.getRevenue()
        self.otherpricestyles = listinginjection.getOtherPriceStyles()


    def getListingInjection(self):
        return self.listinginjection

    def getPrice(self, price_style):
        if price_style == "Base":
            return self.baseprice
        elif price_style == "Profit":
            return self.profit
        elif price_style == "Revenue":
            return self.revenue
        elif price_style == "Other":
            for i in self.otherpricestyles:
                if i[0] == price_style:
                    return i[1]
        else:
            return 0

    def export(self):
        data = ""
        data += "Item_Product|" + str(self.product) + "*"
        data += "Item_Base_Price|" + str(self.baseprice) + "*"
        data += "Item_Profit|" + str(self.profit) + "*"
        data += "Item_Revenue|" + str(self.revenue) + "*"
        data += "Item_Quantity|" + str(self.quantity) + "*"
        for i in self.otherpricestyles:
            data += "Item_Other_Price_Style|" + str(i[0]) + "~" + str(i[1]) + "*"
        return data

    def isNonEmpty(self):
        if self.product == "Empty" or self.quantity == 0:
            return False
        else:
            return True

    def isOrder(self):
        return False