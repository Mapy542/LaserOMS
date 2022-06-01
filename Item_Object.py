class Item():
    def __init__(self, product = "Empty", baseprice = 0, profit = 0, wordpress_price = 0, etsy_price = 0, editboromarket_price = 0, quantity = 0, updatepricing = False):
        self.product = product
        self.baseprice = baseprice
        self.profit = profit
        self.wordpress_price = wordpress_price
        self.etsy_price = etsy_price
        self.quantity = quantity
        self.editboromarket_price = editboromarket_price
        if updatepricing:
            self.baseprice, self.profit, self.wordpress_price, self.etsy_price, self.editboromarket_price = self.makePrices()

    def __str__(self):
        return self.product + " $" + self.baseprice

    def makePrices(self):
        try:
            with open("../Items.txt", "r") as f:
                for line in f:
                    if line.startswith(self.product):
                        prices = line.split(',')
                        baseprice = prices[1]
                        profit = prices[2]
                        wordpress_price = prices[3]
                        etsy_price = prices[4]
                        editboromarket_price = prices[5]
                        f.close()
                        return int(baseprice), int(profit), int(wordpress_price), int(etsy_price), int(editboromarket_price)
        except OSError:
            print("Failed To Read Item File")
            return 0, 0, 0, 0, 0

    def getPrice(self, website):
        if website == "Base":
            return self.baseprice * self.quantity
        elif website == "Profit":
            return self.profit * self.quantity
        elif website == "Wordpress":
            return self.wordpress_price * self.quantity
        elif website == "Etsy":
            return self.etsy_price * self.quantity
        elif website == "EditBoroMarket":
            return int(self.editboromarket_price) * int(self.quantity)

    def getUnitPrice(self, website):
        if website == "Base":
            return self.baseprice
        elif website == "Profit":
            return self.profit
        elif website == "Wordpress":
            return self.wordpress_price
        elif website == "Etsy":
            return self.etsy_price
        elif website == "EditBoroMarket":
            return self.editboromarket_price

    def getProduct(self):
        return self.product

    def getBasePrice(self):
        return self.baseprice

    def getProfit(self):
        return self.profit

    def getQuantity(self):
        return self.quantity

    def changeQuantity(self, quantity):
        self.quantity = quantity

    def changeProduct(self, product):
        self.product = product
        self.baseprice, self.profit, self.wordpress_price, self.etsy_price, self.editboromarket_price = self.makePrices()

    #not used and python apparently doesn't like overridden methods like
    # def changeProduct(self, product, baseprice, profit, wordpress_price, etsy_price, editboromarket_price, quantity):
    #     self.product = product
    #     self.baseprice = baseprice
    #     self.profit = profit
    #     self.wordpress_price = wordpress_price
    #     self.etsy_price = etsy_price
    #     self.editboromarket_price = editboromarket_price
    #     self.quantity = quantity

    def export(self):
        data = ""
        data += "Item_Product|" + str(self.product) + "*"
        data += "Item_Base_Price|" + str(self.baseprice) + "*"
        data += "Item_Profit|" + str(self.profit) + "*"
        data += "Item_Wordpress_Price|" + str(self.wordpress_price) + "*"
        data += "Item_Etsy_Price|" + str(self.etsy_price) + "*"
        data += "Item_EditBoroMarket_Price|" + str(self.editboromarket_price) + "*"
        data += "Item_Quantity|" + str(self.quantity) + "*"
        return data

    def isNonEmpty(self):
        if self.product == "Empty" or self.quantity == 0:
            return False
        else:
            return True

    def isOrder(self):
        return False