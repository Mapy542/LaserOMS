import datetime
import os
import shutil

import PyPDF2
import tinydb
from guizero import CheckBox, PushButton, Text, TextBox, Window

import Common


def price_update():
    global ExpenseName, ItemQuantity, ItemPrice, TotalText
    TotalText.value = "Total: $" + str(
        Common.MonetaryMultiply(ItemQuantity.value, ItemPrice.value)
    )  # Update total


def export(database):
    global ExpenseName, ItemQuantity, ItemPrice, TotalText, Description, Window2, DateField, ImageButton, deleteImg
    expenses = database.table("Expenses")  # Get expenses table

    ExpenseName.value = Common.CleanedFileName(ExpenseName.value)  # Clean up expense name

    imgPath = ""  # define in scope for image path, if no image is attached, it will be blank

    # copy image to
    if ImageButton.text != "":
        settings = database.table("Settings")
        ImageFolderPath = settings.search(
            (tinydb.Query().setting_name == "Images_Folder_Path")
            & (tinydb.Query().process_status == "UTILIZE")
        )[0]["setting_value"]
        FileEnding = os.path.splitext(ImageButton.text)

        # copy file to new path based on defined image folder path. file name is expense name. file type is preserved.
        try:
            shutil.copy(
                ImageButton.text,
                os.path.join(os.path.realpath(ImageFolderPath), ExpenseName.value + FileEnding[1]),
            )
        except:
            Window2.warning("Error", "Image could not be saved.")
            return

        if deleteImg.value == True:  # delete original image if checkbox is checked
            try:
                os.remove(ImageButton.text)
            except:
                Window2.warning(
                    "Error",
                    "Original image could not be deleted. Expense was still saved successfully.",
                )

        imgPath = os.path.join(  # mark the image path for the database
            os.path.realpath(ImageFolderPath), ExpenseName.value + FileEnding[1]
        )

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
            "expense_image_path": imgPath,
            "process_status": "UTILIZE",
        }
    )
    # Add expense to database

    Window2.destroy()  # Close window


def close():
    global ExpenseName, ItemQuantity, ItemPrice, TotalText, Description, Window2
    if ExpenseName.value == "" and Description.value == "":
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


def ImportAmazonExpense(main_window, database):
    global ExpenseName, ItemQuantity, ItemPrice, TotalText, Description, DateField, ImageButton, deleteImg
    global Window2

    Window2 = Window(
        main_window, title="New Expense", layout="grid", width=800, height=600
    )  # Create window

    # get the path of the pdf file from the user
    PDFPath = Window2.select_file(
        title="Select Invoice PDF",
        folder=".",
        filetypes=[["PDF files", "*.pdf"]],
        save=False,
        filename="",
    )
    if PDFPath == "":  # if the user cancels, close the window
        Window2.destroy()
        return

    # get the date from the pdf file
    try:
        PDFReader = PyPDF2.PdfReader(PDFPath)
        PDFText = ""
        for page in range(len(PDFReader.pages)):
            PDFText += PDFReader.pages[page].extract_text()

        Cost = PDFText.split("Order Total: $")[1].split("\n")[0]
        AmazonOrderNumber = PDFText.split("Amazon.com order number:  ")[1].split("\n")[0]

    except Exception as e:
        print("Exception: ", e)
        Window2.warn("Error", "Error reading PDF file. Please try again.")
        Window2.destroy()
        return

    welcome_message = Text(
        Window2, text="Add Expense", size=18, font="Times New Roman", grid=[0, 0]
    )  # Create text

    NameText = Text(
        Window2, text="Item Name", size=15, font="Times New Roman", grid=[0, 1]
    )  # Create text
    ExpenseName = TextBox(
        Window2, width=30, grid=[1, 1], text="Amazon Order: " + AmazonOrderNumber
    )  # Create textbox
    QuantityText = Text(
        Window2, text="Quantity", size=15, font="Times New Roman", grid=[0, 2]
    )  # Create text
    ItemQuantity = TextBox(
        Window2, grid=[1, 2], width=10, command=price_update, text="1"
    )  # Create textbox
    PriceText = Text(
        Window2, text="Price per Sub-Unit", size=15, font="Times New Roman", grid=[0, 3]
    )  # Create text
    ItemPrice = TextBox(
        Window2, grid=[1, 3], width=10, command=price_update, text=Cost
    )  # Create textbox
    TotalText = Text(
        Window2, text="Total: $0", size=15, font="Times New Roman", grid=[0, 4]
    )  # Create text
    price_update()  # Update total text

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
        Window2, command=AttachImage, args=[Window2], text=PDFPath, grid=[1, 17]
    )
    ImageCancelButton = PushButton(Window2, command=RemoveImage, text="Clear", grid=[2, 17])

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
    CancelButton = PushButton(Window2, command=close, text="Cancel", grid=[1, 19])  # Create button

    deleteImg = CheckBox(Window2, text="Delete Img after Save", grid=[0, 20])
