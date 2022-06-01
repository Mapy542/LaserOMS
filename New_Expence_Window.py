from guizero import Text, TextBox, PushButton, Window
from Expence_Object import Expence
import Order_Manipulator, Cache_Handler

def price_update():
    global item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, finish
    global realitems
    global window2


    realitems[0].changeName(item1.value)
    realitems[0].changeCost(int(item_price1.value) * 100)
    realitems[0].changeQuantity(item_quant1.value)
    
    realitems[1].changeName(item2.value)
    realitems[1].changeCost(int(item_price2.value) * 100)
    realitems[1].changeQuantity(item_quant2.value)

    realitems[2].changeName(item3.value)
    realitems[2].changeCost(int(item_price3.value) * 100)
    realitems[2].changeQuantity(item_quant3.value)

    realitems[3].changeName(item4.value)
    realitems[3].changeCost(int(item_price4.value) * 100)
    realitems[3].changeQuantity(item_quant4.value)

    realitems[4].changeName(item5.value)
    realitems[4].changeCost(int(item_price5.value) * 100)
    realitems[4].changeQuantity(item_quant5.value)

    totalmonet = 0
    for item in realitems:
        totalmonet += item.getTotalCost()
    total.value = "Total: $" + str(totalmonet/100)
    print(totalmonet)


def export():
    global item_price5, total, finish
    global realitems
    global window2

    price_update()
    new_items = []
    for item in realitems:
        if item.isNonEmpty():
            new_items.append(item)

    Order_Manipulator.BulkSaveExpences(new_items)
    for item in new_items:
        Cache_Handler.AddExpence(item)

    window2.destroy()

def NewExpense(main_window):
    global item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global realitems
    global window2
    realitems = []
    for i in range(0,5):
        realitems.append(Expence())
    window2 = Window(main_window, title="New Expence", layout="grid", width=1100,height=700)
    welcome_message = Text(window2,text='Generate New Order.', size=18, font="Times New Roman", grid=[1,0])

    items_message = Text(window2, text='Items,    Quantitiy,    Cost per Unit', size=12, font="Times New Roman", grid=[1,8])
    #items
    item1 = TextBox(window2, width=30,grid=[0,9],text='Empty')
    item_quant1 = TextBox(window2,grid=[1,9], width=10, command=price_update, text='0')
    item_price1 = TextBox(window2,grid=[2,9], width=10, command=price_update, text='0')

    item2 = TextBox(window2, width=30,grid=[0,10],text='Empty')
    item_quant2 = TextBox(window2,grid=[1,10], width=10, command=price_update, text='0')
    item_price2 = TextBox(window2,grid=[2,10], width=10, command=price_update, text='0')

    item3 = TextBox(window2, width=30,grid=[0,11],text='Empty')
    item_quant3 = TextBox(window2,grid=[1,11], width=10, command=price_update, text='0')
    item_price3 = TextBox(window2,grid=[2,11], width=10, command=price_update, text='0')

    item4 = TextBox(window2, width=30,grid=[0,12],text='Empty')
    item_quant4 = TextBox(window2,grid=[1,12], width=10, command=price_update, text='0')
    item_price4 = TextBox(window2,grid=[2,12], width=10, command=price_update, text='0')

    item5 = TextBox(window2, width=30,grid=[0,13],text='Empty')
    item_quant5 = TextBox(window2,grid=[1,13], width=10, command=price_update, text='0')
    item_price5 = TextBox(window2,grid=[2,13], width=10, command=price_update, text='0')

    #Total
    total = Text(window2,text='Total: $0', size=18, font="Times New Roman", grid=[2,19])

    finish = PushButton(window2,command=export,text='Save',grid=[0,19])
