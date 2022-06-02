class BOM:
    def __init__(self, name = "", items = [], overall_cost = 0):
        self.name = name
        self.items = items
        self.overall_cost = overall_cost
        
    def __str__(self):
        return f"{self.items}"

    def recalculate_overall_cost(self):
        self.overall_cost = 0
        for item in self.items:
            self.overall_cost += item[1]
        return self.overall_cost

    def add_item(self, itemname, itemcost):
        self.items.append(itemname, itemcost)
        self.overall_cost += itemcost

    def remove_item(self, itemname):
        for i in range(len(self.items)):
            if self.items[i][0] == itemname:
                self.overall_cost -= self.items[i][1]
                self.items.pop(i)
                break
    
    def getItems(self):
        return self.items

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name