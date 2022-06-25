from Item_Object import Item
from Order_Object import Order
import Order_Manipulator, os

def AllRebuildCache():
    # This function will rebuild all cache files. TIME INTENSIVE FOR LARGE ORDER COUNT. RECOMENDED TO RUN ON SERVER
    RebuildExpenceCache()
    RebuildOrderCaches()

def RebuildOrderCaches():
    order_nums = os.popen('ls ../Orders').read()
    order_nums = order_nums.split('\n')
    order_nums = [i for i in order_nums if i]

    allorders = []
    for i in order_nums:
        if i.endswith(".ord"):
            allorders.append(Order_Manipulator.GetOrder(i.split(".")[0]))

    openorders = []
    years = []
    for i in allorders:
        if i.getStatus() == "Open":
            openorders.append(i.getOrderNumber())
        if i.getDate().split("-")[0] not in years:
            years.append(i.getDate().split("-")[0])
        years[i.getDate().split("-")[0]].append(i.getOrderNumber())
    try:
        with open("Open_Orders.txt", "w+") as f:
            f.write(",".join(openorders))
            f.close()
    except OSError:
        print("Failed To Rebuild Open Orders")

    try:
        for i in years:
            with open("../" + str(i) + "_Orders.txt", "w+") as f:
                f.write(",".join(years[i]))
                f.close()
    except OSError:
        print("Failed To Rebuild Year Orders")

def RebuildExpenceCache():
    # This function will rebuild the expence cache.
    pass

def AddOpenOrder(order):
    # This function will add an order to the open order cache.
    try:
        with open("../Open_Orders.txt", "w+") as f:
            orders = f.read().strip().split(",")
            orders = [i for i in orders if i]
            orders.append(str(order.getOrderNumber()))
            f.write(",".join(orders))
            f.close()
            return True
    except OSError:
        print("Failed To Add Open Order")
        return False

def RemoveOpenOrder(ordernumber):
    # This function will remove an order from the open order cache.
    open_orders = Order_Manipulator.BulkLoadOrder(GetOpenOrders())
    try:
        with open("../Open_Orders.txt", "w") as f:
            f.truncate(0)
            f.seek(0)
            f.close()
    except OSError:
        print("Failed To Remove Open Order")
    for order in open_orders:
        if order.getOrderNumber() != ordernumber:
            AddOpenOrder(order)

def GetOpenOrders():
    # This function will return a list of all open orders.
    try:
        with open("../Open_Orders.txt", "r") as f:
            orders = f.read().strip().split(',')
            orders = [i for i in orders if i]
            f.close()
            return orders
    except OSError:
        print("Failed To Get Open Orders")
        return []

def AddYearOrder(order):
    # This function will add an order to the year order cache.
    year = order.getOrderDate().split("-")[0]
    try:
        with open("../" + str(year) + "_Orders.txt", "w+") as f:
            orders = f.read().split(',')
            orders = [i for i in orders if i]
            orders.append(str(order.getOrderNumber()))
            f.write(",".join(orders))
            f.close()
            return True
    except OSError:
        print("Failed To Add Year Order")
        return False

def RemoveYearOrder(ordernumber):
    # This function will remove an order from the year order cache.
    order = Order_Manipulator(ordernumber)
    year = order.getDate().split("-")[0]
    try:
        with open("../" + str(year) + "_Orders.txt", "w+") as f:
            orders = f.read().split(',')
            orders = [i for i in orders if i]
            orders.remove(str(ordernumber))
            f.write(",".join(orders))
            f.close()
            return True
    except OSError:
        print("Failed To Remove Year Order")
        return False

def GetYearOrders(year):
    # This function will return a list of all orders for a specific year.
    try:
        with open("../" + str(year) + "_Orders.txt", "r") as f:
            orders = f.read().split(',')
            orders = [i for i in orders if i]
            f.close()
            return orders
    except OSError:
        print("Failed To Get Year Orders")
        return []

def GetAllOrders():
    order_nums = os.popen('ls ../Orders').read()
    order_nums = order_nums.split('\n')
    order_nums = [i for i in order_nums if i]
    justnums = []
    for i in order_nums:
        if i.endswith(".ord"):
            justnums.append(i.split(".")[0])
    return justnums

def AddExpence(expence):
    # This function will add an expence to the expence cache.
    try:
        with open("../Finances.txt", "w+") as f:
            data = f.read().split('\n')
            data = [i for i in data if i]
            for i in range(len(data)):
                data[i] = data[i].split(':')
                for j in range(len(data[i])):
                    if(data[i][j] == "Total_Cost"):
                        data[i][j+1] = str(int(data[i][j+1]) + expence.getCost())
                    if(data[i][j] == expence.getDate().split("-")[2] + "_Total_Cost"):
                        data[i][j+1] = str(int(data[i][j+1]) + expence.getCost())

            f.write("\n".join([" : ".join(i) for i in data]))
            f.close()
            return True
    except OSError:
        print("Failed To Add Expence")
        return False

def AddRevenueOrder(order):
    # This function will add an order to the revenue order cache.
    try:
        with open("../Finances.txt", "w+") as f:
            data = f.read().split('\n')
            data = [i for i in data if i]
            for i in range(len(data)):
                data[i] = data[i].split(':')
                for j in range(len(data[i])):
                    if(data[i][j] == "Total_Revenue"):
                        data[i][j+1] = str(int(data[i][j+1]) + order.getTotal())
                    if(data[i][j] == "Total_Orders"):
                        data[i][j+1] = str(int(data[i][j+1]) + 1)
                    if(data[i][j] == order.getDate().split("-")[2] + "_Total_Revenue"):
                        data[i][j+1] = str(int(data[i][j+1]) + order.getTotal())
                    if(data[i][j] == order.getDate().split("-")[2] + "_Total_Orders"):
                        data[i][j+1] = str(int(data[i][j+1]) + 1)

            f.write("\n".join([" : ".join(i) for i in data]))
            f.close()
            return True
    except OSError:
        print("Failed To Add Revenue Order")
        return False

def getFinanceCache():
    # This function will return the finance cache.
    try:
        with open("../Finances.txt", "r") as f:
            data = f.read().split('\n')
            data = [i for i in data if i]
            f.close()
            return data
    except OSError:
        print("Failed To Get Finance Cache")
        return []