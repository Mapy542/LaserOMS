import Order_Manipulator, os

#USED TO MIGRATE ORDERS FROM OLDER VERSION TO NEWER VERSION
#PRE GITHUB UPLOAD
#YOU WILL NOT NEED THIS

Order_Manipulator.MigrateOrders()#migrate orders

order_nums = os.popen('ls ../Orders').read()
order_nums = order_nums.split('\n')
order_nums = [i for i in order_nums if i]
for files in order_nums: #delete old files
    if files.endswith(".txt"):
        os.system("rm ../Orders/" + files)