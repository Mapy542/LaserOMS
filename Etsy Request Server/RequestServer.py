import os
from datetime import datetime
import tinydb
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import traceback
#from etsyv3 import EtsyV3
from etsyv3.util.auth.auth_helper import AuthHelper
import socketserver
import Asymmetric_Encryption


class RequestHandler(socketserver.BaseRequestHandler):
    def AccessDataBase(self, TableName, Query):
        global database
        table = database.table(TableName)
        return table.search(Query)

    def handle(self):
        self.ClientKey = ''
        # generate new keys for each handshake
        self.PrivateKey, self.PublicKey = Asymmetric_Encryption.GenerateKeyPair()
        self.HandsShakeStatus = 3
        self.Action = 'Initialize'
        self.ShopID = ''
        while True:
            self.data = self.request.recv(1024).strip()  # receive data

            # parse incoming data
            if self.data == b'':
                break  # client disconnected
            elif self.data == b'CLOSE' or self.data == b'CANCEL':
                break
            elif self.data == b'InitiateHandshake' and self.HandsShakeStatus == 2:  # start handshake
                self.request.sendall(self.PublicKey)  # send public key
                self.HandsShakeStatus = 2
                continue
            # receive client key
            elif self.HandsShakeStatus == 2 and (self.data != b'InitiateHandshake' or self.data != b'CANCEL'):
                self.ClientKey = Asymmetric_Encryption.DecryptData(
                    self.data, self.PrivateKey)
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'HandshakeComplete', self.ClientKey))  # send handshake complete to verify success
                self.HandsShakeStatus = 1
                continue
            elif self.HandsShakeStatus == 1:  # verify handshake success
                self.DecryptedData = Asymmetric_Encryption.DecryptData(
                    self.data, self.PrivateKey)  # decrypt data
                if not self.DecryptedData == b'HandshakeCompleteAcknowledged':
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'HandshakeFailed', self.ClientKey))  # send handshake failed and close connection
                    break
                else:
                    self.HandsShakeStatus = 0  # handshake complete ready to communicate
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(Asymmetric_Encryption.EncryptData(
                        b'Listening', self.ClientKey))
                    self.Action = 'Listening'
                    continue

            self.DecryptedData = Asymmetric_Encryption.DecryptData(
                self.data, self.PrivateKey)  # decrypt data

            if self.HandsShakeStatus == 0 and self.DecryptedData == b'CANCEL':
                self.Action = 'Listening'
                # send listening acknowledgement to client to start sending data
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'Listening', self.ClientKey))
                continue
            elif self.HandsShakeStatus == 0 and self.Action == 'Listening' and self.DecryptedData == b'SetShopId':
                # send self.Action ready acknowledgement to client to start sending data
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'Continue', self.ClientKey))
                self.Action = 'SetShopId'
                continue
            elif self.HandsShakeStatus == 0 and self.Action == 'SetShopId' and self.DecryptedData != b'SetShopId':
                self.ShopID = self.DecryptedData.decode('utf-8')  # set shop id
                # send success acknowledgement to client that data was received
                self.request.sendall(Asymmetric_Encryption.EncryptData(
                    b'Success', self.ClientKey))
                self.Action = 'Listening'
                continue


def VerifySettings(database):
    settings = database.table('Settings')
    MadeUpdate = False
    if not settings.contains((tinydb.Query().setting_name == 'Empty')):
        settings.insert({'setting_name': 'Empty', 'setting_value': 'Empty',
                        'setting_type': 'BOOLEAN', 'setting_rank': 0, 'process_status': "IGNORE"})
        MadeUpdate = True

    # Version
    if not settings.contains((tinydb.Query().setting_name == 'LaserOMS_Server_Version')):
        settings.insert({'setting_name': 'LaserOMS_Version', 'setting_value': '1.0.0',
                        'setting_type': 'STATIC', 'setting_rank': 1, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 1},
                    tinydb.Query().setting_name == 'LaserOMS_Version')

    if not settings.contains((tinydb.Query().setting_name == 'Etsy_API_Client_Key')):
        settings.insert({'setting_name': 'Etsy_API_Client_Key', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 13, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 13}, tinydb.Query(
    ).setting_name == 'Etsy_API_Client_Key')
    if not settings.contains((tinydb.Query().setting_name == 'Etsy_API_Client_Secret')):
        settings.insert({'setting_name': 'Etsy_API_Client_Secret', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 14, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 14}, tinydb.Query(
    ).setting_name == 'Etsy_API_Client_Secret')

    return MadeUpdate


try:
    database = tinydb.TinyDB(os.path.join(os.path.realpath(os.path.dirname(__file__)),
                                          '../Server-Settings.json'), storage=CachingMiddleware(JSONStorage))  # load database (use memory cache)

    # setup server
    HOST, PORT = "", 55555
    with socketserver.TCPServer((HOST, PORT), RequestHandler) as server:
        server.serve_forever()


except Exception as err:  # catch all errors
    print(traceback.format_exc())  # print error
finally:
    database.close()  # close database
    server.close_request()  # close server
    # NOT CLOSED PROPERLY RESULTS IN LOSS OF CACHED CHANGES
