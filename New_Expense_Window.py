from guizero import Text, TextBox, PushButton, Window
import tinydb
import datetime


def price_update():
    global Item1, ItemQuantity, ItemPrice, TotalText
    TotalText.value = 'Total: $' + \
        str(float(ItemQuantity.value) * float(ItemPrice.value))  # Update total


def export(database):
    global Item1, ItemQuantity, ItemPrice, TotalText, Description, Window2, DateField
    expenses = database.table('Expenses')  # Get expenses table
    expenses.insert({'expense_name': Item1.value, 'expense_quantity': ItemQuantity.value, 'expense_unit_price': ItemPrice.value,
                     'expense_total': float(ItemQuantity.value) * float(ItemPrice.value), 'expense_notes': Description.value,
                     'expense_date': DateField, 'process_status': "UTILIZE"})
    # Add expense to database

    Window2.destroy()  # Close window


def close():
    global Item1, ItemQuantity, ItemPrice, TotalText, Description, Window2
    if (Item1.value == '' and ItemQuantity.value == '0' and ItemPrice.value == '0' and Description.value == ''):
        # If all fields are empty, close window
        Window2.destroy()
    else:
        # Ask user if they are sure they want to close
        result = Window2.yesno("Cancel", "Are you sure you want to Cancel?")
        if result == True:
            # If user is sure, close window
            Window2.destroy()


def NewExpense(main_window, database):
    global Item1, ItemQuantity, ItemPrice, TotalText, Description, DateField
    global Window2

    Window2 = Window(main_window, title="New Expense",
                     layout="grid", width=500, height=600)  # Create window
    welcome_message = Text(Window2, text='Add Expense', size=18,
                           font="Times New Roman", grid=[0, 0])  # Create text

    NameText = Text(Window2, text='Item Name', size=15,
                    font="Times New Roman", grid=[0, 1])  # Create text
    Item1 = TextBox(Window2, width=30, grid=[1, 1], text='')  # Create textbox
    QuantityText = Text(Window2, text='Quantity', size=15,
                        font="Times New Roman", grid=[0, 2])  # Create text
    ItemQuantity = TextBox(
        Window2, grid=[1, 2], width=10, command=price_update, text='0')  # Create textbox
    PriceText = Text(Window2, text='Price per Sub-Unit', size=15,
                     font="Times New Roman", grid=[0, 3])  # Create text
    ItemPrice = TextBox(
        Window2, grid=[1, 3], width=10, command=price_update, text='0')  # Create textbox
    TotalText = Text(Window2, text='Total: $0', size=15,
                     font="Times New Roman", grid=[0, 4])  # Create text

    DescriptionText = Text(Window2, text='Additional Notes',
                           size=15, font="Times New Roman", grid=[0, 10])
    Description = TextBox(Window2, width=40, grid=[
        1, 10], text='', multiline=True, height=15)  # Create textbox

    DateText = Text(Window2, text='Date', size=15,
                    font="Times New Roman", grid=[0, 18])
    DateField = TextBox(Window2, text=datetime.datetime.now().strftime(
        "%m-%d-%Y"), width=15, grid=[1, 18])  # Create textbox

    FinishButton = PushButton(Window2, command=export, text='Save', grid=[
        0, 19], args=[database])  # Create button
    CancelButton = PushButton(Window2, command=close, text='Cancel',
                              grid=[1, 19])  # Create button
