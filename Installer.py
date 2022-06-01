import os

#Find and install all required Packages.
os.system("python3 -m pip install --upgrade pip")
f = open("Packages.txt", "r")
recs = f.read()
print(recs)
f.close()
packages = recs.split(',')
for i in range(len(packages)):
    os.system("pip install --upgrade " + str(packages[i]))

#where all orders are stored and yearly expences are stored.
os.system("mkdir ../Orders")
os.system("mkdir ../Expences")

#steup data for etsy api in this file
os.system("cp demooauth.txt ../oauth.txt")

#create default first order number and will be 123
os.system("cp default_order.txt ../Last_Order.txt")

#create default pricing list link from an empty file
os.system("cp blanktext.txt ../Pricing_List_Link.txt")

#install tkinter the base for gui zero
os.system("sudo apt install python3-tk")
