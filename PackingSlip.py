import os, math, sys
from PIL import Image, ImageDraw, ImageFont
from Order_Object import Order
from Item_Object import Item

def GeneratePackingSlip(order):
    #Formating
    infile = "Order_Slip.png"
    text_color = (0,0,0)

    try:
        with Image.open(infile) as im:
            modd = ImageDraw.Draw(im)
    except OSError:
        print("Failed Import Background.")

    #Fonts
    shmol = ImageFont.truetype('Bright.TTF', 15)
    normal = ImageFont.truetype('Bright.TTF', 30)

    #Dividing Line
    modd.line((400, 600, 400, 1800), fill=(text_color))

    #Ship To
    modd.text((20,640), 'Ship To:', font=normal, fill=(text_color))
    modd.text((20,690), order.getOrderName(), font=normal, fill=(text_color))
    modd.text((20,730), order.getOrderAddress()[0], font=normal, fill=(text_color))
    modd.text((20,770), order.getOrderAddress()[2] + ', ' + order.getOrderAddress()[3] + ' ' + order.getOrderAddress()[4], font=normal, fill=(text_color))

    #From (100 between)
    modd.text((20,870), 'Ship From:', font=normal, fill=(text_color))
    modd.text((20,920), 'Leboeuf Lasing', font=normal, fill=(text_color))
    modd.text((20,960), '2255 Quance Road', font=normal, fill=(text_color))
    modd.text((20,1000), 'Waterford, Pa 16441', font=normal, fill=(text_color))

    #Order Number (100 between)
    modd.text((20,1100), 'Order Number:', font=normal, fill=(text_color))
    modd.text((20,1150), order.getOrderNumber(), font=normal, fill=(text_color))

    #Order Date (100 between)
    modd.text((20,1250), 'Order Date:', font=normal, fill=(text_color))
    modd.text((20,1300), order.getOrderDate(), font=normal, fill=(text_color))

    #Purchase Name (100 between)
    modd.text((20,1400), 'Buyer:', font=normal, fill=(text_color))
    modd.text((20,1450), order.getOrderName(), font=normal, fill=(text_color))

    #Quantity
    modd.text((500,650), str(len(order.getOrderItems())) + ' Items', font=normal, fill=(text_color))

    #Grid Top
    modd.line((500, 700, 1400, 700), fill=(text_color))

    #Header
    modd.text((520,710), 'QTY:', font=normal, fill=(text_color))
    modd.text((650,710), 'Item:', font=normal, fill=(text_color))
    modd.text((1050,710), 'Price:', font=normal, fill=(text_color))
    modd.text((1200,710), 'Sub-Total:', font=normal, fill=(text_color))
    modd.line((500, 760, 1400, 760), fill=(text_color))

    #Side Bars
    length = 710 + ((len(order.getOrderItems()) + 1) * 50)
    modd.line((500, 700, 500, length), fill=(text_color))
    modd.line((630, 700, 630, length), fill=(text_color))
    modd.line((1030, 700, 1030, length), fill=(text_color))
    modd.line((1180, 700, 1180, length), fill=(text_color))
    modd.line((1400, 700, 1400, length), fill=(text_color))

    #Item Fill
    resize = False
    for i in range(len(order.getOrderItems())):
        if len(order.getOrderItems()[i].getProduct()) > 20:
            resize = True

    for i in range(len(order.getOrderItems())):
        if resize == False:
            modd.text((520,720+(i+1)*50), str(order.getOrderItems()[i].getQuantity()), font=normal, fill=(text_color))
            modd.text((650,720+(i+1)*50), str(order.getOrderItems()[i].getProduct()), font=normal, fill=(text_color))
            modd.text((1050,720+(i+1)*50), '$' + str(order.getOrderItems()[i].getUnitPrice(order.getPricingStyle())/100), font=normal, fill=(text_color))
            modd.text((1200,720+(i+1)*50), '$' + str(order.getOrderItems()[i].getPrice(order.getPricingStyle())/100), font=normal, fill=(text_color))
            modd.line((500, 760+(i+1)*50, 1400, 760+(i+1)*50), fill=(text_color))
        if resize == True:
            modd.text((520,720+(i+1)*50), str(order.getOrderItems()[i].getQuantity()), font=normal, fill=(text_color))
            modd.text((650,720+(i+1)*50), str(order.getOrderItems()[i].getProduct()), font=shmol, fill=(text_color))
            modd.text((1050,720+(i+1)*50), '$' + str(order.getOrderItems()[i].getUnitPrice(order.getPricingStyle())/100), font=normal, fill=(text_color))
            modd.text((1200,720+(i+1)*50), '$' + str(order.getOrderItems()[i].getPrice(order.getPricingStyle())/100), font=normal, fill=(text_color))
            modd.line((500, 760+(i+1)*50, 1400, 760+(i+1)*50), fill=(text_color))

    #Total
    modd.text((520,1600), 'Total: $' + str(order.getOrderTotal()/100), font=normal, fill=(text_color))

    im.save('../Orders/' + str(order.getOrderNumber()) + '.png', "PNG")

def PrintPackingSlip(order):
    try:
        os.system("lp -d Envy-5000 ../Orders/" + str(order.getOrderNumber()) + '.png ')

    except OSError:
        try:
            GeneratePackingSlip(order)
            os.system("lp -d Envy-5000 ../Orders/" + str(order.getOrderNumber()) + '.png ')   
        except OSError:
            print("Error Printing")
