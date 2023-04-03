import tinydb
import json
import requests


def ImportEtsyOrders(app, database):
    # get etsy keys and info
    settings = database.table('Settings')
    ClientKey = settings.search(tinydb.where(
        'setting_name') == 'Etsy_API_Client_Key')[0]['setting_value']
    ClientSecret = settings.search(tinydb.where(
        'setting_name') == 'Etsy_API_Client_Secret')[0]['setting_value']
    OAuthToken = settings.search(tinydb.where(
        'setting_name') == 'Etsy_API_OAuth_Token')[0]['setting_value']
    OAuthTokenSecret = settings.search(tinydb.where(
        'setting_name') == 'Etsy_API_OAuth_Token_Secret')[0]['setting_value']
    ShopID = settings.search(tinydb.where('setting_name') == 'Etsy_Shop_ID')[
        0]['setting_value']

    # try to connect to etsy
    oauth = AuthHelper()
    return 1
