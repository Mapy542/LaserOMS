from etsy2 import Etsy
from etsy2.oauth import EtsyOAuthClient

#Validate from API keys and Oauth tokens
try:
    with open("../oauth.txt", "r") as f:
        tokens = f.read()
        tokens = tokens.split(',')
        oauth_token = tokens[0]
        oauth_token_secret = tokens[1]
        clikey = tokens[3].strip()
        csecret = tokens[4].strip()
        shopid = tokens[2].strip()
        print(tokens)
        f.close()
except OSError:
    print("Failed Get OAuth tokens")

#Pull api data    
etsy_oauth = EtsyOAuthClient(client_key=clikey,
                            client_secret=csecret,
                            resource_owner_key=oauth_token,
                            resource_owner_secret=oauth_token_secret)
etsy = Etsy(etsy_oauth_client=etsy_oauth)
data1 = etsy.findAllShopReceiptsByStatus(shop_id=shopid,status='unshipped')
data = etsy.findAllShopReceipts(shopid)


#WIP