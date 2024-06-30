import copy
import os
import platform
import subprocess
import traceback

import tinydb
from PIL import Image, ImageDraw, ImageFont

import Common


def TextWrap(text, rowLength):
    """Wraps text to fit within a given row length. Also hydrates escape sequences if allowed.

    Args:
        text (Str): The text to wrap.
        rowLength (Int): The maximum length of each row.

    Returns:
        Str: The wrapped text.
    """

    wrappedText = copy.copy(text)  # copy text to avoid modifying original as it will be pull apart

    i = 0  # index of the current character
    length = 0  # length of the current line
    while i < len(wrappedText):
        if wrappedText[i] == "\n":  # if a newline is found, reset the length
            length = 0
        else:
            length += 1

        if length >= rowLength:  # if the length is greater than the row length
            # find the last space before the row length
            for j in range(
                i, i - rowLength, -1
            ):  # search backwards from the current character to the row length
                if (
                    wrappedText[j] == " "
                ):  # if a space is found, break the loop and wrap the text at that space
                    wrappedText = wrappedText[:j] + "\n" + wrappedText[j + 1 :]
                    break
            length = 0

        i += 1

    return wrappedText


def PrintPackingSlip(app, database, OrderNumber):
    """Prints a packing slip for the given order number.

    Args:
        app (GuiZero Window): The main window of the program.
        database (TindyDb): The database to use.
        OrderNumber (Str): The order number to print the packing slip for.
    """

    if type(OrderNumber) != str:
        OrderNumber = str(OrderNumber)
        app.warn("Order Number Error", "The order number must be a string. Casting to string.")

    try:
        settings = database.table("Settings")
        orders = database.table("Orders")
        order_items = database.table("Order_Items")

        # Formatting
        Path = settings.search(
            (tinydb.Query().setting_name == "Packing_Slip_Background_Path")
            & (tinydb.Query()["process_status"] == "UTILIZE")
        )[0]["setting_value"]
        if Path == "":
            Path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "Order_Slip.png")

        TextColor = settings.search(
            (tinydb.Query().setting_name == "Packing_Slip_Text_Color")
            & (tinydb.Query()["process_status"] == "UTILIZE")
        )[0]["setting_value"]
        if TextColor == "":
            TextColor = "#000000"

        R = TextColor[1:3]
        G = TextColor[3:5]
        B = TextColor[5:7]
        # map to 0-255
        R = int(R, 16)
        G = int(G, 16)
        B = int(B, 16)
        TextColor = (R, G, B)

        IncludePrices = settings.search(
            (tinydb.Query().setting_name == "Packing_Slip_Include_Prices")
            & (tinydb.Query()["process_status"] == "UTILIZE")
        )[0]["setting_value"]
        if IncludePrices == "":  # if blank
            IncludePrices = True
        elif IncludePrices == "True":  # if true
            IncludePrices = True
        elif IncludePrices == "False":  # if false
            IncludePrices = False

        ImagesFolderPath = settings.search(
            (tinydb.Query().setting_name == "Images_Folder_Path")
            & (tinydb.Query()["process_status"] == "UTILIZE")
        )[0]["setting_value"]

        IncludeOrderNotes = settings.search(
            (tinydb.Query().setting_name == "Packing_Slip_Include_Notes")
            & (tinydb.Query()["process_status"] == "UTILIZE")
        )[0]["setting_value"]

        # Order
        try:
            order = orders.search(
                (tinydb.Query().order_number == OrderNumber)
                & (tinydb.Query().process_status == "UTILIZE")
            )[0]
        except IndexError:
            app.warn(
                "Order Error",
                "The order could not be found. Please check the order number and try again.",
            )
            return

        # Order Items
        try:
            UIDs = order["order_items_UID"]
            items = []
            for UID in UIDs:
                items.append(
                    order_items.search(
                        (tinydb.Query().item_UID == UID)
                        & (tinydb.Query().process_status == "UTILIZE")
                    )[0]
                )
        except IndexError:
            app.warn(
                "Order Items Error",
                "The order items could not be found. Please check the order number and try again.",
            )
            return

        # open image
        try:
            with Image.open(Path) as im:
                Canvas = ImageDraw.Draw(im)
        except OSError:
            app.warn(
                "Open Image Error",
                "The image file could not be opened. Please check the path and try again.",
            )
            return

        # Fonts
        SmallFont = ImageFont.truetype(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "Bright.TTF"), 15
        )
        NormalFont = ImageFont.truetype(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "Bright.TTF"), 30
        )

        # Dividing Line
        Canvas.line((400, 600, 400, 1800), fill=(TextColor))

        # Ship To
        Name = order["order_name"]
        Address1 = order["order_address"]
        Address2 = order["order_address2"]
        City = order["order_city"]
        State = order["order_state"]
        Zip = order["order_zip"]
        Canvas.text((20, 640), "Ship To:", font=NormalFont, fill=(TextColor))
        Canvas.text((20, 690), Name, font=NormalFont, fill=(TextColor))
        if Address1 != "":  # if address available
            Canvas.text((20, 730), Address1, font=NormalFont, fill=(TextColor))
            if Address2 != "":  # if address2 available
                Canvas.text((20, 770), Address2, font=NormalFont, fill=(TextColor))
                if City != "" and State != "" and Zip != "":
                    Canvas.text(
                        (20, 810),
                        City + ", " + State + " " + Zip,
                        font=NormalFont,
                        fill=(TextColor),
                    )
                elif City != "" and State != "":
                    Canvas.text(
                        (20, 810),
                        City + ", " + State,
                        font=NormalFont,
                        fill=(TextColor),
                    )
                elif State != "" and Zip != "":
                    Canvas.text((20, 810), State + " " + Zip, font=NormalFont, fill=(TextColor))
            # if address2 not available but city, state, or zip is
            elif Address2 == "" and (City != "" or State != "" or Zip != ""):
                if City != "" and State != "" and Zip != "":
                    Canvas.text(
                        (20, 770),
                        City + ", " + State + " " + Zip,
                        font=NormalFont,
                        fill=(TextColor),
                    )
                elif City != "" and State != "":
                    Canvas.text(
                        (20, 770),
                        City + ", " + State,
                        font=NormalFont,
                        fill=(TextColor),
                    )
                elif State != "" and Zip != "":
                    Canvas.text((20, 770), State + " " + Zip, font=NormalFont, fill=(TextColor))

        # From (100 between)
        Canvas.text((20, 870), "Ship From:", font=NormalFont, fill=(TextColor))
        Canvas.text((20, 920), "LeBoeuf Lasing", font=NormalFont, fill=(TextColor))
        Canvas.text((20, 960), "2255 Quance Road", font=NormalFont, fill=(TextColor))
        Canvas.text((20, 1000), "Waterford, Pa 16441", font=NormalFont, fill=(TextColor))

        # Order Number (100 between)
        OrderNumber = order["order_number"]
        Canvas.text((20, 1100), "Order Number:", font=NormalFont, fill=(TextColor))
        Canvas.text((20, 1150), str(OrderNumber), font=NormalFont, fill=(TextColor))

        # Order Date (100 between)
        OrderDate = order["order_date"]
        # if there is a space in the date then there is a time (don't include time)
        if " " in OrderDate:
            OrderDate = OrderDate.split(" ")[0]

        Canvas.text((20, 1250), "Order Date:", font=NormalFont, fill=(TextColor))
        Canvas.text((20, 1300), OrderDate, font=NormalFont, fill=(TextColor))

        # Purchase Name (100 between)
        Canvas.text((20, 1400), "Buyer:", font=NormalFont, fill=(TextColor))
        Canvas.text((20, 1450), order["order_name"], font=NormalFont, fill=(TextColor))

        # Quantity
        Quantity = 0
        for item in items:
            Quantity += int(item["item_quantity"])
        Canvas.text((500, 650), str(Quantity) + " Items", font=NormalFont, fill=(TextColor))

        # Grid Top
        if IncludePrices:
            Canvas.line((500, 700, 1400, 700), fill=(TextColor))
        else:
            Canvas.line((500, 700, 1030, 700), fill=(TextColor))

        # Header
        Canvas.text((520, 710), "QTY:", font=NormalFont, fill=(TextColor))
        Canvas.text((650, 710), "Item:", font=NormalFont, fill=(TextColor))
        if IncludePrices:
            Canvas.text((1050, 710), "Price:", font=NormalFont, fill=(TextColor))
            Canvas.text((1200, 710), "Sub-Total:", font=NormalFont, fill=(TextColor))
            Canvas.line((500, 760, 1400, 760), fill=(TextColor))
        else:
            Canvas.line((500, 760, 1030, 760), fill=(TextColor))

        # Side Bars
        SeparateItems = len(order["order_items_UID"])
        # 50 is the height of each item + 1 extra bar for titles
        length = 710 + ((SeparateItems + 1) * 50)
        Canvas.line((500, 700, 500, length), fill=(TextColor))
        Canvas.line((630, 700, 630, length), fill=(TextColor))
        Canvas.line((1030, 700, 1030, length), fill=(TextColor))
        if IncludePrices:
            Canvas.line((1180, 700, 1180, length), fill=(TextColor))
            Canvas.line((1400, 700, 1400, length), fill=(TextColor))

        # Item Fill
        for i in range(len(items)):
            Canvas.text(
                (520, 720 + (i + 1) * 50),
                str(items[i]["item_quantity"]),
                font=NormalFont,
                fill=(TextColor),
            )
            if len(items[i]["item_name"]) > 20:
                NameFont = SmallFont
            else:
                NameFont = NormalFont
            Canvas.text(
                (650, 720 + (i + 1) * 50),
                str(items[i]["item_name"]),
                font=NameFont,
                fill=(TextColor),
            )
            if IncludePrices:
                Canvas.text(
                    (1050, 720 + (i + 1) * 50),
                    "$" + str(items[i]["item_unit_price"]),
                    font=NormalFont,
                    fill=(TextColor),
                )
                Subtotal = Common.Decimal(items[i]["item_quantity"])
                Subtotal.multiply(items[i]["item_unit_price"])
                Canvas.text(
                    (1200, 720 + (i + 1) * 50),
                    "$" + str(Subtotal),
                    font=NormalFont,
                    fill=(TextColor),
                )
                Canvas.line(
                    (500, 760 + (i + 1) * 50, 1400, 760 + (i + 1) * 50),
                    fill=(TextColor),
                )
            else:
                Canvas.line(
                    (500, 760 + (i + 1) * 50, 1030, 760 + (i + 1) * 50),
                    fill=(TextColor),
                )

        # Total
        if IncludePrices:
            Total = Common.Decimal(0)
            for item in items:
                Subtotal = Common.Decimal(item["item_quantity"])
                Subtotal.multiply(item["item_unit_price"])
                Total.add(Subtotal)

            Canvas.text((520, 1600), "Total: $" + str(Total), font=NormalFont, fill=(TextColor))

        # Add Notes
        if IncludeOrderNotes:
            notes = ""
            try:
                notes = order["order_notes"]
            except KeyError:
                pass  # no notes to add

            if notes != "":
                # wrap notes to fit within the packing slip
                wrappedNotes = TextWrap(notes, 60)
                Canvas.text((520, 1700), "Order Notes:", font=NormalFont, fill=(TextColor))
                Canvas.text((520, 1750), wrappedNotes, font=NormalFont, fill=(TextColor))

        # Save Image
        im.save(os.path.join(ImagesFolderPath, str(order["order_number"]) + ".png"), "PNG")

        path = os.path.join(ImagesFolderPath, str(order["order_number"]) + ".png")
        # open the file in the default browser
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(path)
        else:  # linux variants
            subprocess.call(("xdg-open", path))
    except:
        app.warn("Packing Slip Error", traceback.format_exc())
