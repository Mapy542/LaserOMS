import os
from Item_Object import Item
from Order_Object import Order
from Expence_Object import Expence
from Task_Object import Task
from Listing_Object import Listing
from Bill_Of_Material_Object import BOM


def SaveOrder(order):
    '''
    This function saves the order to the orders folder under the order number.ord
    '''
    try:
        with open("../Orders/" + str(order.getOrderNumber()) + ".ord", "w") as f:
            f.write("Order_Number:" + str(order.getOrderNumber()) + ',')
            f.write("Order_Date:" + str(order.getOrderDate()) + ',')
            f.write("Order_Name:" + str(order.getOrderName()) + ',')
            line1, line2, city, state, zipcode = order.getOrderAddress()
            f.write("Order_Address_Line_1:" + str(line1) + ',')
            f.write("Order_Address_Line_2:" + str(line2) + ',')
            f.write("Order_City:" + str(city) + ',')
            f.write("Order_State:" + str(state) + ',')
            f.write("Order_Zip:" + str(zipcode) + ',')
            f.write("Order_Phone:" + str(order.getOrderPhone()) + ',')
            f.write("Order_Email:" + str(order.getOrderEmail()) + ',')
            f.write("Order_Total:" + str(order.getOrderTotal()) + ',')
            f.write("Order_Pricing_Style:" + str(order.getPricingStyle()) + ',')
            f.write("Order_Status:" + str(order.getOrderStatus()) + ',')
            items = order.getOrderItems()
            export = ""
            for item in items:
                export += str(item.export()) + ";"
            f.write("Order_Items:" + export)
            f.close()
            return True
    except OSError:
        print("Failed To Save Order")
        return False

def LoadOrder(ordernum):
    try:
        with open("../Orders/" + str(ordernum) + ".ord", "r") as f:
            order = f.read().split(',')
            f.close()
            for i in range(len(order)):
                order[i] = order[i].split(':')
                if order[i][0] == 'Order_Number':
                    order_number = order[i][1]
                if order[i][0] == 'Order_Date':
                    order_date = order[i][1]
                if order[i][0] == 'Order_Name':
                    order_name = order[i][1]
                if order[i][0] == 'Order_Address_Line_1':
                    order_address_line_1 = order[i][1]
                if order[i][0] == 'Order_Address_Line_2':
                    order_address_line_2 = order[i][1]
                if order[i][0] == 'Order_City':
                    order_city = order[i][1]
                if order[i][0] == 'Order_State':
                    order_state = order[i][1]
                if order[i][0] == 'Order_Zip':
                    order_zip = order[i][1]
                if order[i][0] == 'Order_Phone':
                    order_phone = order[i][1]
                if order[i][0] == 'Order_Email':
                    order_email = order[i][1]
                if order[i][0] == 'Order_Total':
                    order_total = order[i][1]
                if order[i][0] == 'Order_Pricing_Style':
                    order_pricing_style = order[i][1]
                if order[i][0] == 'Order_Status':
                    order_status = order[i][1]
                if order[i][0] == 'Order_Items':
                    order_items = order[i][1].split(';')
                    order_items = [i for i in order_items if i]

            if "order_items" in locals():
                items = []
                for item in order_items:
                    data = item.split("*")
                    for i in range(len(data)):
                        data[i] = data[i].split("|")
                        if data[i][0] == 'Item_Product':
                            item_product = data[i][1]
                        if data[i][0] == 'Item_Base_Price':
                            item_base_price = data[i][1]
                        if data[i][0] == 'Item_Profit':
                            item_profit = data[i][1]
                        if data[i][0] == 'Item_Wordpress_Price':
                            item_wordpress_price = data[i][1]
                        if data[i][0] == 'Item_Etsy_Price':
                            item_etsy_price = data[i][1]
                        if data[i][0] == 'Item_EditBoroMarket_Price':
                            item_editBoroMarket_price = data[i][1]
                        if data[i][0] == 'Item_Quantity':
                            item_quantity = data[i][1]
                    items.append(Item(item_product, int(item_base_price), int(item_profit), int(item_wordpress_price), int(item_etsy_price), int(item_editBoroMarket_price), int(item_quantity)))
                neworder = Order(order_number, order_date, order_name, order_address_line_1, order_address_line_2, order_city, order_state, order_zip,
                order_phone, order_email, items, order_total, order_pricing_style, order_status)

                return neworder
    except OSError:
        print("Failed To Load Order")

def DeleteOrder(ordernum):
    try:
        os.remove("../Orders/" + str(ordernum) + ".ord")
        return True
    except OSError:
        print("Failed To Delete Order")
        return False

def BulkSaveOrder(orders):
    for order in orders:
        SaveOrder(order)

def BulkLoadOrder(ordernums):
    orders = []
    print(ordernums)
    for orderdata in ordernums:
        orders.append(LoadOrder(orderdata))
    return orders

def BulkDeleteOrder(ordernums):
    for order in ordernums:
        DeleteOrder(order)

def SaveExpence(expence):
    try:
        with open("../Expences/" + str(expence.getDate().split("-")[2]) + ".exp", "a") as f:
            f.write("Expence_Date:" + str(expence.getDate()) + ',' + "Expence_Unit_Total:" + str(expence.getUnitCost()) + ','
             + "Expence_Quantity:" + str(expence.getQuantity()) + ',' + "Expence_Item:" + str(expence.getName()) + "," + "Expence_Category:" + str(expence.getCategory()) + ","
             + "Expence_Discription:" + str(expence.getDiscription()) + "\n")

            f.close()
            return True
    except OSError:
        print("Failed To Save Expence")
        return False

def LoadExpences(expenceyear):
    try:
        with open("../Expences/" + str(expenceyear) + ".exp", "r") as f:
            expences = f.read().split('\n')
            f.close()
            newexpences = []
            for i in range(len(expences)):
                expences[i] = expences[i].split(':')
                if expences[i][0] == 'Expence_Date':
                    expence_date = expences[i][1]
                if expences[i][0] == 'Expence_Unit_Total':
                    expence_unit_total = expences[i][1]
                if expences[i][0] == 'Expence_Quantity':
                    expence_quantity = expences[i][1]
                if expences[i][0] == 'Expence_Item':
                    expence_item = expences[i][1]
                if expences[i][0] == 'Expence_Category':
                    expence_category = expences[i][1]
                if expences[i][0] == 'Expence_Discription':
                    expence_discription = expences[i][1]
            newexpences.append(Expence(expence_item, expence_unit_total, expence_quantity, expence_date, expence_category, expence_discription))
            return newexpences
    except OSError:
        print("Failed To Load Expence")

def BulkSaveExpences(expences):
    for expence in expences:
        SaveExpence(expence)

def SaveTask(task):
    try:
        with open("../Tasks.tsk", "a") as f:
            f.write("Task_Name:" + str(task.getName()) + "," + "Task_Date:" + str(task.getDate()) + ',' + "Task_Priority:" + str(task.getPriority()) + ',' + "Task_Discription:" + str(task.getDiscription()) + "\n")
            f.close()
            return True
    except OSError:
        print("Failed To Save Task")
        return False

def LoadTasks():
    try:
        with open("../Tasks.tsk", "r") as f:
            tasks = f.read().split('\n')
            tasks = [i for i in tasks if i]
            f.close()
            newtasks = []
            for j in range(len(tasks)):
                tasks[j] = tasks[j].split(",")
                for i in range(len(tasks[j])):
                    tasks[j][i] = tasks[j][i].split(':')
                    if tasks[j][i][0] == 'Task_Name':
                        task_name = tasks[j][i][1]
                    if tasks[j][i][0] == 'Task_Date':
                        task_date = tasks[j][i][1]
                    if tasks[j][i][0] == 'Task_Priority':
                        task_priority = int(tasks[j][i][1])
                    if tasks[j][i][0] == 'Task_Discription':
                        task_discription = tasks[j][i][1]
                newtasks.append(Task(task_name, task_priority, task_date, task_discription))
            return newtasks
    except OSError:
        print("Failed To Load Task")

def BulkSaveTask(tasks):
    for task in tasks:
        SaveTask(task)

def DeleteTask(taskname):
    tasks = LoadTasks()
    for i in range(len(tasks)):
        if tasks[i].getName() == taskname:
            tasks.pop(i)
            break
    try:
        with open("../Tasks.tsk", "w") as f:
            f.truncate(0)
            f.seek(0)
            f.close()
    except OSError:
        print("Failed To Delete Task")
    BulkSaveTask(tasks)

def MigrateOrders():
    order_nums = os.popen('ls ../Orders').read()
    order_nums = order_nums.split('\n')
    order_nums = [i for i in order_nums if i]

    allorders = []
    for i in order_nums:
        if i.endswith(".txt"):
            print("Migrating Order: " + i)
            try:
                with open("../Orders/" + str(i), "r") as f:
                    orders = f.read().split(',')
                    f.close()
                    order_name = orders[0]
                    adress_line1 = orders[1]
                    city = orders[2]
                    state = orders[3]
                    zipcode = orders[4]
                    order_number = orders[5]
                    order_date = orders[6]
                    order_items = []
                    for j in range(int((len(orders)-8)/3)):
                        order_items.append(Item(product=orders[8+j*3],quantity=int(orders[9+j*3]),baseprice=int(orders[10+j*3])))
                    SaveOrder(Order(order_num = order_number, order_date = order_date, order_items= order_items,order_address=adress_line1, order_city=city, order_state=state, order_zip=zipcode, order_name=order_name, order_pricing_style="Base", order_status="Complete"))

            except OSError:
                print("Failed To Load Order")

def SaveBOM(bom):
    try:
        with open("../Listings/" + str(bom.getName()) + ".bom", "w") as f:
            f.write("BOM_Name:" + str(bom.getName()) + ",")
            items = bom.getItems()
            for singleitem in items:
                f.write("Item_Name:" + str(singleitem[0]) + "," + "Item_Cost:" + str(singleitem[1]) + ",")
            f.close()
            return True
    except OSError:
        print("Failed To Save BOM")
        return False

def LoadBOM(bomname):
    try:
        with open("../Listings/" + str(bomname) + ".bom", "r") as f:
            bom = f.read().split(',')
            f.close()
            itemnames = []
            itemcosts = []
            for i in range(len(bom)):
                bom[i] = bom[i].split(':')
                if bom[i][0] == 'BOM_Name':
                    bom_name = bom[i][1]
                if bom[i][0] == 'Item_Name':
                    itemnames.append(bom[i][1])
                if bom[i][0] == 'Item_Cost':
                    itemcosts.append(int(bom[i][1]))
            items = []
            for i in range(len(itemnames)):
                items.append([itemnames[i],itemcosts[i]])
            newbom = BOM(name = bom_name, items = items)
            newbom.recalculate_overall_cost()
            return newbom
    except OSError:
        print("Failed To Load BOM")
        

