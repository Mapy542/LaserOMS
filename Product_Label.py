import copy
import os
import platform
import subprocess
import time
import traceback

import tinydb
from guizero import Combo, ListBox, PushButton, Text, Window
from PIL import Image, ImageDraw, ImageFont

import Common
from PackingSlip import TextWrap


def PrintProductLabel(app, database, ProductName, PricingStyle):
    """Prints a packing slip for the given order number.

    Args:
        app (GuiZero Window): The main window of the program.
        database (TindyDb): The database to use.
        ProductName (Str): The name of the product to print a label for.
        PricingStyle (Str): The pricing style to use.
    """

    if type(ProductName) != str:
        ProductName = str(ProductName)
        app.warn("Order Number Error", "The order number must be a string. Casting to string.")

    try:
        settings = database.table("Settings")
        products = database.table("Products")
        pricingStyles = database.table("Product_Pricing_Styles")

        # Formatting
        Path = settings.search(
            (tinydb.Query().setting_name == "Label_Background_Path")
            & (tinydb.Query()["process_status"] == "UTILIZE")
        )[0]["setting_value"]
        if Path == "":
            Path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "Order_Slip.png")

        TextColor = settings.search(
            (tinydb.Query().setting_name == "Label_Text_Color")
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

        ImagesFolderPath = settings.search(
            (tinydb.Query().setting_name == "Images_Folder_Path")
            & (tinydb.Query()["process_status"] == "UTILIZE")
        )[0]["setting_value"]

        # company name
        try:
            companyName = settings.search(
                (tinydb.Query().setting_name == "Company_Name")
                & (tinydb.Query()["process_status"] == "UTILIZE")
            )[0]["setting_value"]
        except IndexError:
            companyName = ""

        # company website
        try:
            companyWebsite = settings.search(
                (tinydb.Query().setting_name == "Company_Website")
                & (tinydb.Query()["process_status"] == "UTILIZE")
            )[0]["setting_value"]
        except IndexError:
            companyWebsite = ""

        # include website
        try:
            showWebsite = settings.search(
                (tinydb.Query().setting_name == "Label_Include_Website")
                & (tinydb.Query()["process_status"] == "UTILIZE")
            )[0]["setting_value"]
        except IndexError:
            showWebsite = False

        # product
        try:
            product = products.search(
                (tinydb.Query().product_name == ProductName)
                & (tinydb.Query().process_status == "UTILIZE")
            )[0]
        except IndexError:
            app.warn(
                "Query Error",
                "The product could not be found. Please check the product name and try again.",
            )
            return

        # product pricing style
        try:
            pricingStyle = pricingStyles.search(
                (tinydb.Query().style_name == PricingStyle)
                & (tinydb.Query().process_status == "UTILIZE")
            )[0]
        except IndexError:
            app.warn(
                "Query Error",
                "The pricing style could not be found.",
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
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "Bright.TTF"), 25
        )
        MediumFont = ImageFont.truetype(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "Bright.TTF"), 50
        )
        NormalFont = ImageFont.truetype(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "Bright.TTF"), 40
        )
        BigFont = ImageFont.truetype(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "Bright.TTF"), 80
        )

        """Label 600w x 300h"""

        # Company info
        Canvas.text((20, 150), companyName, font=MediumFont, fill=(TextColor))
        if showWebsite:
            wrappedText = TextWrap(companyWebsite, 20)
            Canvas.text((20, 220), wrappedText, font=NormalFont, fill=(TextColor))

        # Product Name
        if len(product["product_name"]) > 15:
            wrappedText = TextWrap(product["product_name"], 25)
            Canvas.text((250, 30), wrappedText, font=(SmallFont), fill=(TextColor))
        else:
            wrappedText = TextWrap(product["product_name"], 15)
            Canvas.text((250, 30), wrappedText, font=(NormalFont), fill=(TextColor))

        # Product Price
        try:
            Price = Common.Decimal(product[pricingStyle["style_name"].replace(" ", "_")])
        except KeyError:
            app.warn(
                "Query Error",
                "The pricing style could not be found in the product. Please check the pricing style and try again.",
            )
            return
        Canvas.text((20, 30), "$" + str(Price), font=BigFont, fill=(TextColor))

        # Save Image
        im.save(os.path.join(ImagesFolderPath, str(product["product_name"]) + ".png"), "PNG")

        path = os.path.join(ImagesFolderPath, str(product["product_name"]) + ".png")
        # open the file in the default browser
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", path))
        elif platform.system() == "Windows":  # Windows
            os.startfile(path)
        else:  # linux variants
            subprocess.call(("xdg-open", path))
    except:
        app.warn("Label Making Error", traceback.format_exc())


def ProductLabelsSelector(app, database):
    """A GUI for selecting a products to print labels for.

    Args:
        app (GUIZero App): The an application window.
        database (TinyDB): The database to use.
    """

    def FillProductListbox(products, Listbox):
        """Fills a listbox with products.

        Args:
            products (List): The products to fill the listbox with.
            Listbox (ListBox): The listbox to fill.
        """

        Listbox.clear()

        for product in products:
            Listbox.append(product["product_name"])

    def LoopPrintLabels(app, database, ProductListbox, PricingStyleSelector):
        """Prints labels for the selected products.

        Args:
            app (GUIZero App): The an application window.
            database (TinyDB): The database to use.
            ProductListbox (ListBox): The listbox of products to print labels for.
            PricingStyleSelector (Combo): The combo box of pricing styles to use.
        """

        for value in ProductListbox.value:
            PrintProductLabel(app, database, value, PricingStyleSelector.value)
            time.sleep(1)  # buffer file opening otherwise it will not open multiple files

    window2 = Window(app, title="Product Labels", layout="grid", width=700, height=700)

    # get the products
    products = database.table("Products")
    activeProducts = products.search(tinydb.where("process_status") == "UTILIZE")

    # get the pricing styles
    pricingStyles = database.table("Product_Pricing_Styles")
    activePricingStyles = pricingStyles.search(tinydb.where("process_status") == "UTILIZE")

    # create the listbox
    ProductListbox = ListBox(
        window2,
        items=[],
        multiselect=True,
        width=600,
        height=400,
        scrollbar=True,
        grid=[0, 0, 4, 5],
    )

    FillProductListbox(activeProducts, ProductListbox)

    # select product pricing style
    PricingStyleSelector = Combo(
        window2,
        options=[pricingStyle["style_name"] for pricingStyle in activePricingStyles],
        grid=[0, 5],
    )

    # make button
    PrintButton = PushButton(
        window2,
        text="Print Labels",
        command=lambda: LoopPrintLabels(app, database, ProductListbox, PricingStyleSelector),
        grid=[1, 5],
    )
