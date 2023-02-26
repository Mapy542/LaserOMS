import urllib.request
import tinydb



def RebuildProductsFromSheets(app, database):
    # download data from link
    download = DownloadListings(app, database)
    if download == None:
        return False

    products = database.table('Products')
    pricing_styles = database.table('Product_Pricing_Styles')

    products.remove((tinydb.where('process_status') == 'UTILIZE') & (tinydb.where('google_sheet_listing') == "TRUE"))
    pricing_styles.remove((tinydb.where('process_status') == 'UTILIZE') & (tinydb.where('google_sheet_listing') == "TRUE"))
    lines = download.split('\n')
    firstline = lines[0].split(',')

    fieldnames = []
    fieldindexes = []
    pricingstylenames = []
    pricingstyleindexes = []
    for i in range(len(firstline)):
        if firstline[i] == "~":
            break
        elif "**" in firstline[i]:
            pricingstylenames.append(firstline[i].replace("**", ""))
            pricingstyleindexes.append(i)
        elif firstline[i] != "":
            fieldnames.append(firstline[i])
            fieldindexes.append(i)

    for i in range(len(pricingstylenames)):
        pricing_styles.insert({'style_name': pricingstylenames[i], 'process_status': "UTILIZE", 'google_sheet_listing': "TRUE"})

    lines.pop(0)
    productcount = 0
    for i in range(len(lines)):
        line = lines[i].split(',')
        if line[0] == '':
            continue
        product = {}
        for j in range(len(fieldnames)):
            product[fieldnames[j]] = line[fieldindexes[j]]
        product['process_status'] = "UTILIZE"
        product['google_sheet_listing'] = "TRUE"
        for l in range(len(pricingstylenames)):
            product[pricingstylenames[l].replace(" ", "_")] = line[pricingstyleindexes[l]]
        products.insert(product)
        productcount += 1

    app.info("Product Import Successful", str(productcount) + " Products Imported From Google Sheet")
    return True

def DownloadListings(app, database):
    settings = database.table('Settings')
    url = settings.search(tinydb.where('setting_name') == 'Google_Sheet_Link')[0]['setting_value'].strip()
    if url == '':
        app.warn("Error", "No Google Sheet Link Found")
        return None
    try:
        response = urllib.request.urlopen(url)
        data = response.read()      # a `bytes` object
        text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    except:
        app.warn("Error", "Failed To Download Google Sheet")
        return None
    return text
