import os
from datetime import datetime
from datetime import date
import random
import string
import tinydb
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import traceback
# from etsyv3 import EtsyV3
from etsyv3.util.auth.auth_helper import AuthHelper
from etsyv3.etsy_api import EtsyAPI
import socketserver
import Asymmetric_Encryption
import hashlib
import json


class RequestHandler(socketserver.BaseRequestHandler):
    def AccessDataBase(self, TableName, Query):
        global database
        table = database.table(TableName)
        return table.search(Query)

    def InsertDataBase(self, TableName, Data):
        global database
        table = database.table(TableName)
        table.insert(Data)

    def RemoveDataBase(self, TableName, Query):
        global database
        table = database.table(TableName)
        table.remove(Query)

    def UpdateDataBase(self, TableName, Query, Data):
        global database
        table = database.table(TableName)
        table.update(Data, Query)

    # Hashes password using sha256 into a 64 character string
    def IDTokenHash(self, ShopID, token):
        salt = str(ShopID) + token
        return hashlib.sha256(salt.encode('utf-8')).hexdigest()

    def AppendLog(self, EventType, Message):
        global database
        table = database.table('Logs')
        table.insert({'event_type': EventType, 'event_message': Message,
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
            print(self.data)
            # parse incoming data
            if self.data == b'' or self.data == b'CLOSE':
                return False, None  # connection closed
            elif self.data == b'CANCEL':
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

    def ReceiveAndDecrypt(self):
        self.RawData = self.request.recv(1024)  # receive data
        if self.RawData == b'':
            self.data = b''
            return
        self.data = Asymmetric_Encryption.DecryptData(
            self.RawData, self.PrivateKey)  # decrypt data

    def ChopSendCheck(self, string):
        # chop string into 100 byte chunks and send to client
        chunks = [string[i:i+50] for i in range(0, len(string), 50)]
        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'ChopSendCheckStart', self.ClientKey))
        self.ReceiveAndDecrypt()
        if not self.data == b'ChopSendCheckAcknowledged':
            return False  # chop send check failed
        i = 0
        while i < len(chunks):
            self.request.sendall(Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(chunks[i]), self.ClientKey))
            self.ReceiveAndDecrypt()
            # check if chunk was received correctly
            if self.data == Asymmetric_Encryption.StringToBytes(chunks[i]):
                i += 1
            else:
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ChunkResend', self.ClientKey))
                self.ReceiveAndDecrypt()
                if not self.data == b'ChunkResendAcknowledged':
                    return False  # chop send check failed

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'ChopSendCheckComplete', self.ClientKey))
        self.ReceiveAndDecrypt()
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

        self.ReceiveAndDecrypt()
        if not self.data == b'PrepareOauthAcknowledged':
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to prepare for Oauth Token Registration.')
            return False

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'SendShopID', self.ClientKey))
        self.ReceiveAndDecrypt()  # receive shop id
        self.ShopID = Asymmetric_Encryption.BytesToString(
            self.data)  # convert shop id to string

        try:  # check if shop id already exists
            exists = self.AccessDataBase(
                'OauthTokens', tinydb.Query().shop_id == self.ShopID)[0]
            if exists:
                self.AppendLog('Oauth Token Registration Failed', str(
                    self.client_address[0]) + ' failed to register a new Oauth Token because one already exists for this shop.')
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ExistingOauthToken', self.ClientKey))
                return False
        except IndexError:
            pass

        APIKeyString = self.AccessDataBase('Settings', tinydb.Query(
        ).setting_name == 'API_Key_String')[0]['setting_value']  # get API key string

        RandomState = ''.join(random.choice(string.ascii_letters + string.digits)
                              for _ in range(32))  # generate random state

        RandomCode = ''.join(random.choice(string.ascii_letters + string.digits)
                             for _ in range(100))  # generate random code

        Oauth = AuthHelper(keystring=APIKeyString,
                           redirect_uri='https://leboeuflasing.ddns.net', scopes='billing_r shops_r transactions_r', code_verifier=RandomCode, state=RandomState)  # create redirect oauth object
        UserURL = Oauth.get_auth_code()[0]  # get user url to redirect to
        print(UserURL)

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
                                            'hash': Hash})

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'AuthenticationSuccess', self.ClientKey))
        self.ReceiveAndDecrypt()
        if not self.data == b'AuthenticationSuccessAcknowledged':
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to acknowledge authentication success.')
            return False

        Success = self.ChopSendCheck(ClientToken)  # send password to client
        if not Success:
            self.AppendLog('Oauth Token Registration Failed', str(
                self.client_address[0]) + ' failed to send password to client.')
            return False

        self.AppendLog('Oauth Token Registration Success', str(
            self.client_address[0]) + ' successfully registered a new Oauth Token with ShopID:' + str(self.ShopID) + '.')  # log success
        return True

    def GetShopReceipts(self, ShopID, StartNumber, EndNumber):
        APIKeyString = self.AccessDataBase('Settings', tinydb.Query(
        ).setting_name == 'API_Key_String')[0]['setting_value']
        OauthTokenSet = self.AccessDataBase('OauthTokens', tinydb.Query(
        ).shop_id == ShopID)[0]
        print(OauthTokenSet)
        self.AppendLog('Begin Receipt Retrieval', str(
            self.client_address[0]) + ' started a new Receipt Retrieval.')
        EtsyClient = EtsyAPI(keystring=APIKeyString, token=OauthTokenSet['token'], refresh_token=OauthTokenSet['refresh_token'], expiry=datetime.fromtimestamp(
            OauthTokenSet['expires_at']), refresh_save=self.UpdateOauthToken)
        AllReceipts = []
        MaximumReceiptsPerQuery = 100
        for i in range(StartNumber, EndNumber, MaximumReceiptsPerQuery):
            try:
                Receipts = EtsyClient.get_shop_receipts(shop_id=int(
                    OauthTokenSet['shop_id']), limit=int(MaximumReceiptsPerQuery), offset=int(i))
                AllReceipts += Receipts['results']
            except:
                self.AppendLog('Receipt Retrieval Failed', str(
                    self.client_address[0]) + ' failed to retrieve Receipts from Etsy.')
                return False, None
        self.AppendLog('Receipt Retrieval Success', str(
            self.client_address[0]) + ' successfully retrieved Receipts from Etsy.')
        return True, AllReceipts

    def UpdateOauthToken(self, Token, RefreshToken, ExpiresAt):
        self.UpdateDataBase('OauthTokens', tinydb.Query().shop_id == self.ShopID, {
                            'token': Token, 'refresh_token': RefreshToken, 'expires_at': datetime.timestamp(ExpiresAt)})

    def AuthenticateSession(self):
        self.ReceiveAndDecrypt()
        ShopID = self.data.decode('utf-8')  # get shop id from data
        self.ShopID = ShopID
        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'ShopIDReceived', self.ClientKey))  # send shop id received acknowledgement to client
        ClientToken = self.ChopReceiveCheck()  # receive token from client
        if not ClientToken:
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
            self.AppendLog('Authentication Failed', str(
                self.client_address[0]) + ' failed to authenticate with ShopID:' + str(ShopID) + '.')
            return False, None

        return True, OauthTokenSet

    def handle(self):
        # generate new keys for each handshake
        self.PrivateKey, self.PublicKey = Asymmetric_Encryption.GenerateKeyPair()

        self.LoggedIn = False

        Success, self.ClientKey = self.Handshake()
        if not Success:
            self.AppendLog('Handshake Failed', str(
                self.client_address[0]) + ' failed to handshake with server.')
            return

        self.AppendLog('Handshake Success', str(
            self.client_address[0]) + ' successfully started a secure communication.')

        self.request.sendall(Asymmetric_Encryption.EncryptData(
            b'Listening', self.ClientKey))  # send listening acknowledgement to client to start sending data
        self.Action = 'Listening'

        while True:
            self.ReceiveAndDecrypt()
            print(self.data)
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
            elif self.Action == 'Listening' and self.data == b'RemoveToken' and self.LoggedIn:
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ConfirmRemoveToken', self.ClientKey))
                self.Action = 'RemoveToken'
                continue
            elif self.Action == 'RemoveToken' and self.data == b'ConfirmRemoveTokenAcknowledged' and self.LoggedIn:
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'ResendToken', self.ClientKey))
                data = self.ChopReceiveCheck()
                if not data:
                    self.AppendLog('Remove Token Failed', str(
                        self.client_address[0]) + ' failed to send token to server.')
                    return False
                self.RemoveDataBase('OauthTokens', tinydb.Query(
                ).hash == self.IDTokenHash(self.ShopID, data))
                self.AppendLog('Remove Token Success', str(
                    self.client_address[0]) + ' successfully removed token for shop ID:' + str(self.ShopID) + '.')  # log success
                self.Action = 'Listening'
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'RemoveTokenSuccess', self.ClientKey))
            elif self.Action == 'Listening' and self.data == b'QueryReceipts' and self.LoggedIn:
                self.Action = 'QueryReceipts'
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'QueryCount', self.ClientKey))
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


def VerifySettings(database):
    settings = database.table('Settings')
    MadeUpdate = False
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

    if not settings.contains((tinydb.Query().setting_name == 'API_Key_String')):
        settings.insert({'setting_name': 'API_Key_String', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 13, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 13}, tinydb.Query(
    ).setting_name == 'API_Key_String')

    return MadeUpdate


try:
    database = tinydb.TinyDB(os.path.join(os.path.realpath(os.path.dirname(__file__)),
                                          '../Server.json'), storage=CachingMiddleware(JSONStorage))  # load database (use memory cache)
    if VerifySettings(database):
        print('Updated Settings')
    # setup server
    HOST, PORT = "", 55555  # listen on all interfaces on port 55555
    with socketserver.TCPServer((HOST, PORT), RequestHandler) as server:
        server.serve_forever()

except Exception as err:  # catch all errors
    print(traceback.format_exc())  # print error
finally:
    database.close()  # close database
    server.close_request()  # close server
    # NOT CLOSED PROPERLY RESULTS IN LOSS OF CACHED CHANGES
