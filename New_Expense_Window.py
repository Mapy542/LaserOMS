import datetime
import os
import shutil

import tinydb
from guizero import PushButton, Text, TextBox, Window

import Common


def price_update():
    global ExpenseName, ItemQuantity, ItemPrice, TotalText
    TotalText.value = "Total: $" + str(
        Common.MonetaryMultiply(ItemQuantity.value, ItemPrice.value)
    )


def export(database):
    global ExpenseName, ItemQuantity, ItemPrice, TotalText, Description, Window2, DateField, ImageButton
    expenses = database.table("Expenses")  # Get expenses table

    ExpenseName.value = Common.CleanedFileName(
        ExpenseName.value
    )  # Clean up expense name

    # Check if expense name is already in database
    while len(expenses.search(tinydb.Query().expense_name == ExpenseName.value)) > 0:
        ExpenseName.value = (
            ExpenseName.value + "_Copy"
        )  # If it is, add _Copy to the end of the name
        # continue adding _Copy until the name is unique

    # Replace the / with a - to clean up the date
    DateField.value = DateField.value.replace("/", "-")
    expenses.insert(
        {
            "expense_name": ExpenseName.value,
            "expense_quantity": ItemQuantity.value,
            "expense_unit_price": ItemPrice.value,
            "expense_notes": Description.value,
            "expense_date": DateField.value,
            "expense_image_path": "",
            "process_status": "UTILIZE",
        }
    )
    # Add expense to database

    # copy image to
    if ImageButton.text != "":
        settings = database.table("Settings")
        ImageFolderPath = settings.search(
            (tinydb.Query().setting_name == "Images_Folder_Path")
            & (tinydb.Query().process_status == "UTILIZE")
        )[0]["setting_value"]
        FileEnding = os.path.splitext(ImageButton.text)

        # copy file to new path based on defined image folder path. file name is expense name. file type is preserved.
        shutil.copy(
            ImageButton.text,
            os.path.join(
                os.path.realpath(ImageFolderPath), ExpenseName.value + FileEnding[1]
            ),
        )

        expenses.update(
            {
                "expense_image_path": os.path.join(  # update image path in database
                    os.path.realpath(ImageFolderPath), ExpenseName.value + FileEnding[1]
                )
            },
            tinydb.Query().expense_name == ExpenseName.value,
        )

    Window2.destroy()  # Close window


def close():
    global ExpenseName, ItemQuantity, ItemPrice, TotalText, Description, Window2
    if (
        ExpenseName.value == ""
        and ItemQuantity.value == ""
        and ItemPrice.value == ""
        and Description.value == ""
    ):
        # If all fields are empty, close window
        Window2.destroy()
    else:
        # Ask user if they are sure they want to close
        result = Window2.yesno("Cancel", "Are you sure you want to Cancel?")
        if result == True:
            # If user is sure, close window
            Window2.destroy()


def AttachImage(window2):  # select image and show the path on the button
    global ImageButton
    path = window2.select_file(
        title="Select Image",
        folder=".",
        filetypes=[["All files", "*.*"]],
        save=False,
        filename="",
    )
    ImageButton.text = path


def RemoveImage():  # remove image and clear the button
    global ImageButton
    ImageButton.text = ""


def NewExpense(main_window, database):
    global ExpenseName, ItemQuantity, ItemPrice, TotalText, Description, DateField, ImageButton
    global Window2

    Window2 = Window(
        main_window, title="New Expense", layout="grid", width=600, height=600
    )  # Create window
    welcome_message = Text(
        Window2, text="Add Expense", size=18, font="Times New Roman", grid=[0, 0]
    )  # Create text

    NameText = Text(
        Window2, text="Item Name", size=15, font="Times New Roman", grid=[0, 1]
    )  # Create text
    ExpenseName = TextBox(Window2, width=30, grid=[1, 1], text="")  # Create textbox
    QuantityText = Text(
        Window2, text="Quantity", size=15, font="Times New Roman", grid=[0, 2]
    )  # Create text
    ItemQuantity = TextBox(
        Window2, grid=[1, 2], width=10, command=price_update, text="0"
    )  # Create textbox
    PriceText = Text(
        Window2, text="Price per Sub-Unit", size=15, font="Times New Roman", grid=[0, 3]
    )  # Create text
    ItemPrice = TextBox(
        Window2, grid=[1, 3], width=10, command=price_update, text="0"
    )  # Create textbox
    TotalText = Text(
        Window2, text="Total: $0", size=15, font="Times New Roman", grid=[0, 4]
    )  # Create text

    DescriptionText = Text(
        Window2, text="Additional Notes", size=15, font="Times New Roman", grid=[0, 10]
    )
    Description = TextBox(
        Window2, width=40, grid=[1, 10], text="", multiline=True, height=15
    )  # Create textbox

    ImageText = Text(
        Window2,
        text="Attach Verification Image",
        size=15,
        font="Times New Roman",
        grid=[0, 17],
    )
    ImageButton = PushButton(
        Window2, command=AttachImage, args=[Window2], text="", grid=[1, 17]
    )
    ImageCancelButton = PushButton(
        Window2, command=RemoveImage, text="Clear", grid=[2, 17]
    )

    DateText = Text(Window2, text="Date", size=15, font="Times New Roman", grid=[0, 18])
    DateField = TextBox(
        Window2,
        text=datetime.datetime.now().strftime("%m-%d-%Y"),
        width=15,
        grid=[1, 18],
    )  # Create textbox

    FinishButton = PushButton(
        Window2, command=export, text="Save", grid=[0, 19], args=[database]
    )  # Create button
    CancelButton = PushButton(
        Window2, command=close, text="Cancel", grid=[1, 19]
    )  # Create button
