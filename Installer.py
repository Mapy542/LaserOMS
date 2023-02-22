import tinydb
import os

# Find and install all required Packages.
os.system("python3 -m pip install --upgrade pip")
f = open("Packages.txt", "r")
recs = f.read()
print(recs)
f.close()
packages = recs.split(',')
for i in range(len(packages)):
    os.system("pip install --upgrade " + str(packages[i]))

# install tkinter the base for gui zero
# sudo may be required to install tkinter
print("Installing Tkinter with APT")
os.system("sudo apt install python3-tk")

# wipe data?
answer = input("Would you like to wipe all databases? (y/n): ")
if answer == "y" or answer == "Y":
    doublecheck = input("Are you sure? (y/n): ")
    if doublecheck == "y" or doublecheck == "Y":
        doOverwrite = True


# check for existing files
dir = os.listdir("../")

if "Orders.json" not in dir or doOverwrite:
    print("Creating Database file at \"../OMS-Data.json\"")
    f = open("../OMS-Data.json", "w")
    f.write("{}")
    f.close()

# setup tables
if (doOverwrite):
    database = tinydb.TinyDB('../OMS-Data.json')
    orders = database.table('Orders')  # Form orders table
    orders.insert({'order_ID': 111, 'order_name': 'LAST_ORDER',
                   'order_status': "IGNORE", 'Process_Status': "IGNORE"})
    order_items = database.table('Order_Items')  # Form order items table
    order_items.insert({'order_ID': 111, 'item_UID': 'IGNORE',
                        'item_quantity': 0, 'item_price': 0.00, 'Process_Status': "IGNORE"})
    expences = database.table('Expenses')  # Form expences table
    expences.insert({'expence_ID': 111, 'expence_name': 'LAST_EXPENCE',
                     'Process_Status': "IGNORE"})
    inventory = database.table('Products')  # Form inventory table
    inventory.insert({'product_name': 'Empty',
                     'product_base_price': 0, 'Process_Status': "UTILIZED"})
    # Form product pricing styles table
    prods = database.table('Product_Pricing_Styles')
    prods.insert({'style_name': 'Empty', 'Process_Status': "IGNORE"})
    taks = database.table('Tasks')  # Form tasks table
    taks.insert({'task_name': 'Empty', 'Process_Status': "IGNORE"})
    database.close()
