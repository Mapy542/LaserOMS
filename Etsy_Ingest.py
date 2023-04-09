import tinydb
import json
import socket
import datetime
import webbrowser
from Etsy_Request_Server import Asymmetric_Encryption


def ImportEtsyOrders(app, database):
    # get etsy keys and info
    settings = database.table('Settings')
    ShopID = settings.get(tinydb.where('setting_name') ==
                          'Etsy_Shop_ID')['setting_value']
    Token = settings.get(tinydb.where('setting_name') ==
                         'Etsy_Request_Server_Token')['setting_value']
    RequestServerAddress = settings.get(tinydb.where(
        'setting_name') == 'Etsy_Request_Server_Address')['setting_value']

    if ShopID == '':  # if shop id is not set
        UserShopID = app.question(
            'Etsy Ingest Error', 'Etsy Shop ID not set. Enter now or cancel to exit.').strip()
        if UserShopID == '':
            app.warn('Etsy Ingest Error',
                     'Etsy Shop ID not set. Ingest cancelled.')
            return 0
        else:
            settings.upsert({'setting_value': UserShopID},
                            tinydb.where('setting_name') == 'Etsy_Shop_ID')
            ShopID = UserShopID

    HOST = RequestServerAddress  # The server's hostname or IP address
    PORT = 55555  # The port used by the server
    PrivateKey, PublicKey = Asymmetric_Encryption.GenerateKeyPair()  # generate key pair

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # connect to server
        Success, ServerKey = Asymmetric_Encryption.ClientHandshake(
            s, PublicKey, PrivateKey)  # handshake with server
        if not Success:
            app.warn('Request Server Connection Failed',
                     'Handshake failed, unable to communicate to server.')
            return 0
        # authentication loop. if token is not set, set it up, then log in
        while True:
            if Token == '':
                app.info('Etsy Oauth Initialization',
                         'Request Server needs to access to Etsy Shop.')
                app.info('User Actionable Steps', '1. A web browser will open to the Etsy Oauth page. 2. Click "Allow" to allow access to your shop. 3. The Oauth page will redirect to leboeuflasing.ddns.net. User must copy the URL from the address bar and paste it into the dialog box that will appear.')
                s.sendall(Asymmetric_Encryption.EncryptData(
                    b'CreateOauthToken', ServerKey))
                data = Asymmetric_Encryption.DecryptData(
                    s.recv(1024), PrivateKey)
                if data == b'PrepareOauth':
                    s.sendall(Asymmetric_Encryption.EncryptData(
                        b'PrepareOauthAcknowledged', ServerKey))
                else:
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to prepare for Oauth.')
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(1024), PrivateKey)
                if data == b'SendShopID':
                    s.sendall(Asymmetric_Encryption.EncryptData(
                        Asymmetric_Encryption.StringToBytes(ShopID), ServerKey))
                else:
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to receive Shop ID.')
                    return 0

                UserURL = Asymmetric_Encryption.ChopReceiveCheck(
                    s, ServerKey, PrivateKey)  # receive URL from server
                if UserURL == False:  # if URL not received
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to receive URL.')
                    return 0
                webbrowser.open(UserURL)  # open URL in web browser
                UserURI = app.question(
                    'User Actionable Steps', 'Enter the URL from the address bar of the web browser that was opened.').strip()

                if UserURI == '':
                    app.warn('Request Server Connection Failed',
                             'User did not enter URL.')
                    return 0

                Success = Asymmetric_Encryption.ChopSendCheck(
                    UserURI, s, ServerKey, PrivateKey)  # send URL to server
                if not Success:
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to receive URL.')
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(1024), PrivateKey)
                if data == b'AuthenticationSuccess':
                    s.sendall(Asymmetric_Encryption.EncryptData(
                        b'AuthenticationSuccessAcknowledged', ServerKey))
                else:
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to authenticate.')
                    return 0

                Token = Asymmetric_Encryption.ChopReceiveCheck(
                    s, ServerKey, PrivateKey)  # receive token from server
                if Token == False:  # if token not received
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to receive token.')
                    return 0
                settings.upsert({'setting_value': Token}, tinydb.where(
                    'setting_name') == 'Etsy_Request_Server_Token')
            else:  # token exists
                s.sendall(Asymmetric_Encryption.EncryptData(
                    b'AuthenticateSession', ServerKey))
                data = Asymmetric_Encryption.DecryptData(
                    s.recv(1024), PrivateKey)
                if not data == b'SendShopID':
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to prepare for authentication.')
                    return 0
                s.sendall(Asymmetric_Encryption.EncryptData(
                    Asymmetric_Encryption.StringToBytes(ShopID), ServerKey))
                data = Asymmetric_Encryption.DecryptData(
                    s.recv(1024), PrivateKey)
                if not data == b'ShopIDReceived':
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to receive Shop ID.')
                    return 0
                Success = Asymmetric_Encryption.ChopSendCheck(
                    Token, s, ServerKey, PrivateKey)
                if not Success:
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to receive token.')
                    return 0
                data = Asymmetric_Encryption.DecryptData(
                    s.recv(1024), PrivateKey)
                if not data == b'AuthenticationSuccess':
                    app.warn('Request Server Connection Failed',
                             'Request Server failed to authenticate.')
                    return 0
                break

        # query test
        s.sendall(Asymmetric_Encryption.EncryptData(
            b'QueryReceipts', ServerKey))
        data = Asymmetric_Encryption.DecryptData(
            s.recv(1024), PrivateKey)
        if not data == b'QueryCount':
            app.warn('Request Server Connection Failed',
                     'Request Server failed to prepare for query.')
            return 0
        s.sendall(Asymmetric_Encryption.EncryptData(
            Asymmetric_Encryption.StringToBytes('39'), ServerKey))
        Receipts = Asymmetric_Encryption.ChopReceiveCheck(
            s, ServerKey, PrivateKey)
        print(Receipts)
    return 1
