import os


def RebuildProductsFromSheets(products, prods):
    # download data from link
    DownloadListings()

    try:
        with open("../Items.cvs", "r") as f:
            itemscvs = f.read().split("\n")
            f.close()
    except OSError:
        print("Failed To Read Items.cvs")
        return False

    fields = itemscvs[0].split(',')

    products.truncate()
    for i in range(len(itemscvs)):  # for each item line
        item = itemscvs[i].split(',')  # split into fields
        itemdata = {}  # make dictionary
        for i in range(len(fields)):  # for each field
            itemdata[fields[i]] = item[i]  # add field to dictionary
        products.insert(itemdata)  # add item to database

    prods.truncate()
    for i in range(len(fields)):  # for each field
        if '**' in fields[i]:  # if field is a pricing style
            prods.insert({'style_name': fields[i].replace(
                '**', ''), 'Process_Status': "UTILIZE"})  # add style to database


def DownloadListings():
    # Get link from individuals file
    try:
        with open("../Pricing_List_Link.txt", "r") as f:
            link = f.read().strip()
            f.close()
    except OSError:
        print("Failed To Read Pricing List Link")
        return False

    # download data from link
    os.system('wget -O ../Items.cvs ' + link)
