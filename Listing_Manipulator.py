from Listing_Object import Listing
from Bill_Of_Material_Object import BOM
import os

def Rebuild():
    #download data from link
    DownloadListings()

    #read indicators from file
    try:
        with open("../Indicators.txt", "r") as f:
            indicators = f.read().strip().split(",")
    except:
        print("Failed To Read Indicators")
        return False

    pricing_styles_indicators = []
    for name in indicators:
        if "**" in name:
            pricing_styles_indicators.append(name)
    
    for indicator in pricing_styles_indicators:
        indicators.remove(indicator)

    #parse file to find indicators
    pricing_styles_indicies = []
    indicies = []
    try:
        with open("../Items.cvs", "r") as f:
            line1 = f.readline()
            line1.strip().split(',')
            for i in range(len(line1)):
                if line1[i] in indicators:
                    indicies.append(i, line1[i])
                elif line1[i] in pricing_styles_indicators:
                    pricing_styles_indicies.append(i, line1[i].strip('**'))

            
    except OSError:
        print("Failed To Read Items.cvs")
        return False

    #parse file to find items
    products = []
    product_base_prices = []
    product_revenue = []
    product_profit = []

    other_pricing_styles = []

    try:
        with open("../Items.cvs", "r") as f:
            for line in f:
                if line == '\n':
                    continue
                line = line.strip().split(',')
                products.append(line[product_index])
                product_base_prices.append(int(line[base_price_index])*100)
                product_revenue.append(int(line[revenue_index])*100)
                product_profit.append(int(line[profit_index])*100)
                item_pricing_styles = []
                for i in range(len(pricing_styles_index)):
                    item_pricing_styles.append(int(line[pricing_styles_index[i][0]])*100, line[pricing_styles_index[i][1]])
                other_pricing_styles.append(item_pricing_styles)
    except OSError:
        print("Failed To Read Items.cvs")
        return False


def DownloadListings():
    #Get link from individuals file
    try:
        with open("../Pricing_List_Link.txt", "r") as f:
            link = f.read().strip()
            f.close()
    except OSError:
        print("Failed To Read Pricing List Link")
        return False

    #download data from link
    os.system('wget -O ../Items.cvs ' + link)


