import os, Order_Cache_Handler, Order_Manipulator
from guizero import Window, Text, TextBox, CheckBox, Combo, PushButton, ListBox
from datetime import datetime
from Bill_Of_Material_Object import BOM
from Listing_Object import Listing

def getListings():
    files = os.popen('ls ../Listings').read()
    files = files.split('\n')
    files = [i for i in files if i]
    files = [i for i in files if i.endswith('.lst')]
    return files



def update_listbox():
    
def ListingDisplay(main_window):
    global listbox, new_expence, pricing_button, rebuild
    global window2
    window2 = Window(main_window, title="Listings", layout="grid", width=1100,height=700)

    welcome_message = Text(window2, text="Listing Data" , size=15, font="Times New Roman",grid=[0,0,4,1])
    listbox = ListBox(window2, items=[],multiselect=True,width=1000,height=500,scrollbar=True,grid=[0,1,4,5])

    update_listbox()

    #options
    new_expence = PushButton(window2,text='Create New Expence',command=,grid=[0,7,1,1])

    rebuild = PushButton(window2,text='Rebuild Statistics',command=update_listbox,grid=[1,8,1,1])
    pricing_button = PushButton(window2,text='Update Pricing',command=,grid=[0,8,1,1])


    window2.display()
