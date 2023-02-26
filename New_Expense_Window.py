from guizero import Text, TextBox, PushButton, Window
import tinydb
import datetime


def price_update():
    global item1, item_quant1, item_price1, totaltext
    totaltext.value = 'Total: $' + \
        str(float(item_quant1.value) * float(item_price1.value))  # Update total


def export(database):
    global item1, item_quant1, item_price1, totaltext, discrption, window2, datefield
    expenses = database.table('Expenses')  # Get expenses table
    expenses.insert({'expense_name': item1.value, 'expense_quantity': item_quant1.value, 'expense_unit_price': item_price1.value,
                     'expense_total': float(item_quant1.value) * float(item_price1.value), 'expense_notes': discrption.value,
                     'expense_date': datefield, 'process_status': "UTILIZE"})
    # Add expense to database

    window2.destroy()  # Close window


def close():
    global item1, item_quant1, item_price1, totaltext, discrption, window2
    if (item1.value == '' and item_quant1.value == '0' and item_price1.value == '0' and discrption.value == ''):
        # If all fields are empty, close window
        window2.destroy()
    else:
        # Ask user if they are sure they want to cancel
        result = window2.yesno("Cancel", "Are you sure you want to cancel?")
        if result == True:
            # If user is sure, close window
            window2.destroy()


def NewExpense(main_window, database):
    global item1, item_quant1, item_price1, totaltext, discrption, datefield
    global window2

    window2 = Window(main_window, title="New Expense",
                     layout="grid", width=500, height=600)  # Create window
    welcome_message = Text(window2, text='Add Expense', size=18,
                           font="Times New Roman", grid=[0, 0])  # Create text

    nametext = Text(window2, text='Item Name', size=15,
                    font="Times New Roman", grid=[0, 1])  # Create text
    item1 = TextBox(window2, width=30, grid=[1, 1], text='')  # Create textbox
    quanttext = Text(window2, text='Quantity', size=15,
                     font="Times New Roman", grid=[0, 2])  # Create text
    item_quant1 = TextBox(
        window2, grid=[1, 2], width=10, command=price_update, text='0')  # Create textbox
    pricetext = Text(window2, text='Price per Sub-Unit', size=15,
                     font="Times New Roman", grid=[0, 3])  # Create text
    item_price1 = TextBox(
        window2, grid=[1, 3], width=10, command=price_update, text='0')  # Create textbox
    totaltext = Text(window2, text='Total: $0', size=15,
                     font="Times New Roman", grid=[0, 4])  # Create text

    discrptiontext = Text(window2, text='Additional Notes',
                          size=15, font="Times New Roman", grid=[0, 10])
    discrption = TextBox(window2, width=40, grid=[
                         1, 10], text='', multiline=True, height=15)  # Create textbox

    datetext = Text(window2, text='Date', size=15,
                    font="Times New Roman", grid=[0, 18])
    datefield = TextBox(window2, text=datetime.datetime.now().strftime(
        "%m-%d-%Y"), width=15, grid=[1, 18])  # Create textbox

    finish = PushButton(window2, command=export, text='Save', grid=[
                        0, 19], args=[database])  # Create button
    cancel = PushButton(window2, command=close, text='Cancel',
                        grid=[1, 19])  # Create button
