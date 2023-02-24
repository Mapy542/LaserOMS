from guizero import Text, TextBox, PushButton, Window, yesno
import tinydb

def price_update():
    global item1,item_quant1, item_price1,totaltext
    totaltext.value = 'Total: $' + str(float(item_quant1.value) * float(item_price1.value))


def export(database):
    global item1,item_quant1, item_price1,totaltext,discrption, window2
    expenses = database.table('Expenses')
    expenses.insert({'expense_name': item1.value, 'expense_quantity': item_quant1.value, 'expense_unit_price': item_price1.value, 'expense_total': float(item_quant1.value) * float(item_price1.value), 'expense_notes': discrption.value, 'process_status': "UTILIZE"})


    window2.destroy()

def close():
    global item1,item_quant1, item_price1,totaltext,discrption, window2
    if (item1.value == '' and item_quant1.value == '0' and item_price1.value == '0' and discrption.value == ''):
        window2.destroy()
    else:
        result = yesno("Cancel", "Are you sure you want to cancel?")
        if result == True:
            window2.destroy()

def NewExpense(main_window, database):
    global item1,item_quant1, item_price1,totaltext,discrption
    global window2

    window2 = Window(main_window, title="New Expense", layout="grid", width=1100,height=700)
    welcome_message = Text(window2,text='Add Expense', size=18, font="Times New Roman", grid=[1,0])

    #items
    nametext = Text(window2,text='Item Name', size=15, font="Times New Roman", grid=[0,1])
    item1 = TextBox(window2, width=30,grid=[1,1],text='')
    quanttext = Text(window2,text='Quantity', size=15, font="Times New Roman", grid=[0,2])
    item_quant1 = TextBox(window2,grid=[1,2], width=10, command=price_update, text='0')
    pricetext = Text(window2,text='Price per Sub-Unit', size=15, font="Times New Roman", grid=[0,3])
    item_price1 = TextBox(window2,grid=[1,3], width=10, command=price_update, text='0')
    totaltext = Text(window2,text='Total: $0', size=15, font="Times New Roman", grid=[0,4])

    discrptiontext = Text(window2, text='Additional Notes', size=15, font="Times New Roman", grid=[0,10])
    discrption = TextBox(window2, width=40,grid=[1,10],text='', multiline=True, height=15)
    #Total


    finish = PushButton(window2,command=export,text='Save',grid=[0,19], args=[database])
    cancel = PushButton(window2,command=close,text='Cancel',grid=[1,19])
