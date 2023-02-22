from guizero import Text, TextBox, CheckBox, Combo, PushButton, ListBox, Window
from datetime import datetime
import difflib as dl
import tinydb
import PackingSlip
import random


def price_update():
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global products
    global realitems, pricing_style
    global window2

    product_names = []
    for product in products:
        product_names.append(product['product_name'])
    autofill1 = dl.get_close_matches(item1.value, product_names)
    item1.value = autofill1[0]
    realitems[0] = products.search(tinydb.Query().product_name == item1.value)
    item_price1.value = "$" + \
        str(realitems[0][pricing_style]/100 * int(item_quant1.value))
    autofill2 = dl.get_close_matches(item2.value, product_names)
    item2.value = autofill2[0]
    realitems[1] = products.search(tinydb.Query().product_name == item2.value)
    item_price2.value = "$" + \
        str(realitems[1][pricing_style]/100 * int(item_quant2.value))
    autofill3 = dl.get_close_matches(item3.value, product_names)
    item3.value = autofill3[0]
    realitems[2] = products.search(tinydb.Query().product_name == item3.value)
    item_price3.value = "$" + \
        str(realitems[2][pricing_style]/100 * int(item_quant3.value))
    autofill4 = dl.get_close_matches(item4.value, product_names)
    item4.value = autofill4[0]
    realitems[3] = products.search(tinydb.Query().product_name == item4.value)
    item_price4.value = "$" + \
        str(realitems[3][pricing_style]/100 * int(item_quant4.value))
    autofill5 = dl.get_close_matches(item5.value, product_names)
    item5.value = autofill5[0]
    realitems[4] = products.search(tinydb.Query().product_name == item5.value)
    item_price5.value = "$" + \
        str(realitems[4][pricing_style]/100 * int(item_quant5.value))

    totalnumber = realitems[0][pricing_style] * int(item_quant1.value) + realitems[1][pricing_style] * int(item_quant2.value) + realitems[2][pricing_style] * int(
        item_quant3.value) + realitems[3][pricing_style] * int(item_quant4.value) + realitems[4][pricing_style] * int(item_quant5.value)
    total.value = "Total: $" + str(totalnumber/100)


def export():
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global products, baseprice, wordpress_price, etsy_price, editboromarket_price
    global realitems
    global window2
    global orders, order_items

    last_order_number = orders.search(
        tinydb.Query().order_name == 'LAST_ORDER')['order_number']
    orders.update(tinydb.operations.increment('order_number'),
                  tinydb.Query().order_name == 'LAST_ORDER')

    UID = random.randint(1000000000, 9999999999)
    all_uids = []
    for order in orders:
        all_uids.append(order['UID'])
    while UID in all_uids:
        UID = random.randint(1000000000, 9999999999)
    orders.insert({'order_number': last_order_number + 1, 'order_name': purchase_name.value,
                   'order_adress': adress.value, 'order_adress2': adress2.value, 'order_city': city.value,
                   'order_state': state.value, 'order_zip': zip_code.value, 'order_items_UID': UID, 'order_date': datetime.today().strftime('%m-%d-%Y'),
                   'order_status': 'Open', 'Process_Status': 'UTILIZE'})

    price_update()
    new_items = []
    for item in realitems:
        if item['product_name'] != 'Empty':
            new_items.append(item)

    for item in new_items:
        order_items.insert(item)
        order_items[len(order_items) - 1]['UID'] = UID

    if choose_export.value == 1:
        PackingSlip.GeneratePackingSlip(last_order_number + 1)
        PackingSlip.PrintPackingSlip(last_order_number + 1)

    if choose_ship.value == 1:
        # ShipppingHandler.ShipOrder(order)
        pass

    window2.destroy()


def update_pricing_options():
    global styles, pricing_style
    pricing_style = styles[pricing_option_button.value]
    price_update()


def NewOrder(main_window):
    global purchase_name, adress, adress2, city, state, zip_code, pricing_option_button, item1, item2, item3, item4, item5
    global item_quant1, item_quant2, item_quant3, item_quant4, item_quant5, item_price1, item_price2, item_price3, item_price4
    global item_price5, total, choose_export, choose_ship, finish
    global products, styles
    global realitems, pricing_style
    global window2

    pricing_style = styles[0]['style_name']
    realitems = []

    for i in range(0, 5):
        realitems.append(products.get(tinydb.Query().product_name == "Empty"))

    style_names = []
    for i in range(len(styles)):
        style_names.append(styles[i]['style_name'])

    window2 = Window(main_window, title="New Order",
                     layout="grid", width=1100, height=700)
    welcome_message = Text(window2, text='Generate New Order.',
                           size=18, font="Times New Roman", grid=[1, 0])

    purchase_name_text = Text(
        window2, text='Buyer Name', size=15, font="Times New Roman", grid=[0, 1])
    purchase_name = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    adress_text = Text(window2, text='Adress', size=15,
                       font="Times New Roman", grid=[0, 3])
    adress = TextBox(window2, grid=[1, 3], width=60)
    adress_text2 = Text(window2, text='Line 2', size=15,
                        font="Times New Roman", grid=[0, 4])
    adress2 = TextBox(window2, grid=[1, 4], width=60)
    city_text = Text(window2, text='City', size=15,
                     font="Times New Roman", grid=[0, 5])
    city = TextBox(window2, grid=[1, 5], width=30)
    state_text = Text(window2, text='State', size=15,
                      font="Times New Roman", grid=[0, 6])
    state = TextBox(window2, grid=[1, 6], width=10)
    zip_text = Text(window2, text='Zip Code', size=15,
                    font="Times New Roman", grid=[0, 7])
    zip_code = TextBox(window2, grid=[1, 7], width=10)
    # items header
    items_message = Text(window2, text='Include Items',
                         size=18, font="Times New Roman", grid=[1, 8])

    pricing_option_button = Combo(
        window2, options=style_names, command=update_pricing_options, grid=[2, 7])
    # items
    item1 = TextBox(window2, width=30, grid=[0, 9], text='Empty')
    item_quant1 = TextBox(
        window2, grid=[1, 9], width=10, command=price_update, text='0')
    item_price1 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 9])

    item2 = TextBox(window2, width=30, grid=[0, 10], text='Empty')
    item_quant2 = TextBox(
        window2, grid=[1, 10], width=10, command=price_update, text='0')
    item_price2 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 10])

    item3 = TextBox(window2, width=30, grid=[0, 11], text='Empty')
    item_quant3 = TextBox(
        window2, grid=[1, 11], width=10, command=price_update, text='0')
    item_price3 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 11])

    item4 = TextBox(window2, width=30, grid=[0, 12], text='Empty')
    item_quant4 = TextBox(
        window2, grid=[1, 12], width=10, command=price_update, text='0')
    item_price4 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 12])

    item5 = TextBox(window2, width=30, grid=[0, 13], text='Empty')
    item_quant5 = TextBox(
        window2, grid=[1, 13], width=10, command=price_update, text='0')
    item_price5 = Text(window2, text='0', size=15,
                       font="Times New Roman", grid=[2, 13])

    # Total
    total = Text(window2, text='Total: $0', size=18,
                 font="Times New Roman", grid=[2, 19])

    # Export Options
    choose_export = CheckBox(window2, text="Export Order", grid=[1, 19])
    choose_ship = CheckBox(window2, text="Ship Order", grid=[1, 20])
    finish = PushButton(window2, command=export, text='Save', grid=[0, 19])
