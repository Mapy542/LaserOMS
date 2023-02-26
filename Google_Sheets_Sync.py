import urllib.request
import tinydb


def RebuildProductsFromSheets(app, database):
    # download data from link
    download = DownloadListings(app, database)
    if download == None:  # If download failed, return false
        return False

    products = database.table('Products')  # Get products table
    PricingStyles = database.table(
        'Product_PricingStyles')  # Get pricing styles table

    # Remove all products and pricing styles that are to be imported from google sheets
    products.remove((tinydb.where('process_status') == 'UTILIZE') & (
        tinydb.where('google_sheet_listing') == "TRUE"))
    PricingStyles.remove((tinydb.where('process_status') == 'UTILIZE') & (
        tinydb.where('google_sheet_listing') == "TRUE"))
    lines = download.split('\n')  # Split data into lines
    FirstLine = lines[0].split(',')  # Get first line

    FieldNames = []  # Get field names
    FieldIndexes = []  # Get field indexes
    PricingStylesName = []  # Get pricing style names
    PricingStylesIndexes = []  # Get pricing style indexes
    for i in range(len(FirstLine)):
        # If line is ~, end of data is reached even if lines have not been exhausted
        if FirstLine[i] == "~":
            break
        elif "**" in FirstLine[i]:  # If line contains **, it is a pricing style
            PricingStylesName.append(FirstLine[i].replace("**", ""))
            PricingStylesIndexes.append(i)
        elif FirstLine[i] != "":  # If line is not empty, it is a field name
            FieldNames.append(FirstLine[i])
            FieldIndexes.append(i)

    for i in range(len(PricingStylesName)):  # Insert pricing styles into database
        PricingStyles.insert(
            {'style_name': PricingStylesName[i], 'process_status': "UTILIZE", 'google_sheet_listing': "TRUE"})

    lines.pop(0)  # Remove first line from lines
    ProductCount = 0  # Count number of products imported
    for i in range(len(lines)):  # Insert products into database
        line = lines[i].split(',')
        if line[0] == '':  # if line is empty, do not add as product
            continue
        product = {}  # Create product
        for j in range(len(FieldNames)):  # Add fields to product
            product[FieldNames[j]] = line[FieldIndexes[j]]
        product['process_status'] = "UTILIZE"  # Set process status to utilize
        # Set google sheet listing to true
        product['google_sheet_listing'] = "TRUE"
        for l in range(len(PricingStylesName)):  # Add pricing styles to product
            product[PricingStylesName[l].replace(
                " ", "_")] = line[PricingStylesIndexes[l]]
        products.insert(product)  # Insert product into database
        ProductCount += 1  # Increment product count

    app.info("Product Import Successful", str(ProductCount) +
             " Products Imported From Google Sheet")  # Display success message
    return True


def DownloadListings(app, database):  # Download listings from google sheets
    settings = database.table('Settings')  # Get settings table
    url = settings.search(tinydb.where('setting_name') == 'Google_Sheet_Link')[
        0]['setting_value'].strip()  # Get google sheet link
    if url == '':
        # If no link found, display error message
        app.warn("Error", "No Google Sheet Link Found")
        return None
    try:
        response = urllib.request.urlopen(url)  # Open url
        data = response.read()      # a `bytes` object
        # a `str`; this step can't be used if data is binary
        text = data.decode('utf-8')
    except:
        # If download failed, display error message
        app.warn("Error", "Failed To Download Google Sheet")
        return None
    return text  # Return data
