import urllib.request
import tinydb


def RebuildProductsFromSheets(app, database):
    # download data from link
    download = DownloadListings(app, database)
    if download == None:  # If download failed, return false
        return False

    products = database.table('Products')  # Get products table
    pricing_styles = database.table(
        'Product_Pricing_Styles')  # Get pricing styles table

    # Remove all products and pricing styles that are to be imported from google sheets
    products.remove((tinydb.where('process_status') == 'UTILIZE') & (
        tinydb.where('google_sheet_listing') == "TRUE"))
    pricing_styles.remove((tinydb.where('process_status') == 'UTILIZE') & (
        tinydb.where('google_sheet_listing') == "TRUE"))
    lines = download.split('\n')  # Split data into lines
    firstline = lines[0].split(',')  # Get first line

    fieldnames = []  # Get field names
    fieldindexes = []  # Get field indexes
    pricingstylenames = []  # Get pricing style names
    pricingstyleindexes = []  # Get pricing style indexes
    for i in range(len(firstline)):
        # If line is ~, end of data is reached even if lines have not been exhausted
        if firstline[i] == "~":
            break
        elif "**" in firstline[i]:  # If line contains **, it is a pricing style
            pricingstylenames.append(firstline[i].replace("**", ""))
            pricingstyleindexes.append(i)
        elif firstline[i] != "":  # If line is not empty, it is a field name
            fieldnames.append(firstline[i])
            fieldindexes.append(i)

    for i in range(len(pricingstylenames)):  # Insert pricing styles into database
        pricing_styles.insert(
            {'style_name': pricingstylenames[i], 'process_status': "UTILIZE", 'google_sheet_listing': "TRUE"})

    lines.pop(0)  # Remove first line from lines
    productcount = 0  # Count number of products imported
    for i in range(len(lines)):  # Insert products into database
        line = lines[i].split(',')
        if line[0] == '':  # if line is empty, do not add as product
            continue
        product = {}  # Create product
        for j in range(len(fieldnames)):  # Add fields to product
            product[fieldnames[j]] = line[fieldindexes[j]]
        product['process_status'] = "UTILIZE"  # Set process status to utilize
        # Set google sheet listing to true
        product['google_sheet_listing'] = "TRUE"
        for l in range(len(pricingstylenames)):  # Add pricing styles to product
            product[pricingstylenames[l].replace(
                " ", "_")] = line[pricingstyleindexes[l]]
        products.insert(product)  # Insert product into database
        productcount += 1  # Increment product count

    app.info("Product Import Successful", str(productcount) +
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
