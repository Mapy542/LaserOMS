import os

def SyncSheetItems():
    #Get updated pricing from google

    #to be dynamic soon
    try:
        with open("../Pricing_List_Link.txt", "r") as f:
            link = f.read().strip()
            f.close()
    except OSError:
        print("Failed To Read Pricing List Link")
        return False

    os.system('wget -O ../Items.cvs ' + link) #download google sheet

    #parse file
    products = []
    product_prices = []
    product_income = []
    product_wp = []
    product_etsy = []
    product_market = []

    try:
        with open("../Items.cvs", "r") as f:
            num_lines = sum(1 for line in open("../Items.cvs")) #this big dumb
            for i in range(num_lines):
                injest = f.readline()
                injest = injest.split(',')
                products.append(injest[0])
                product_prices.append(injest[4])
                product_income.append(injest[6])
                product_wp.append(injest[7])
                product_etsy.append(injest[8])
                product_market.append(injest[9])
            f.close()
    except OSError:
        print("Failed To Injest Item Database")

    #trim
    products.pop(0)
    product_prices.pop(0)
    product_income.pop(0)
    product_wp.pop(0)
    product_etsy.pop(0)
    product_market.pop(0)

    products = list(filter(None, products))
    product_prices = list(filter(None, product_prices))
    product_income = list(filter(None, product_income))
    product_wp = list(filter(None, product_wp))
    product_etsy = list(filter(None, product_etsy))
    product_market = list(filter(None, product_market))

    for i in range(len(product_prices)):
        product_prices[i] = int(round(float(product_prices[i]),2)*100)
        product_income[i] = int(round(float(product_income[i]),2)*100)
        product_wp[i] = int(round(float(product_wp[i]),2)*100)
        product_etsy[i] = int(round(float(product_etsy[i]),2)*100)
        product_market[i] = int(round(float(product_market[i]),2)*100)


    print(products)
    print(product_prices)
    print(product_income)

    if len(products) != len(product_prices) or len(products) != len(product_income) or len(product_income) != len(product_prices):
        print('Items values do not correlate. Check for empty values in pricing.')
        
    #save to new file
    try:
        with open("../Items.txt", "w") as f:
            for i in range(len(products)):
                f.writelines(str(products[i]) + ',' + str(product_prices[i]) + ',' + str(product_income[i]) + ',' +
                str(product_wp[i]) + ',' + str(product_etsy[i]) + ',' + str(product_market[i]) + ', \n')
            f.close()
    except OSError:
        print("Failed To Update Item Database")
