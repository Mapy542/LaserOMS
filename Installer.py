import tinydb
import os

# Find and install all required Packages.
os.system("python3 -m pip install --upgrade pip")
f = open(os.path.join(os.path.realpath(os.path.dirname(__file__)), 'Packages.txt'), "r")
recs = f.read()
print(recs)
f.close()
packages = recs.split(',')
for i in range(len(packages)):
    os.system("pip install --upgrade " + str(packages[i]))

# wipe data?
answer = input("Would you like to wipe all databases? (y/n): ")
if answer == "y" or answer == "Y":
    DoubleCheck = input("Are you sure? (y/n): ")
    if DoubleCheck == "y" or DoubleCheck == "Y":
        doOverwrite = True


# check for existing files
dir = os.listdir("../")

if "OMS-Data.json" not in dir or doOverwrite:
    print("Creating Database file at \"../OMS-Data.json\"")
    f = open(os.path.join(os.path.realpath(os.path.dirname(__file__)),
        '../OMS-Data.json'), "w")
    f.write("{}")
    f.close()

# setup tables
if (doOverwrite):
    database = tinydb.TinyDB(os.path.join(os.path.realpath(os.path.dirname(__file__)),
        '../OMS-Data.json'))
    orders = database.table('Orders')  # Form orders table
    orders.insert({'order_ID': 111, 'order_name': 'LAST_ORDER',
                   'order_status': "IGNORE", 'process_status': "IGNORE"})
    order_items = database.table('Order_Items')  # Form order items table
    order_items.insert(
        {'order_ID': 111, 'item_UID': 'IGNORE', 'process_status': "IGNORE"})
    expenses = database.table('Expenses')  # Form expenses table
    expenses.insert({'expense_ID': 111, 'expense_name': 'LAST_EXPENSE',
                     'process_status': "IGNORE"})
    inventory = database.table('Products')  # Form inventory table
    inventory.insert({'product_name': 'Empty',
                     'product_base_price': 0, 'process_status': "UTILIZED"})
    # Form product pricing styles table
    prods = database.table('Product_Pricing_Styles')
    prods.insert({'style_name': 'Empty', 'process_status': "IGNORE"})
    tasks = database.table('Tasks')  # Form tasks table
    tasks.insert({'task_name': 'Empty', 'process_status': "IGNORE"})
    settings = database.table('Settings')  # Form settings table
    settings.insert({'setting_name': 'Empty',
                    'setting_value': 'Empty', 'process_status': "IGNORE"})
    database.close()

# make image folder
os.mkdir(os.path.join(os.path.realpath(os.path.dirname(__file__)),
        '../LaserOMS-Images'), mode=0o777)
