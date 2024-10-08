import hashlib
import json
import os
import random
import signal
import socketserver
import string
import threading
import time
import traceback
from datetime import datetime

import Asymmetric_Encryption
import tinydb
from etsyv3.etsy_api import EtsyAPI
from etsyv3.util.auth.auth_helper import AuthHelper
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage


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

    def LogConnectIP(self, IP):  # log ip address of connected client
        self.InsertDataBase("IPs", {"ip": IP, "date": datetime.now().timestamp()})
        self.RemoveDataBase(
            "IPs", tinydb.Query().date < datetime.now().timestamp() - 86400
        )  # remove ips older than 1 day

    def AllowConnection(self, IP):  # check if ip is allowed to connect
        instances = self.AccessDataBase(
            "IPs", tinydb.Query().ip == IP
        )  # check if ip is in database
        if len(instances) > 10:  # ip is in database
            return False  # ip is not allowed to connect
        return True  # ip is allowed to connect

    # Hashes token using sha256 into a 64 character string
    def IDTokenHash(self, ShopID, token):
        salt = str(ShopID) + token  # salt is shop id and token
        # hash salt and return
        return hashlib.sha256(salt.encode("utf-8")).hexdigest()

    def AppendLog(self, EventType, Message):  # append log to database
        global database
        table = database.table("Logs")
        table.insert(
            {
                "event_type": EventType,
                "event_message": Message,  # insert log
                "event_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_year": datetime.now().strftime("%Y"),
                "event_month": datetime.now().strftime("%m"),
            }
        )

        # remove logs older than 1 year
        table.remove(tinydb.Query().event_year < datetime.now().strftime("%Y"))
        table.remove(
            tinydb.Query().event_year == datetime.now().strftime("%Y")
            and tinydb.Query().event_month < datetime.now().strftime("%m")
        )  # remove logs older than 1 month

    def Handshake(self):
        # handshake status 3 = initiate handshake, 2 = send public key, 1 = receive client key, 0 = handshake complete
        self.HandsShakeStatus = 3
        while True:
            self.data = self.request.recv(Asymmetric_Encryption.KeySize()).strip()  # receive data
            # parse incoming data
            if self.data == b"" or self.data == b"CLOSE":
                return False, None  # connection closed
            elif self.data == b"CANCEL":  # cancel handshake and restart
                self.request.sendall(b"HandshakeRestart")
                self.HandsShakeStatus = 3
                continue
            elif (
                self.data == b"InitiateHandshake" and self.HandsShakeStatus == 3
            ):  # start handshake
                self.request.sendall(
                    Asymmetric_Encryption.SendablePublicKey(self.PublicKey)
                )  # send public key
                self.HandsShakeStatus = 2
                continue
            # receive client key
            elif self.HandsShakeStatus == 2 and self.data != b"InitiateHandshake":
                self.ClientKey = Asymmetric_Encryption.LoadPublicKey(self.data)  # load client key
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"HandshakeComplete", self.ClientKey)
                )  # send handshake complete to verify success
                self.HandsShakeStatus = 1
                continue
            elif self.HandsShakeStatus == 1:  # verify handshake success
                self.data = Asymmetric_Encryption.DecryptData(
                    self.data, self.PrivateKey
                )  # decrypt data
                if not self.data == b"HandshakeCompleteAcknowledged":
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"HandshakeFailed", self.ClientKey)
                    )  # send handshake failed and close connection
                    return False, None
                else:
                    self.HandsShakeStatus = 0  # handshake complete ready to communicate
                    # send listening acknowledgement to client to start sending data
                    return True, self.ClientKey

    def ReceiveAndDecrypt(self):  # receive and decrypt data generic and reusable
        self.RawData = self.request.recv(Asymmetric_Encryption.PacketSize())  # receive data
        if self.RawData == b"":  # check if connection was closed or data was empty
            self.data = b""  # set data to empty
            # decryption fails if data is empty so return to prevent error
            return
        self.data = Asymmetric_Encryption.DecryptData(self.RawData, self.PrivateKey)  # decrypt data

    """
    def ChopSendCheck(self, string):
        # chop string into Asymmetric_Encryption.MaxStringLen() byte chunks and send to client (MAX is 86 theoretically based on Asymmetric_Encryption.PacketSize() bit transmission)
        chunks = [
            string[i : i + Asymmetric_Encryption.MaxStringLen()]
            for i in range(0, len(string), Asymmetric_Encryption.MaxStringLen())
        ]
        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"ChopSendCheckStart", self.ClientKey)
        )  # send chop send check start
        self.ReceiveAndDecrypt()  # receive chop send check start acknowledgement
        if not self.data == b"ChopSendCheckAcknowledged":
            return False  # chop send check failed
        i = 0
        while i < len(chunks):
            # send chunk
            self.request.sendall(
                Asymmetric_Encryption.EncryptData(
                    Asymmetric_Encryption.StringToBytes(chunks[i]), self.ClientKey
                )
            )
            self.ReceiveAndDecrypt()  # receive chunk
            # check if chunk was received correctly
            if self.data == Asymmetric_Encryption.StringToBytes(chunks[i]):
                i += 1
            else:
                # if chunk was not received correctly send chunk resend request
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"ChunkResend", self.ClientKey)
                )
                self.ReceiveAndDecrypt()  # receive chunk resend request acknowledgement
                if not self.data == b"ChunkResendAcknowledged":
                    return False  # chop send check failed

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"ChopSendCheckComplete", self.ClientKey)
        )  # send chop send check complete
        self.ReceiveAndDecrypt()  # receive chop send check complete acknowledgement
        if not self.data == b"ChopSendCheckCompleteAcknowledged":
            return False  # chop send check failed

        return True  # chop send check complete

    def ProgressChopSendCheck(self, string):
        # chop string into Asymmetric_Encryption.MaxStringLen() byte chunks and send to client (MAX is 86 theoretically based on Asymmetric_Encryption.PacketSize() bit transmission)
        chunks = [
            string[i : i + Asymmetric_Encryption.MaxStringLen()]
            for i in range(0, len(string), Asymmetric_Encryption.MaxStringLen())
        ]
        chunks.insert(0, str(len(chunks)))  # insert number of chunks at start of list

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"ChopSendCheckStart", self.ClientKey)
        )  # send chop send check start
        self.ReceiveAndDecrypt()  # receive chop send check start acknowledgement
        if not self.data == b"ChopSendCheckAcknowledged":
            return False  # chop send check failed

        i = 0
        while i < len(chunks):
            # send chunk
            self.request.sendall(
                Asymmetric_Encryption.EncryptData(
                    Asymmetric_Encryption.StringToBytes(chunks[i]), self.ClientKey
                )
            )
            self.ReceiveAndDecrypt()  # receive chunk
            # check if chunk was received correctly
            if self.data == Asymmetric_Encryption.StringToBytes(chunks[i]):
                i += 1
            else:
                # if chunk was not received correctly send chunk resend request
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"ChunkResend", self.ClientKey)
                )
                self.ReceiveAndDecrypt()  # receive chunk resend request acknowledgement
                if not self.data == b"ChunkResendAcknowledged":
                    return False  # chop send check failed

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"ChopSendCheckComplete", self.ClientKey)
        )  # send chop send check complete
        self.ReceiveAndDecrypt()  # receive chop send check complete acknowledgement
        if not self.data == b"ChopSendCheckCompleteAcknowledged":
            return False  # chop send check failed

        return True  # chop send check complete

    def ChopReceiveCheck(self):
        self.ReceiveAndDecrypt()  # receive chop send check start
        if (
            not self.data == b"ChopSendCheckStart"
        ):  # check if chop send check start was received correctly
            return False
        self.request.sendall(
            Asymmetric_Encryption.EncryptData(  # send chop send check acknowledged
                b"ChopSendCheckAcknowledged", self.ClientKey
            )
        )
        chunks = []
        while True:  # receive chunks
            self.ReceiveAndDecrypt()  # receive chunk
            if (
                self.data == b"ChopSendCheckComplete"
            ):  # check if chop send check complete was received correctly
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(  # send chop send check complete acknowledged
                        b"ChopSendCheckCompleteAcknowledged", self.ClientKey
                    )
                )
                break  # chop send check complete
            elif self.data == b"ChunkResend":  # check if chunk resend was received correctly
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(  # send chunk resend acknowledged
                        b"ChunkResendAcknowledged", self.ClientKey
                    )
                )
                chunks.pop()  # remove last chunk from list
                continue
            else:
                chunks.append(Asymmetric_Encryption.BytesToString(self.data))  # add chunk to list
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(
                        self.data, self.ClientKey
                    )  # send chunk acknowledged
                )
        return "".join(chunks)
    """

    def ArbitraryStringSend(self, string):
        """Sends an arbitrary length string over TCP as fast as possible.

        Args:
            string (str): The string to send.

        Returns:
            bool: True if the string was sent successfully, False otherwise.
        """
        chunks = [
            string[i : i + Asymmetric_Encryption.MaxStringLen()]
            for i in range(0, len(string), Asymmetric_Encryption.MaxStringLen())
        ]

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"StringSendStart", self.ClientKey)
        )  # send string send start

        # receive string send start
        data = Asymmetric_Encryption.DecryptData(
            self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
        )

        if not data == b"StringSendAcknowledged":
            return False

        for i in range(len(chunks)):
            if i % Asymmetric_Encryption.MaxBufferLen() == 0 and i != 0:
                data = Asymmetric_Encryption.DecryptData(
                    self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
                )
                if not data == b"BufferReceived":
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"CANCEL", self.ClientKey)
                    )
                    return False

            self.request.sendall(
                Asymmetric_Encryption.EncryptData(
                    Asymmetric_Encryption.StringToBytes(chunks[i]), self.ClientKey
                )
            )

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"StringSendComplete", self.ClientKey)
        )
        data = Asymmetric_Encryption.DecryptData(
            self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
        )
        if not data == b"StringSendCompleteAcknowledged":
            return False

        return True

    def ArbitraryStringReceive(self):
        """Receives an arbitrary length string over TCP as fast as possible.

        Returns:
            str: The received string. None if the string was not received successfully.
        """
        data = Asymmetric_Encryption.DecryptData(
            self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
        )
        if not data == b"StringSendStart":
            return ""

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"StringSendAcknowledged", self.ClientKey)
        )

        chunks = []
        while True:
            RawData = self.request.recv(Asymmetric_Encryption.PacketSize())
            data = Asymmetric_Encryption.DecryptData(RawData, self.PrivateKey)

            if data == b"StringSendComplete":
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(
                        b"StringSendCompleteAcknowledged", self.ClientKey
                    )
                )
                break
            elif data == b"CANCEL":
                return None
            else:
                chunks.append(Asymmetric_Encryption.BytesToString(data))

            if len(chunks) % Asymmetric_Encryption.MaxBufferLen() == 0 and len(chunks) != 0:
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"BufferReceived", self.ClientKey)
                )

        return "".join(chunks)

    def ProgressArbitraryStringSend(self, string):
        """Sends an arbitrary length string over TCP as fast as possible with progress.

        Args:
            string (str): The string to send.
        """
        chunks = [
            string[i : i + Asymmetric_Encryption.MaxStringLen()]
            for i in range(0, len(string), Asymmetric_Encryption.MaxStringLen())
        ]

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"ProgressStringSendStart", self.ClientKey)
        )  # send string send start

        # receive string send start
        data = Asymmetric_Encryption.DecryptData(
            self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
        )

        if not data == b"ProgressStringSendAcknowledged":
            return False

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(str(len(chunks))), self.ClientKey
            )
        )

        data = Asymmetric_Encryption.DecryptData(
            self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
        )

        if not data == b"AcknowledgeTotal":
            return False

        for i in range(len(chunks)):
            if i % Asymmetric_Encryption.MaxBufferLen() == 0 and i != 0:
                data = Asymmetric_Encryption.DecryptData(
                    self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
                )
                if not data == b"BufferReceived":
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"CANCEL", self.ClientKey)
                    )
                    return False

            self.request.sendall(
                Asymmetric_Encryption.EncryptData(
                    Asymmetric_Encryption.StringToBytes(chunks[i]), self.ClientKey
                )
            )

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"StringSendComplete", self.ClientKey)
        )
        data = Asymmetric_Encryption.DecryptData(
            self.request.recv(Asymmetric_Encryption.PacketSize()), self.PrivateKey
        )
        if not data == b"StringSendCompleteAcknowledged":
            return False

        return True

    def CreateOauthToken(self):
        self.AppendLog(
            "Begin Oauth Token Registration",
            str(self.client_address[0]) + " started a new Oauth Token Registration.",
        )
        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"PrepareOauth", self.ClientKey)
        )  # send prepare oauth to client to start oauth process

        self.ReceiveAndDecrypt()  # receive prepare oauth acknowledgement
        # check if prepare oauth acknowledgement was received correctly
        if not self.data == b"PrepareOauthAcknowledged":
            self.AppendLog(
                "Oauth Token Registration Failed",
                str(self.client_address[0]) + " failed to prepare for Oauth Token Registration.",
            )
            return False

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"SendShopID", self.ClientKey)  # send shop id request
        )
        self.ReceiveAndDecrypt()  # receive shop id
        self.ShopID = Asymmetric_Encryption.BytesToString(self.data)  # convert shop id to string

        try:  # check if shop id already exists
            exists = self.AccessDataBase("OauthTokens", tinydb.Query().shop_id == self.ShopID)[0]
            if exists:
                # if shop id already exists send existing oauth token message to client and close connection
                self.AppendLog(
                    "Oauth Token Registration Failed",
                    str(self.client_address[0])
                    + " failed to register a new Oauth Token because one already exists for this shop.",
                )
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"ExistingOauthToken", self.ClientKey)
                )
                return False
        except IndexError:
            pass

        APIKeyString = self.AccessDataBase(
            "Settings", tinydb.Query().setting_name == "API_Key_String"
        )[0][
            "setting_value"
        ]  # get API key string

        # ETSY required random security strings
        RandomState = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(32)
        )  # generate random state

        RandomCode = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(100)
        )  # generate random code

        # create redirect oauth object
        Oauth = AuthHelper(
            keystring=APIKeyString,
            redirect_uri="https://leboeuflasing.ddns.net",
            scopes="billing_r shops_r transactions_r",
            code_verifier=RandomCode,
            state=RandomState,
        )  # create redirect oauth object
        UserURL = Oauth.get_auth_code()[0]  # get user url to redirect to

        Success = self.ArbitraryStringSend(UserURL)  # send user url to client
        if not Success:
            self.AppendLog(
                "Oauth Token Registration Failed",
                str(self.client_address[0]) + " failed to send user url to client.",
            )
            return False
        UserURI = self.ArbitraryStringReceive()  # receive user uri from client

        try:
            # get headless uri from user uri
            HeadlessURI = UserURI.split("code=")[1]
            # get code and state from headless uri
            CodeAndState = HeadlessURI.split("&state=")
            code = CodeAndState[0]
            state = CodeAndState[1]
        except Exception as e:
            self.AppendLog(
                "Oauth Token Registration Failed",
                str(self.client_address[0]) + " failed to get code and state from user uri.",
            )
            return False

        try:
            # set code and state in oauth object
            Oauth.set_authorisation_code(code, state)
            TokenDictionary = Oauth.get_access_token()  # get token from oauth object
            # get token from token dictionary
            Token = TokenDictionary["access_token"]
            # get refresh token from token dictionary
            RefreshToken = TokenDictionary["refresh_token"]
            # get expires at from token dictionary
            ExpiresAt = TokenDictionary["expires_at"]
        except:
            self.AppendLog(
                "Oauth Token Registration Failed",
                str(self.client_address[0]) + " failed to get oauth token from Etsy.",
            )
            return False

        ClientToken = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(100)  # generate client token
        )
        # hash client token with shop id
        Hash = self.IDTokenHash(self.ShopID, ClientToken)

        self.InsertDataBase(
            "OauthTokens",
            {
                "shop_id": self.ShopID,
                "token": Token,
                "refresh_token": RefreshToken,
                "expires_at": ExpiresAt,
                "hash": Hash,
            },
        )  # insert oauth token into database

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"AuthenticationSuccess", self.ClientKey)
        )  # send authentication success to client
        self.ReceiveAndDecrypt()
        # check if authentication success acknowledgement was received correctly
        if not self.data == b"AuthenticationSuccessAcknowledged":
            self.AppendLog(
                "Oauth Token Registration Failed",
                str(self.client_address[0]) + " failed to acknowledge authentication success.",
            )
            return False

        Success = self.ArbitraryStringSend(ClientToken)  # send password to client
        if not Success:
            self.AppendLog(
                "Oauth Token Registration Failed",
                str(self.client_address[0]) + " failed to send password to client.",  # log failure
            )
            return False

        self.AppendLog(
            "Oauth Token Registration Success",
            str(self.client_address[0])  # log success
            + " successfully registered a new Oauth Token with ShopID:"
            + str(self.ShopID)
            + ".",
        )  # log success
        return True

    # get shop receipts from Etsy for a given shop id
    def GetAllShopReceipts(self, ShopID, StartNumber):
        """
        Etsy API call to get receipts for a given shop id.

        Keyword arguments:
        @param ShopID -- the shop id to get receipts for
        @param StartNumber -- the start number of the receipt range
        """
        APIKeyString = self.AccessDataBase(
            "Settings", tinydb.Query().setting_name == "API_Key_String"
        )[0][
            "setting_value"
        ]  # get API key string
        OauthTokenSet = self.AccessDataBase("OauthTokens", tinydb.Query().shop_id == ShopID)[
            0
        ]  # get oauth token set from database

        self.AppendLog(
            "Begin Receipt Retrieval",
            str(self.client_address[0])
            + " started a new Receipt Retrieval.",  # log receipt retrieval start
        )

        EtsyClient = EtsyAPI(
            keystring=APIKeyString,
            token=OauthTokenSet["token"],
            refresh_token=OauthTokenSet["refresh_token"],
            expiry=datetime.fromtimestamp(OauthTokenSet["expires_at"]),
            refresh_save=self.UpdateOauthToken,
        )  # create Etsy API client

        AllReceipts = []
        # maximum number of receipts per query (Etsy API limit)
        MaximumReceiptsPerQuery = 100
        i = StartNumber  # start at given start number for less data to process
        while True:  # loop until no more receipts
            try:
                Receipts = EtsyClient.get_shop_receipts(
                    shop_id=int(OauthTokenSet["shop_id"]),  # get receipts from Etsy
                    limit=int(MaximumReceiptsPerQuery),
                    offset=int(i),
                    was_canceled=False,
                    was_shipped=None,
                    was_paid=None,
                )
                if i >= Receipts["count"]:  # if no more receipts
                    break
                i += MaximumReceiptsPerQuery  # increment offset
                AllReceipts += Receipts["results"]  # add receipts to list
            except:
                self.AppendLog(
                    "Receipt Retrieval Failed",
                    str(self.client_address[0])
                    + " failed to retrieve Receipts from Etsy.",  # log failure
                )
                return False, None

        self.AppendLog(
            "Receipt Retrieval Success",
            str(self.client_address[0])
            + " successfully retrieved Receipts from Etsy.",  # log success
        )
        return True, AllReceipts

    def GetPartialShopReceipts(self, ShopID, EndingReceiptID):
        """
        Etsy API call to get receipts for a given shop id.

        Keyword arguments:
        @param ShopID -- the shop id to get receipts for
        @param EndingReceiptID -- the receipt id to end at (non-inclusive)
        """
        APIKeyString = self.AccessDataBase(
            "Settings", tinydb.Query().setting_name == "API_Key_String"
        )[0][
            "setting_value"
        ]  # get API key string
        OauthTokenSet = self.AccessDataBase("OauthTokens", tinydb.Query().shop_id == ShopID)[
            0
        ]  # get oauth token set from database

        self.AppendLog(
            "Begin Receipt Retrieval",
            str(self.client_address[0])
            + " started a new Receipt Retrieval.",  # log receipt retrieval start
        )

        EtsyClient = EtsyAPI(
            keystring=APIKeyString,
            token=OauthTokenSet["token"],
            refresh_token=OauthTokenSet["refresh_token"],
            expiry=datetime.fromtimestamp(OauthTokenSet["expires_at"]),
            refresh_save=self.UpdateOauthToken,
        )  # create Etsy API client

        AllReceipts = []
        # maximum number of receipts per query (Etsy API limit)
        MaximumReceiptsPerQuery = 100
        i = 0  # start at given start number for less data to process
        while True:  # loop until no more receipts
            try:
                Receipts = EtsyClient.get_shop_receipts(
                    shop_id=int(OauthTokenSet["shop_id"]),  # get receipts from Etsy
                    limit=int(MaximumReceiptsPerQuery),
                    offset=int(i),
                )
                if any(
                    R["receipt_id"] == EndingReceiptID for R in Receipts["results"]
                ):  # if ending receipt id reached
                    # remove all receipts after ending receipt id and the ending receipt id
                    for i in range(len(Receipts["results"])):
                        if Receipts["results"][i]["receipt_id"] == EndingReceiptID:
                            Receipts["results"] = Receipts["results"][
                                :i
                            ]  # remove all receipts after ending receipt id
                            Receipts["results"] = Receipts["results"][
                                :-1
                            ]  # remove ending receipt id
                            break
                    AllReceipts += Receipts["results"]  # add receipts to list
                    break
                i += MaximumReceiptsPerQuery  # increment offset
                AllReceipts += Receipts["results"]  # add receipts to list
            except:
                self.AppendLog(
                    "Receipt Retrieval Failed",
                    str(self.client_address[0])
                    + " failed to retrieve Receipts from Etsy.",  # log failure
                )
                return False, None

        self.AppendLog(
            "Receipt Retrieval Success",
            str(self.client_address[0])
            + " successfully retrieved Receipts from Etsy.",  # log success
        )
        return True, AllReceipts

    def GetShop(self, ShopID):
        """
        Etsy API call to get shop information for a given shop id.

        Keyword arguments:
        @param ShopID -- the shop id to get shop information for
        """
        APIKeyString = self.AccessDataBase(
            "Settings", tinydb.Query().setting_name == "API_Key_String"
        )[0][
            "setting_value"
        ]  # get API key string
        OauthTokenSet = self.AccessDataBase("OauthTokens", tinydb.Query().shop_id == ShopID)[
            0
        ]  # get oauth token set from database

        self.AppendLog(
            "Begin Shop Retrieval",
            str(self.client_address[0])
            + " started a new Shop Retrieval.",  # log shop retrieval start
        )

        EtsyClient = EtsyAPI(
            keystring=APIKeyString,
            token=OauthTokenSet["token"],
            refresh_token=OauthTokenSet["refresh_token"],
            expiry=datetime.fromtimestamp(OauthTokenSet["expires_at"]),
            refresh_save=self.UpdateOauthToken,
        )  # create Etsy API client

        try:
            Shop = EtsyClient.get_shop(shop_id=int(OauthTokenSet["shop_id"]))  # get shop from Etsy

        except:
            self.AppendLog(
                "Shop Retrieval Failed",
                str(self.client_address[0]) + " failed to retrieve Shop from Etsy.",  # log failure
            )
            return False, None

        self.AppendLog(
            "Shop Retrieval Success",
            str(self.client_address[0]) + " successfully retrieved Shop from Etsy.",  # log success
        )
        return True, Shop

    # update oauth token in database (Etsy API Package use only)

    def UpdateOauthToken(self, Token, RefreshToken, ExpiresAt):
        # Token must be refreshed after expiry so the package handles this automatically
        self.UpdateDataBase(
            "OauthTokens",
            tinydb.Query().shop_id == self.ShopID,
            {  # update oauth token in database
                "token": Token,
                "refresh_token": RefreshToken,
                "expires_at": datetime.timestamp(ExpiresAt),
            },
        )

        self.AppendLog(
            "Oauth Token Updated",
            str(self.client_address[0])  # log success
            + " successfully updated Oauth Token with ShopID:"
            + str(self.ShopID)
            + ".",
        )  # log success

    def AuthenticateSession(self):
        self.ReceiveAndDecrypt()  # receive shop id from client

        ShopID = Asymmetric_Encryption.BytesToString(self.data)  # get shop id from data
        self.ShopID = ShopID

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"ShopIDReceived", self.ClientKey)
        )  # send shop id received acknowledgement to client

        ClientToken = self.ArbitraryStringReceive()  # receive token from client
        if not ClientToken:  # check if token was received correctly
            self.AppendLog(
                "Authentication Failed",
                str(self.client_address[0]) + " failed to send password to server.",
            )
            return False, None

        # hash token with shop id
        Hash = self.IDTokenHash(ShopID, ClientToken)

        try:
            # get token from database with shop id and hash
            OauthTokenSet = self.AccessDataBase(
                "OauthTokens",
                (tinydb.Query().shop_id == ShopID) & (tinydb.Query().hash == Hash),
            )[0]
        except:
            self.AppendLog(
                "Authentication Failed",
                str(self.client_address[0])  # log failure
                + " failed to authenticate with ShopID:"
                + str(ShopID)
                + ".",
            )
            return False, None

        # return success and oauth token set (set not currently used. A database query is used instead because of the etsy token refresh)
        return True, OauthTokenSet

    def handle(self):
        # stop brute force attacks by limiting connections to 10x per day.
        # also acts as a simple rate limiter
        self.LogConnectIP(self.client_address[0])  # log connection ip
        Allow = self.AllowConnection(self.client_address[0])  # check if ip is allowed
        # Allow = True  # remove this line to re-enable ip limiting------
        if not Allow:
            self.AppendLog(
                "Connection Denied",
                str(self.client_address[0]) + " was denied connection to server.",  # log failure
            )
            # send connection denied message
            self.request.sendall(b"ConnectionDenied")
            return
        else:
            # send connection allowed message
            self.request.sendall(b"ConnectionAllowed")

        # generate new keys for each handshake
        self.PrivateKey, self.PublicKey = Asymmetric_Encryption.GenerateKeyPair()

        self.LoggedIn = False  # set logged in to false

        # handshake with client for secure communication
        Success, self.ClientKey = self.Handshake()
        if not Success:
            self.AppendLog(
                "Handshake Failed",
                str(self.client_address[0]) + " failed to handshake with server.",  # log failure
            )
            return

        self.AppendLog(
            "Handshake Success",
            str(self.client_address[0])
            + " successfully started a secure communication.",  # log success
        )

        self.request.sendall(
            Asymmetric_Encryption.EncryptData(b"Listening", self.ClientKey)
        )  # send listening acknowledgement to client to start sending data
        self.Action = "Listening"

        while True:
            self.ReceiveAndDecrypt()

            # close connection if client sends b''
            if self.data == b"" or self.data == b"CLOSE":
                self.AppendLog(
                    "Connection Closed",
                    str(self.client_address[0]) + " closed connection.",
                )
                return

            if self.data == b"CANCEL":
                self.Action = "Listening"
                # send listening acknowledgement to client to start sending data
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"Listening", self.ClientKey)
                )
                continue

            elif self.Action == "Listening" and self.data == b"CreateOauthToken":
                self.Action = "CreateAPIToken"
                Success = self.CreateOauthToken()  # create new oauth token
                if not Success:
                    self.Action = "Listening"
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"OauthFailed", self.ClientKey)
                    )
                    continue

            elif self.Action == "Listening" and self.data == b"AuthenticateSession":
                self.Action = "AuthenticateSession"
                # send start acknowledgement to client to start sending data
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"SendShopID", self.ClientKey)
                )
                (
                    Success,
                    self.OauthTokenSet,
                ) = self.AuthenticateSession()  # authenticate session
                if not Success:
                    self.Action = "Listening"
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"AuthenticationFailed", self.ClientKey)
                    )
                else:
                    self.LoggedIn = True
                    self.Action = "Listening"
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"AuthenticationSuccess", self.ClientKey)
                    )
                    self.AppendLog(
                        "Authentication Success",
                        str(self.client_address[0])
                        + " successfully authenticated with ShopID:"
                        + str(self.ShopID)
                        + ".",
                    )
                continue

            elif self.Action == "Listening" and self.data == b"RemoveToken" and self.LoggedIn:
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"ConfirmRemoveToken", self.ClientKey)
                )  # send confirmation to client to remove token
                self.Action = "RemoveToken"
                continue

            elif (
                self.Action == "RemoveToken"
                and self.data == b"ConfirmRemoveTokenAcknowledged"
                and self.LoggedIn
            ):
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"ResendToken", self.ClientKey)
                )
                data = self.ArbitraryStringReceive()  # receive token from client
                if not data:  # check if token was received correctly
                    self.AppendLog(
                        "Remove Token Failed",
                        str(self.client_address[0]) + " failed to send token to server.",
                    )
                    return False
                self.RemoveDataBase(
                    "OauthTokens",
                    tinydb.Query().hash == self.IDTokenHash(self.ShopID, data),
                )
                self.AppendLog(
                    "Remove Token Success",
                    str(self.client_address[0])
                    + " successfully removed token for shop ID:"
                    + str(self.ShopID)
                    + ".",
                )  # log success
                self.Action = "Listening"  # set action to listening
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"RemoveTokenSuccess", self.ClientKey)
                )  # send listening acknowledgement to client to start sending data
                continue

            elif self.Action == "Listening" and self.data == b"QueryAllReceipts" and self.LoggedIn:
                self.Action = "QueryAllReceipts"
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"QueryFloor", self.ClientKey)
                )  # send query count acknowledgement to client to start sending data
                continue

            elif self.Action == "QueryAllReceipts" and self.LoggedIn:
                LowCount = int(self.data.decode("utf-8"))
                Success, Receipts = self.GetAllShopReceipts(self.ShopID, LowCount)
                if not Success:
                    self.Action = "Listening"
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"QueryReceiptsFailed", self.ClientKey)
                    )
                    continue
                StringReceipts = json.dumps(Receipts)
                Success = self.ProgressArbitraryStringSend(StringReceipts)
                if not Success:
                    self.AppendLog(
                        "Query Receipts Failed",
                        str(self.client_address[0]) + " failed to send receipt data to server.",
                    )
                else:
                    self.AppendLog(
                        "Query Receipts Success",
                        str(self.client_address[0])
                        + " successfully queried receipts for shop ID:"
                        + str(self.ShopID)
                        + ".",
                    )  # log success
                self.Action = "Listening"

            elif self.Action == "Listening" and self.data == b"QueryReceipts" and self.LoggedIn:
                self.Action = "QueryReceipts"
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"EndID", self.ClientKey)
                )  # send query count acknowledgement to client to start sending data
                continue

            elif self.Action == "QueryReceipts" and self.LoggedIn:
                EndID = int(self.data.decode("utf-8"))
                Success, Receipts = self.GetPartialShopReceipts(self.ShopID, EndID)
                if not Success:
                    self.Action = "Listening"
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"QueryReceiptsFailed", self.ClientKey)
                    )
                    continue
                StringReceipts = json.dumps(Receipts)
                Success = self.ProgressArbitraryStringSend(StringReceipts)
                if not Success:
                    self.AppendLog(
                        "Query Receipts Failed",
                        str(self.client_address[0]) + " failed to send receipt data to server.",
                    )
                else:
                    self.AppendLog(
                        "Query Receipts Success",
                        str(self.client_address[0])
                        + " successfully queried receipts for shop ID:"
                        + str(self.ShopID)
                        + ".",
                    )  # log success
                self.Action = "Listening"

            elif self.Action == "Listening" and self.data == b"QueryShop" and self.LoggedIn:
                self.Action = "QueryShop"
                self.request.sendall(
                    Asymmetric_Encryption.EncryptData(b"PrepareQueryShop", self.ClientKey)
                )
                continue

            elif self.Action == "QueryShop" and self.LoggedIn:
                Success, Shop = self.GetShop(self.ShopID)
                if not Success:
                    self.Action = "Listening"
                    # send listening acknowledgement to client to start sending data
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"QueryShopFailed", self.ClientKey)
                    )
                    self.AppendLog(
                        "Query Shop Failed",
                        str(self.client_address[0])
                        + " failed query for shop ID:"
                        + str(self.ShopID)
                        + ".",
                    )
                    continue
                else:
                    self.AppendLog(
                        "Query Shop Success",
                        str(self.client_address[0])  # log success
                        + " successfully queried shop for shop ID:"
                        + str(self.ShopID)
                        + ".",
                    )
                    self.request.sendall(
                        Asymmetric_Encryption.EncryptData(b"QueryShopSuccess", self.ClientKey)
                    )
                StringShop = json.dumps(Shop)
                Success = self.ArbitraryStringSend(StringShop)
                if not Success:
                    self.AppendLog(
                        "Query Shop Failed",
                        str(self.client_address[0]) + " failed to receive shop data from server.",
                    )
                self.Action = "Listening"
                continue


def VerifySettings(database):
    # Verify Settings to make sure they are all there
    settings = database.table("Settings")

    MadeUpdate = False  # Flag to see if any updates were made

    if not settings.contains((tinydb.Query().setting_name == "Empty")):
        settings.insert(
            {
                "setting_name": "Empty",
                "setting_value": "Empty",
                "setting_type": "BOOLEAN",
                "setting_rank": 0,
                "process_status": "IGNORE",
            }
        )
        MadeUpdate = True

    # Version
    if not settings.contains((tinydb.Query().setting_name == "LaserOMS_Server_Version")):
        settings.insert(
            {
                "setting_name": "LaserOMS_Server_Version",
                "setting_value": "1.0.0",
                "setting_type": "STATIC",
                "setting_rank": 1,
                "process_status": "IGNORE",
            }
        )
        MadeUpdate = True
    settings.update({"setting_rank": 1}, tinydb.Query().setting_name == "LaserOMS_Server_Version")

    # API Key String for accessing the API
    if not settings.contains((tinydb.Query().setting_name == "API_Key_String")):
        settings.insert(
            {
                "setting_name": "API_Key_String",
                "setting_value": "",
                "setting_type": "TEXT",
                "setting_rank": 13,
                "process_status": "UTILIZE",
            }
        )
        MadeUpdate = True
    settings.update({"setting_rank": 13}, tinydb.Query().setting_name == "API_Key_String")

    return MadeUpdate


def RefreshAllTokens(database):
    def UpdateOauthToken(Token, RefreshToken, ExpiresAt):
        # Token must be refreshed after expiry so the package handles this automatically
        UpdateDataBase(
            "OauthTokens",
            tinydb.Query().shop_id == ShopID,
            {  # update oauth token in database
                "token": Token,
                "refresh_token": RefreshToken,
                "expires_at": datetime.timestamp(ExpiresAt),
            },
        )

        AppendLog(
            "Oauth Token Updated",
            "Refresh Service successfully updated Oauth Token with ShopID:" + str(ShopID) + ".",
        )  # log success

    def UpdateDataBase(TableName, Query, Data):
        global database
        table = database.table(TableName)  # get table
        table.update(Data, Query)  # update data

    def AppendLog(EventType, Message):  # append log to database
        global database
        table = database.table("Logs")
        table.insert(
            {
                "event_type": EventType,
                "event_message": Message,  # insert log
                "event_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event_year": datetime.now().strftime("%Y"),
                "event_month": datetime.now().strftime("%m"),
            }
        )

        # remove logs older than 1 year
        table.remove(tinydb.Query().event_year < datetime.now().strftime("%Y"))
        table.remove(
            tinydb.Query().event_year == datetime.now().strftime("%Y")
            and tinydb.Query().event_month < datetime.now().strftime("%m")
        )  # remove logs older than 1 month

    while True:
        # Refresh all tokens in database
        tokens = database.table("OauthTokens")
        settings = database.table("Settings")

        APIKeyString = settings.get(tinydb.Query().setting_name == "API_Key_String")[
            "setting_value"
        ]  # get API key string

        for token in tokens.all():
            OauthTokenSet = token
            ShopID = OauthTokenSet["shop_id"]
            EtsyClient = EtsyAPI(
                keystring=APIKeyString,
                token=OauthTokenSet["token"],
                refresh_token=OauthTokenSet["refresh_token"],
                expiry=datetime.fromtimestamp(OauthTokenSet["expires_at"]),
                refresh_save=UpdateOauthToken,
            )  # create Etsy API client
            try:
                EtsyClient.get_shop(ShopID)
                print("Refreshed token for shop id: " + str(OauthTokenSet["shop_id"]))
            except:
                print("Failed to refresh token for shop id: " + str(OauthTokenSet["shop_id"]))

        time.sleep(60 * 60 * 24 * 7)  # sleep for 1 week


# signal termination handling
def signal_handler(sig, frame):
    global database
    database.close()
    print("database closed on termination")
    exit(0)


signal.signal(signal.SIGTERM, signal_handler)

try:
    database = tinydb.TinyDB(
        os.path.join(os.path.realpath(os.path.dirname(__file__)), "../../Server.json"),
        storage=JSONStorage,
    )  # load database, don't use memory cache. It is not persistent atm.

    if VerifySettings(database):
        print("Updated Settings. Closing Server. Check Server.json for changes.")
        exit(0)

    # start refresh service
    Refresher = threading.Thread(target=RefreshAllTokens, args=(database,), daemon=True)
    Refresher.start()

    # setup server
    HOST, PORT = "", 55555  # listen on all interfaces on port 55555

    with socketserver.TCPServer((HOST, PORT), RequestHandler) as server:  # create server
        server.serve_forever()  # start server

except Exception as err:  # catch all errors
    print(traceback.format_exc())  # print error
finally:
    database.close()  # close database
    # close server if your feeling nice
    # NOT CLOSED PROPERLY RESULTS IN LOSS OF CACHED CHANGES
