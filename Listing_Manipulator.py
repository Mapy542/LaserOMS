from Listing_Object import Listing
from Bill_Of_Material_Object import BOM

def Rebuild(products, product_base_prices, product_revenue, product_profit, other_pricing_styles):
    #save new product list
    try:
        with open("../Listings/Products.csv", "w") as f:
            f.truncate(0)
            f.seek(0)
            for i in range(len(products)):
                f.write(products[i] + ",")
            f.close()
    except OSError:
        print("Failed To Save Products List")
        return False

        #save all listing data

def LoadListing(listingname):
    try:
        with open("../Listings/Listings.lst", "r") as f:
            lines = f.read().split('\n')
            f.close()
            for i in range(len(lines)):
                if lines[i] == '':
                    continue
                lines[i] = lines[i].split(',')
                if lines[i][0] == listingname:
                    listing = lines[i]
                    break
                
            itemnames = []
            itemcosts = []
            for i in range(len(listing)):
                listing[i] = listing[i].split(':')
                if listing[i][0] == 'Listing_Name':
                    listing_name = listing[i][1]
                if listing[i][0] == 'Item_Name':
                    itemnames.append(listing[i][1])
                if listing[i][0] == 'Item_Cost':
                    itemcosts.append(int(listing[i][1]))
            items = []
            for i in range(len(itemnames)):
                items.append([itemnames[i],itemcosts[i]])
            newlisting = Listing(name = listing_name, items = items)
            newlisting.recalculate_overall_cost()
            return newlisting
    except OSError:
        print("Failed To Load Listing")



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
