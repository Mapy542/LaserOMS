import os
from datetime import datetime
import random
import string
import tinydb
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import traceback
from etsyv3.util.auth.auth_helper import AuthHelper
from etsyv3.etsy_api import EtsyAPI
import socketserver
import Asymmetric_Encryption
import hashlib
import json


class RequestHandler(socketserver.BaseRequestHandler):
    def AccessDataBase(self, TableName, Query):  # access database
        global database
        table = database.table(TableName)  # get table
        return table.search(Query)  # return query results

    def InsertDataBase(self, TableName, Data):  # insert data into
        global database
        table = database.table(TableName)  # get table
        table.insert(Data)  # insert data

    def RemoveDataBase(self, TableName, Query):  # remove data from database
        global database
        table = database.table(TableName)  # get table
        table.remove(Query)  # remove data

    def UpdateDataBase(self, TableName, Query, Data):
        global database
        table = database.table(TableName)  # get table
        table.update(Data, Query)  # update data

    # Hashes token using sha256 into a 64 character string
    def IDTokenHash(self, ShopID, token):
        salt = str(ShopID) + token  # salt is shop id and token
        # hash salt and return
        return hashlib.sha256(salt.encode('utf-8')).hexdigest()

    def AppendLog(self, EventType, Message):  # append log to database
        global database
        table = database.table('Logs')
        table.insert({'event_type': EventType, 'event_message': Message,  # insert log
                      'event_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'event_year': datetime.now().strftime("%Y"), 'event_month': datetime.now().strftime("%m")})

        # remove logs older than 1 year
        table.remove(tinydb.Query().event_year < datetime.now().strftime("%Y"))
        table.remove(tinydb.Query().event_year == datetime.now().strftime("%Y") and tinydb.Query(
        ).event_month < datetime.now().strftime("%m"))  # remove logs older than 1 month

    def Handshake(self):
        # handshake status 3 = initiate handshake, 2 = send public key, 1 = receive client key, 0 = handshake complete
        self.HandsShakeStatus = 3
        while True:
            self.data = self.request.recv(1024).strip()  # receive data
            # parse incoming data
            if self.data == b'' or self.data == b'CLOSE':
                return False, None  # connection closed
            elif self.data == b'CANCEL':  # cancel handshake and restart
                self.request.sendall(b'HandshakeRestart')
                self.HandsShakeStatus = 3
                continue
            elif self.data == b'InitiateHandshake' and self.HandsShakeStatus == 3:  # start handshake
                self.request.sendall(Asymmetric_Encryption.SendablePublicKey(
                    self.PublicKey))  # send public key
                self.HandsShakeStatus = 2
                continue
            # receive client key
            elif self.HandsShakeStatus == 2 and self.data != b'InitiateHandshake':
                self.ClientKey = Asymmetric_Encryption.LoadPublicKey(
                    self.data)  # load client key
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'HandshakeComplete', self.ClientKey))  # send handshake complete to verify success
                self.HandsShakeStatus = 1
                continue
            elif self.HandsShakeStatus == 1:  # verify handshake success
                self.data = Asymmetric_Encryption.DecryptData(
                    self.data, self.PrivateKey)  # decrypt data
                if not self.data == b'HandshakeCompleteAcknowledged':
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'HandshakeFailed', self.ClientKey))  # send handshake failed and close connection
                    return False, None
                else:
                    self.HandsShakeStatus = 0  # handshake complete ready to communicate
                    # send listening acknowledgement to client to start sending data
                    return True, self.ClientKey

    def ReceiveAndDecrypt(self):  # receive and decrypt data generic and reusable
        self.RawData = self.request.recv(1024)  # receive data
        if self.RawData == b'':  # check if connection was closed or data was empty
            self.data = b''  # set data to empty
            # decryption fails if data is empty so return to prevent error
            return
        self.data = Asymmetric_Encryption.DecryptData(
            self.RawData, self.PrivateKey)  # decrypt data

    def ChopSendCheck(self, string):
        # chop string into 50 byte chunks and send to client (MAX is 86 theoretically based on 1024 bit transmission)
        chunks = [string[i:i+50] for i in range(0, len(string), 50)]
        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'ChopSendCheckStart', self.ClientKey))  # send chop send check start
        self.ReceiveAndDecrypt()  # receive chop send check start acknowledgement
        if not self.data == b'ChopSendCheckAcknowledged':
            return False  # chop send check failed
        i = 0
        while i < len(chunks):
            # send chunk
            self.request.sendall(Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(chunks[i]), self.ClientKey))
            self.ReceiveAndDecrypt()  # receive chunk
            # check if chunk was received correctly
            if self.data == Asymmetric_Encryption.StringToBytes(chunks[i]):
                i += 1
            else:
                # if chunk was not received correctly send chunk resend request
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ChunkResend', self.ClientKey))
                self.ReceiveAndDecrypt()  # receive chunk resend request acknowledgement
                if not self.data == b'ChunkResendAcknowledged':
                    return False  # chop send check failed

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'ChopSendCheckComplete', self.ClientKey))  # send chop send check complete
        self.ReceiveAndDecrypt()  # receive chop send check complete acknowledgement
        if not self.data == b'ChopSendCheckCompleteAcknowledged':
            return False  # chop send check failed

        return True  # chop send check complete

    def ChopReceiveCheck(self):
        self.ReceiveAndDecrypt()  # receive chop send check start
        if not self.data == b'ChopSendCheckStart':  # check if chop send check start was received correctly
            return False
        self.request.sendall(Asymmetric_Encryption.EncryptData(  # send chop send check acknowledged
            b'ChopSendCheckAcknowledged', self.ClientKey))
        chunks = []
        while True:  # receive chunks
            self.ReceiveAndDecrypt()  # receive chunk
            if self.data == b'ChopSendCheckComplete':  # check if chop send check complete was received correctly
                self.request.sendall(Asymmetric_Encryption.EncryptData(  # send chop send check complete acknowledged
                    b'ChopSendCheckCompleteAcknowledged', self.ClientKey))
                break  # chop send check complete
            elif self.data == b'ChunkResend':  # check if chunk resend was received correctly
                self.request.sendall(Asymmetric_Encryption.EncryptData(  # send chunk resend acknowledged
                    b'ChunkResendAcknowledged', self.ClientKey))
                chunks.pop()  # remove last chunk from list
                continue
            else:
                chunks.append(Asymmetric_Encryption.BytesToString(
                    self.data))  # add chunk to list
                self.request.sendall(Asymmetric_Encryption.EncryptData(  # send chunk acknowledged
                    self.data, self.ClientKey))
        return ''.join(chunks)

    def CreateOauthToken(self):
        self.AppendLog('Begin Oauth Token Registration', str(
            self.client_address[0]) + ' started a new Oauth Token Registration.')
        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'PrepareOauth', self.ClientKey))  # send prepare oauth to client to start oauth process

        self.ReceiveAndDecrypt()  # receive prepare oauth acknowledgement
        # check if prepare oauth acknowledgement was received correctly
        if not self.data == b'PrepareOauthAcknowledged':
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to prepare for Oauth Token Registration.')
            return False

        self.request.sendall(Asymmetric_Encryption.EncryptData(  # send shop id request
            b'SendShopID', self.ClientKey))
        self.ReceiveAndDecrypt()  # receive shop id
        self.ShopID = Asymmetric_Encryption.BytesToString(
            self.data)  # convert shop id to string

        try:  # check if shop id already exists
            exists = self.AccessDataBase(
                'OauthTokens', tinydb.Query().shop_id == self.ShopID)[0]
            if exists:
                # if shop id already exists send existing oauth token message to client and close connection
                self.AppendLog('Oauth Token Registration Failed', str(
                    self.client_address[0]) + ' failed to register a new Oauth Token because one already exists for this shop.')
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ExistingOauthToken', self.ClientKey))
                return False
        except IndexError:
            pass

        APIKeyString = self.AccessDataBase('Settings', tinydb.Query(
        ).setting_name == 'API_Key_String')[0]['setting_value']  # get API key string

        # ETSY required random security strings
        RandomState = ''.join(random.choice(string.ascii_letters + string.digits)
                              for _ in range(32))  # generate random state

        RandomCode = ''.join(random.choice(string.ascii_letters + string.digits)
                             for _ in range(100))  # generate random code

        # create redirect oauth object
        Oauth = AuthHelper(keystring=APIKeyString,
                           redirect_uri='https://leboeuflasing.ddns.net', scopes='billing_r shops_r transactions_r', code_verifier=RandomCode, state=RandomState)  # create redirect oauth object
        UserURL = Oauth.get_auth_code()[0]  # get user url to redirect to

        Success = self.ChopSendCheck(UserURL)  # send user url to client
        if not Success:
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to send user url to client.')
            return False
        UserURI = self.ChopReceiveCheck()  # receive user uri from client

        try:
            # get headless uri from user uri
            HeadlessURI = UserURI.split('code=')[1]
            # get code and state from headless uri
            CodeAndState = HeadlessURI.split('&state=')
            code = CodeAndState[0]
            state = CodeAndState[1]
        except:
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to get code and state from user uri.')
            return False

        try:
            # set code and state in oauth object
            Oauth.set_authorisation_code(code, state)
            TokenDictionary = Oauth.get_access_token()  # get token from oauth object
            # get token from token dictionary
            Token = TokenDictionary['access_token']
            # get refresh token from token dictionary
            RefreshToken = TokenDictionary['refresh_token']
            # get expires at from token dictionary
            ExpiresAt = TokenDictionary['expires_at']
        except:
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to get oauth token from Etsy.')
            return False

        ClientToken = ''.join(random.choice(string.ascii_letters + string.digits)  # generate client token
                              for _ in range(100))
        # hash client token with shop id
        Hash = self.IDTokenHash(self.ShopID, ClientToken)

        self.InsertDataBase('OauthTokens', {'shop_id': self.ShopID, 'token': Token, 'refresh_token': RefreshToken, 'expires_at': ExpiresAt,
                                            'hash': Hash})  # insert oauth token into database

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'AuthenticationSuccess', self.ClientKey))  # send authentication success to client
        self.ReceiveAndDecrypt()
        # check if authentication success acknowledgement was received correctly
        if not self.data == b'AuthenticationSuccessAcknowledged':
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to acknowledge authentication success.')
            return False

        Success = self.ChopSendCheck(ClientToken)  # send password to client
        if not Success:
            self.AppendLog('Oauth Token Registration Failed', str(  # log failure
                self.client_address[0]) + ' failed to send password to client.')
            return False

        self.AppendLog('Oauth Token Registration Success', str(  # log success
            self.client_address[0]) + ' successfully registered a new Oauth Token with ShopID:' + str(self.ShopID) + '.')  # log success
        return True

    # get shop receipts from Etsy for a given shop id
    def GetShopReceipts(self, ShopID, StartNumber, EndNumber):
        """
        Etsy API call to get receipts for a given shop id.

        Keyword arguments:
        @param ShopID -- the shop id to get receipts for
        @param StartNumber -- the start number of the receipt range
        @param EndNumber -- the end number of the receipt range
        """
        APIKeyString = self.AccessDataBase('Settings', tinydb.Query(
        ).setting_name == 'API_Key_String')[0]['setting_value']  # get API key string
        OauthTokenSet = self.AccessDataBase('OauthTokens', tinydb.Query(
        ).shop_id == ShopID)[0]  # get oauth token set from database

        self.AppendLog('Begin Receipt Retrieval', str(  # log receipt retrieval start
            self.client_address[0]) + ' started a new Receipt Retrieval.')

        EtsyClient = EtsyAPI(keystring=APIKeyString, token=OauthTokenSet['token'], refresh_token=OauthTokenSet['refresh_token'], expiry=datetime.fromtimestamp(
            OauthTokenSet['expires_at']), refresh_save=self.UpdateOauthToken)  # create Etsy API client

        AllReceipts = []
        # maximum number of receipts per query (Etsy API limit)
        MaximumReceiptsPerQuery = 100
        for i in range(StartNumber, EndNumber, MaximumReceiptsPerQuery):
            try:
                Receipts = EtsyClient.get_shop_receipts(shop_id=int(  # get receipts from Etsy
                    OauthTokenSet['shop_id']), limit=int(MaximumReceiptsPerQuery), offset=int(i))
                AllReceipts += Receipts['results']  # add receipts to list
            except:
                self.AppendLog('Receipt Retrieval Failed', str(  # log failure
                    self.client_address[0]) + ' failed to retrieve Receipts from Etsy.')
                return False, None

        self.AppendLog('Receipt Retrieval Success', str(  # log success
            self.client_address[0]) + ' successfully retrieved Receipts from Etsy.')
        return True, AllReceipts

    def GetShop(self, ShopID):
        """
        Etsy API call to get shop information for a given shop id.

        Keyword arguments:
        @param ShopID -- the shop id to get shop information for
        """
        APIKeyString = self.AccessDataBase('Settings', tinydb.Query(
        ).setting_name == 'API_Key_String')[0]['setting_value']  # get API key string
        OauthTokenSet = self.AccessDataBase('OauthTokens', tinydb.Query(
        ).shop_id == ShopID)[0]  # get oauth token set from database

        self.AppendLog('Begin Shop Retrieval', str(  # log shop retrieval start
            self.client_address[0]) + ' started a new Shop Retrieval.')

        EtsyClient = EtsyAPI(keystring=APIKeyString, token=OauthTokenSet['token'], refresh_token=OauthTokenSet['refresh_token'], expiry=datetime.fromtimestamp(
            OauthTokenSet['expires_at']), refresh_save=self.UpdateOauthToken)  # create Etsy API client

        try:
            Shop = EtsyClient.get_shop(shop_id=int(  # get shop from Etsy
                OauthTokenSet['shop_id']))
            print(Shop)
        except:
            self.AppendLog('Shop Retrieval Failed', str(  # log failure
                self.client_address[0]) + ' failed to retrieve Shop from Etsy.')
            return False, None

        self.AppendLog('Shop Retrieval Success', str(  # log success
            self.client_address[0]) + ' successfully retrieved Shop from Etsy.')
        return True, Shop

    # update oauth token in database (Etsy API Package use only)

    def UpdateOauthToken(self, Token, RefreshToken, ExpiresAt):
        # Token must be refreshed after expiry so the package handles this automatically
        self.UpdateDataBase('OauthTokens', tinydb.Query().shop_id == self.ShopID, {  # update oauth token in database
                            'token': Token, 'refresh_token': RefreshToken, 'expires_at': datetime.timestamp(ExpiresAt)})

        self.AppendLog('Oauth Token Updated', str(  # log success
            self.client_address[0]) + ' successfully updated Oauth Token with ShopID:' + str(self.ShopID) + '.')  # log success

    def AuthenticateSession(self):
        self.ReceiveAndDecrypt()  # receive shop id from client

        ShopID = Asymmetric_Encryption.BytesToString(
            self.data)  # get shop id from data
        self.ShopID = ShopID

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'ShopIDReceived', self.ClientKey))  # send shop id received acknowledgement to client

        ClientToken = self.ChopReceiveCheck()  # receive token from client
        if not ClientToken:  # check if token was received correctly
            self.AppendLog('Authentication Failed', str(
                self.client_address[0]) + ' failed to send password to server.')
            return False, None

        # hash token with shop id
        Hash = self.IDTokenHash(ShopID, ClientToken)

        try:
            # get token from database with shop id and hash
            OauthTokenSet = self.AccessDataBase('OauthTokens', (tinydb.Query().shop_id == ShopID) & (
                tinydb.Query().hash == Hash))[0]
        except:
            self.AppendLog('Authentication Failed', str(  # log failure
                self.client_address[0]) + ' failed to authenticate with ShopID:' + str(ShopID) + '.')
            return False, None

        # return success and oauth token set (set not currently used. A database query is used instead because of the etsy token refresh)
        return True, OauthTokenSet

    def handle(self):
        # generate new keys for each handshake
        self.PrivateKey, self.PublicKey = Asymmetric_Encryption.GenerateKeyPair()

        self.LoggedIn = False  # set logged in to false

        # handshake with client for secure communication
        Success, self.ClientKey = self.Handshake()
        if not Success:
            self.AppendLog('Handshake Failed', str(  # log failure
                self.client_address[0]) + ' failed to handshake with server.')
            return

        self.AppendLog('Handshake Success', str(  # log success
            self.client_address[0]) + ' successfully started a secure communication.')

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'Listening', self.ClientKey))  # send listening acknowledgement to client to start sending data
        self.Action = 'Listening'

        while True:
            self.ReceiveAndDecrypt()

            # close connection if client sends b''
            if self.data == b'' and self.Action == 'Listening':
                self.AppendLog('Connection Closed', str(
                    self.client_address[0]) + ' closed connection.')
                return

            if self.data == b'CANCEL':
                self.Action = 'Listening'
                # send listening acknowledgement to client to start sending data
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'Listening', self.ClientKey))
                continue

            elif self.Action == 'Listening' and self.data == b'CreateOauthToken':
                self.Action = 'CreateAPIToken'
                Success = self.CreateOauthToken()  # create new oauth token
                if not Success:
                    self.Action = 'Listening'
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'OauthFailed', self.ClientKey))
                    continue

            elif self.Action == 'Listening' and self.data == b'AuthenticateSession':
                self.Action = 'AuthenticateSession'
                # send start acknowledgement to client to start sending data
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'SendShopID', self.ClientKey))
                Success, self.OauthTokenSet = self.AuthenticateSession()  # authenticate session
                if not Success:
                    self.Action = 'Listening'
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'AuthenticationFailed', self.ClientKey))
                else:
                    self.LoggedIn = True
                    self.Action = 'Listening'
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'AuthenticationSuccess', self.ClientKey))
                    self.AppendLog('Authentication Success', str(
                        self.client_address[0]) + ' successfully authenticated with ShopID:' + str(self.ShopID) + '.')
                continue

            elif self.Action == 'Listening' and self.data == b'RemoveToken' and self.LoggedIn:
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ConfirmRemoveToken', self.ClientKey))  # send confirmation to client to remove token
                self.Action = 'RemoveToken'
                continue

            elif self.Action == 'RemoveToken' and self.data == b'ConfirmRemoveTokenAcknowledged' and self.LoggedIn:
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ResendToken', self.ClientKey))
                data = self.ChopReceiveCheck()  # receive token from client
                if not data:  # check if token was received correctly
                    self.AppendLog('Remove Token Failed', str(
                        self.client_address[0]) + ' failed to send token to server.')
                    return False
                self.RemoveDataBase('OauthTokens', tinydb.Query(
                ).hash == self.IDTokenHash(self.ShopID, data))
                self.AppendLog('Remove Token Success', str(
                    self.client_address[0]) + ' successfully removed token for shop ID:' + str(self.ShopID) + '.')  # log success
                self.Action = 'Listening'  # set action to listening
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'RemoveTokenSuccess', self.ClientKey))  # send listening acknowledgement to client to start sending data
                continue

            elif self.Action == 'Listening' and self.data == b'QueryReceipts' and self.LoggedIn:
                self.Action = 'QueryReceipts'
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'QueryCount', self.ClientKey))  # send query count acknowledgement to client to start sending data
                continue

            elif self.Action == 'QueryReceipts' and self.LoggedIn:
                Count = int(self.data.decode('utf-8'))
                Success, Receipts = self.GetShopReceipts(self.ShopID, 0, Count)
                if not Success:
                    self.Action = 'Listening'
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'QueryReceiptsFailed', self.ClientKey))
                    continue
                StringReceipts = json.dumps(Receipts)
                Success = self.ChopSendCheck(StringReceipts)
                if not Success:
                    self.AppendLog('Query Receipts Failed', str(
                        self.client_address[0]) + ' failed to send receipt data to server.')
                else:
                    self.AppendLog('Query Receipts Success', str(
                        self.client_address[0]) + ' successfully queried receipts for shop ID:' + str(self.ShopID) + '.')  # log success
                self.Action = 'Listening'

            elif self.Action == 'Listening' and self.data == b'QueryShop' and self.LoggedIn:
                self.Action = 'QueryShop'
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'PrepareQueryShop', self.ClientKey))
                continue

            elif self.Action == 'QueryShop' and self.LoggedIn:
                Success, Shop = self.GetShop(self.ShopID)
                if not Success:
                    self.Action = 'Listening'
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'QueryShopFailed', self.ClientKey))
                    self.AppendLog('Query Shop Failed', str(
                        self.client_address[0]) + ' failed query for shop ID:' + str(self.ShopID) + '.')
                    continue
                else:
                    self.AppendLog('Query Shop Success', str(  # log success
                        self.client_address[0]) + ' successfully queried shop for shop ID:' + str(self.ShopID) + '.')
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'QueryShopSuccess', self.ClientKey))
                StringShop = json.dumps(Shop)
                Success = self.ChopSendCheck(StringShop)
                if not Success:
                    self.AppendLog('Query Shop Failed', str(
                        self.client_address[0]) + ' failed to receive shop data from server.')
                self.Action = 'Listening'
                continue


def VerifySettings(database):
    # Verify Settings to make sure they are all there
    settings = database.table('Settings')

    MadeUpdate = False  # Flag to see if any updates were made

    if not settings.contains((tinydb.Query().setting_name == 'Empty')):
        settings.insert({'setting_name': 'Empty', 'setting_value': 'Empty',
                        'setting_type': 'BOOLEAN', 'setting_rank': 0, 'process_status': "IGNORE"})
        MadeUpdate = True

    # Version
    if not settings.contains((tinydb.Query().setting_name == 'LaserOMS_Server_Version')):
        settings.insert({'setting_name': 'LaserOMS_Server_Version', 'setting_value': '1.0.0',
                        'setting_type': 'STATIC', 'setting_rank': 1, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 1},
                    tinydb.Query().setting_name == 'LaserOMS_Server_Version')

    # API Key String for accessing the API
    if not settings.contains((tinydb.Query().setting_name == 'API_Key_String')):
        settings.insert({'setting_name': 'API_Key_String', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 13, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 13}, tinydb.Query(
    ).setting_name == 'API_Key_String')

    return MadeUpdate


try:
    database = tinydb.TinyDB(os.path.join(os.path.realpath(os.path.dirname(__file__)),
                                          '../../Server.json'), storage=CachingMiddleware(JSONStorage))  # load database (use memory cache)
    if VerifySettings(database):
        print('Updated Settings. Closing Server. Check Server.json for changes.')
        exit(0)

    # setup server
    HOST, PORT = "", 55555  # listen on all interfaces on port 55555

    with socketserver.TCPServer((HOST, PORT), RequestHandler) as server:  # create server
        server.serve_forever()  # start server

except Exception as err:  # catch all errors
    print(traceback.format_exc())  # print error
finally:
    database.close()  # close database
    server.close_request()  # close server
    # NOT CLOSED PROPERLY RESULTS IN LOSS OF CACHED CHANGES
