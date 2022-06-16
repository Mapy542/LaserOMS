import os, Listing_Manipulator

def SyncSheetItems():
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

    #parse file to find indicators
    pricing_styles_index = []
    try:
        with open("../Items.cvs", "r") as f:
            line1 = f.readline()
            line1.strip().split(',')
            for i in range(len(line1)):
                if line1[i] == 'Item':
                    product_index = i
                elif line1[i] == 'Base Price':
                    base_price_index = i
                elif line1[i] == 'Revenue':
                    revenue_index = i
                elif line1[i] == 'Profit':
                    profit_index = i
                elif '**' in line1[i]:
                    pricing_styles_index.append(i, line1[i].strip('**'))
                elif line1[i] == 'WP':
                    wp_index = i
                elif line1[i] == 'Etsy':
                    etsy_index = i
                elif line1[i] == 'Market':
                    market_index = i
            
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

    #update listing database
    Listing_Manipulator.PriceDelta(products, product_base_prices, product_revenue, product_profit, other_pricing_styles)
   