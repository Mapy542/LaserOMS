import New_Order_Window
import Google_Sheets_Sync
from guizero import Window, Text, PushButton, ListBox
import tinydb


def UpdateListbox(InfoBox, database):
    ProductsTable = database.table('Products')
    InfoBox.clear()
    products = ProductsTable.search(
        tinydb.where('process_status') == 'UTILIZE')
    for product in products:
        MaxKeyLength = 0
        keys = list(product)
        values = list(product.values())
        for i in range(len(keys)):
            if len(keys[i]) > MaxKeyLength:
                MaxKeyLength = len(keys[i])

        for i in range(len(keys)):
            if keys[i] == 'product_name':
                InfoBox.append(values[i])
            else:
                InfoBox.append(
                    '    ' + keys[i] + ':'+' '*(MaxKeyLength-len(keys[i])) + values[i])
        InfoBox.append('')


def NewOrder(main_window, database):
    New_Order_Window.NewOrder(main_window, database)


def SyncGoogleSheet(main_window, database):
    Google_Sheets_Sync.RebuildProductsFromSheets(main_window, database)


def ListingDisplay(main_window, database):
    global InfoBox
    global window2
    window2 = Window(main_window, title="Listings",
                     layout="grid", width=1100, height=700)

    WelcomeMessage = Text(window2, text="Listing Data",
                          size=15, font="Times New Roman", grid=[0, 0, 4, 1])
    InfoBox = ListBox(window2, items=[], multiselect=True,
                      width=1000, height=500, scrollbar=True, grid=[0, 1, 4, 5])
    InfoBox.font = 'Courier'

    UpdateListbox(InfoBox, database)

    # options
    RebuildButton = PushButton(window2, text='Reload', command=UpdateListbox, grid=[
        0, 7, 1, 1], args=[InfoBox, database])

    NewOrderButton = PushButton(window2, text='Create New Order', command=NewOrder, grid=[
        1, 8, 1, 1], args=[main_window, database])
    UpdatePricingButton = PushButton(window2, text='Update Pricing', command=SyncGoogleSheet, grid=[
        0, 8, 1, 1], args=[main_window, database])
