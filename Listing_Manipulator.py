from Listing_Object import Listing
from Bill_Of_Material_Object import BOM

def PriceDelta(products, product_base_prices, product_revenue, product_profit, other_pricing_styles): #handles pricing changes
    #get current list to compare to
    pricinglist = Load_Pricing_List()

    #remake pricing list
    pricinglist2 = []
    for i in range(len(products)):
        otherstylesstring = ""
        for i in range(len(other_pricing_styles[i])):
            otherstylesstring += str(other_pricing_styles[i][i][0]) + ":" + str(other_pricing_styles[i][i][1]) + ","
        pricinglist2.append(products[i] + "," + str(product_base_prices[i]) + "," + str(product_revenue[i]) + "," + str(product_profit[i]) + "," + otherstylesstring)

    #save new pricing list
    Save_Pricing_List(pricinglist2)

    for i in range(len(pricinglist)):
        #detect item by item changes
        if pricinglist[i] not in pricinglist2:
            #change price of listing data when detected
            print(pricinglist[i] + " delta found")
            oldlisting = LoadListing(pricinglist[i].split(',')[0])
            oldlisting.setOtherPriceStyles(pricinglist[i].split(',')[5].split(','))
            oldlisting.setBasePrice(int(pricinglist[i].split(',')[1]))
            oldlisting.setRevenue(int(pricinglist[i].split(',')[2]))
            oldlisting.setProfit(int(pricinglist[i].split(',')[3]))
            SaveListing(oldlisting)

def RegeneratePricingList(): #will regenerate price list used by new order from listing data (/Listings/)
    pass

def SaveBOM(bom):
    try:
        with open("../Listings/" + str(bom.getName()) + ".bom", "w") as f:
            f.write("BOM_Name:" + str(bom.getName()) + ",")
            items = bom.getItems()
            for singleitem in items:
                f.write("Item_Name:" + str(singleitem[0]) + "," + "Item_Cost:" + str(singleitem[1]) + ",")
            f.close()
            return True
    except OSError:
        print("Failed To Save BOM")
        return False

def LoadBOM(bomname):
    try:
        with open("../Listings/" + str(bomname) + ".bom", "r") as f:
            bom = f.read().split(',')
            f.close()
            itemnames = []
            itemcosts = []
            for i in range(len(bom)):
                bom[i] = bom[i].split(':')
                if bom[i][0] == 'BOM_Name':
                    bom_name = bom[i][1]
                if bom[i][0] == 'Item_Name':
                    itemnames.append(bom[i][1])
                if bom[i][0] == 'Item_Cost':
                    itemcosts.append(int(bom[i][1]))
            items = []
            for i in range(len(itemnames)):
                items.append([itemnames[i],itemcosts[i]])
            newbom = BOM(name = bom_name, items = items)
            newbom.recalculate_overall_cost()
            return newbom
    except OSError:
        print("Failed To Load BOM")

def SaveListing(listing):
    listing.recalculateAllCosts()
    SaveBOM(listing.getBOM())
    try:
        with open("../Listings/" + str(listing.getName()) + ".lst", "w") as f:
            f.write("Listing_Name:" + str(listing.getName()) + ",")
            f.write("Listing_BOM_Name:" + str(listing.getBOM().getName()) + ",")
            f.write("Listing_Base_Price:" + str(listing.getBasePrice()) + ",")
            f.write("Listing_Revenue:" + str(listing.getRevenue()) + ",")
            f.write("Listing_Profit:" + str(listing.getProfit()) + ",")
            pricingstyles = listing.getPricingStyles()
            for i in range(len(pricingstyles)):
                f.write("Listing_Pricing_Style:" + str(pricingstyles[i][0]) + ":" + str(pricingstyles[i][1]) + ",")
            f.close()
            return True
    except OSError:
        print("Failed To Save Listing")
        return False

def LoadListing(listingname):
    try:
        with open("../Listings/" + str(listingname) + ".lst", "r") as f:
            listing = f.read().strip().split(',')
            f.close()
            pricingstyles = []
            for i in range(len(listing)):
                listing[i] = listing[i].split(':')
                if listing[i][0] == 'Listing_Name':
                    listing_name = listing[i][1]
                if listing[i][0] == 'Listing_BOM_Name':
                    bom_name = listing[i][1]
                if listing[i][0] == 'Listing_Base_Price':
                    base_price = int(listing[i][1])
                if listing[i][0] == 'Listing_Revenue':
                    revenue = int(listing[i][1])
                if listing[i][0] == 'Listing_Profit':
                    profit = int(listing[i][1])
                if listing[i][0] == 'Listing_Pricing_Style':
                    pricingstyles.append(listing[i][1].split(":"))

            if bom_name != "":
                bom = LoadBOM(bom_name)
            
            newlisting = Listing(name = listing_name, bom = bom, base_price = base_price, revenue = revenue, profit = profit, otherpricingstyles = pricingstyles)
            return newlisting
    except OSError:
        print("Failed To Load Listing")

def BulkLoadListings(listingnames):
    listings = []
    for i in range(len(listingnames)):
        listings.append(LoadListing(listingnames[i]))
    return listings

def Load_Pricing_List():
    try:
        with open("../Pricing_List.txt", "r") as f:
            pricing_list = f.read().split('\n')
            f.close()
            return pricing_list
    except OSError:
        print("Failed To Load Pricing List")

def Save_Pricing_List(pricing_list):
    try:
        with open("../Pricing_List.txt", "w") as f:
            for i in range(len(pricing_list)):
                f.write(pricing_list[i] + "\n")
            f.close()
            return True
    except OSError:
        print("Failed To Save Pricing List")
        return False