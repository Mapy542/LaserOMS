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

#where all orders, listing data, and yearly expences are stored.
os.system("mkdir ../Orders")
os.system("mkdir ../Expences")
os.system("mkdir ../Listings")

#steup data for etsy api in this file
os.system("cp demooauth.txt ../oauth.txt")

#create default first order number and will be 123
os.system("cp default_order.txt ../Last_Order.txt")

#create item database file
os.system("cp blanktext.txt ../Products.txt")

#install tkinter the base for gui zero
#sudo may be required to install tkinter
print("Installing Tkinter with APT")
os.system("sudo apt install python3-tk")
