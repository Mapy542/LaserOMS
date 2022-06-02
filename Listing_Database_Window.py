import os, Cache_Handler, Order_Manipulator
from guizero import Window, Text, TextBox, CheckBox, Combo, PushButton, ListBox
from datetime import datetime
from Bill_Of_Material_Object import BOM
from Listing_Object import Listing

def update_listbox():
    data = Cache_Handler().getFinanceCache()
    yeardata = []
    for row in data:
        splice = row.split(',')
        if splice[0] == "Total_Revenue":
            total_revenue = splice[1]
        elif splice[0] == "Total_Orders":
            total_orders = splice[1]
        elif splice[0] == "Total_Cost":
            total_expences = splice[1]
        elif(splice[0].isdigit()):
            yeardata.append(splice)
    #place each item on yeardata in an array based on year
    yeardata_array = []
    for data in yeardata:
        if not data[0].split("_")[0] in yeardata_array:
            yeardata_array.append(data[0].split("_")[0], [])
        if data[0].split("_")[1] in yeardata_array:
            yeardata_array[yeardata_array.index(data[0].split("_")[0])][len(yeardata_array[yeardata_array.index(data[0].split("_")[0])])] = data 

    #sort yeardata by numeric order of yeardata[]
    yeardata.sort(key=lambda x: int(x[0]))

    #update listbox
    listbox.clear()
    listbox.append('Total Orders Ever: '+ str(total_orders))
    listbox.append('Total Orders Income Ever: ' + str(int(total_revenue)/100))
    listbox.append('Total Expenditure Ever: ' + str(int(total_expences)/100))
    for i in range(len(yeardata)):
        listbox.append(yeardata_array[i][0] + ":")
        listbox.append('    Total Orders: ' + str(yeardata_array[i][1][1]))
        listbox.append('    Total Income: ' + str(yeardata_array[i][2][1]/100))
        listbox.append('    Total Expenditure: ' + str(yeardata_array[i][3][1]/100))
        listbox.append('    ROI Ratio: ' + str(yeardata_array[i][2][1]/100/yeardata_array[i][3][1]/100))

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
