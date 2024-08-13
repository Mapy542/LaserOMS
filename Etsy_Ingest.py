import datetime
import json
import socket
import threading
import time
import webbrowser

import tinydb
from guizero import Text, Window

import Common
from Easy_Cart_Ingest import ImportEasyCartOrders
from Etsy_Request_Server import Asymmetric_Encryption

"""#deprecated to arbitrary string receive
def ProgressChopReceiveCheck(socket, ClientKey, PrivateKey):
    global ProgressList
    # receive chop send check start
    data = Asymmetric_Encryption.DecryptData(
        socket.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
    )
    if not data == b"ChopSendCheckStart":  # check if chop send check start was received correctly
        return False
    socket.sendall(
        Asymmetric_Encryption.EncryptData(  # send chop send check acknowledged
            b"ChopSendCheckAcknowledged", ClientKey
        )
    )
    chunks = []
    while True:  # receive chunks
        RawData = socket.recv(Asymmetric_Encryption.PacketSize())
        data = Asymmetric_Encryption.DecryptData(RawData, PrivateKey)

        # progressmarker
        if len(chunks) > 1:
            ProgressList[0] = len(chunks) - 1
            ProgressList[1] = int(chunks[0])
            # and save it in the mutable list for the other thread to read
            # this is janky but it works

        if (
            data == b"ChopSendCheckComplete"
        ):  # check if chop send check complete was received correctly
            socket.sendall(
                Asymmetric_Encryption.EncryptData(  # send chop send check complete acknowledged
                    b"ChopSendCheckCompleteAcknowledged", ClientKey
                )
            )
            break  # chop send check complete
        elif data == b"ChunkResend":  # check if chunk resend was received correctly
            socket.sendall(
                Asymmetric_Encryption.EncryptData(  # send chunk resend acknowledged
                    b"ChunkResendAcknowledged", ClientKey
                )
            )
            # remove last chunk from list
            chunks.pop()
            continue
        else:
            chunks.append(Asymmetric_Encryption.BytesToString(data))  # add chunk to list
            socket.sendall(
                Asymmetric_Encryption.EncryptData(data, ClientKey)
            )  # send chunk acknowledged

    chunks.remove(chunks[0])  # remove first chunk from list
    ProgressList[0] = ProgressList[1]  # set progress to 100% to ensure the progress bar exits
    return "".join(chunks)"""


def ProgressArbitraryStringReceive(socket, ClientKey, PrivateKey):
    """Receive arbitrary length string from server, with progress bar.

    Args:
        socket (socket): The socket connection to the server.
        ClientKey (bytes): The client's public key.
        PrivateKey (bytes): The client's private key.

        Global ProgressList:
         [0]: int: The number of packets received.
         [1]: int: The total number of packets to be received.

    Returns:
        str: The received string, or None if the receive failed.
    """

    global ProgressList

    data = Asymmetric_Encryption.DecryptData(
        socket.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
    )
    if not data == b"ProgressStringSendStart":  # check if string send start was received correctly
        return None

    socket.sendall(
        Asymmetric_Encryption.EncryptData(  # send string send acknowledged
            b"ProgressStringSendAcknowledged", ClientKey
        )
    )

    data = Asymmetric_Encryption.DecryptData(
        socket.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
    )
    ProgressList[1] = int(data)  # set total number of packets to be received

    socket.sendall(Asymmetric_Encryption.EncryptData(b"AcknowledgeTotal", ClientKey))

    chunks = []
    while True:
        RawData = socket.recv(Asymmetric_Encryption.PacketSize())

        sawd = len(RawData)

        data = Asymmetric_Encryption.DecryptData(RawData, PrivateKey)

        if data == b"StringSendComplete":
            socket.sendall(
                Asymmetric_Encryption.EncryptData(b"StringSendCompleteAcknowledged", ClientKey)
            )
            break
        elif data == b"CANCEL":
            return None
        else:
            chunks.append(Asymmetric_Encryption.BytesToString(data))

            ProgressList[0] = len(chunks)  # set number of packets received

        if len(chunks) % Asymmetric_Encryption.MaxBufferLen() == 0 and len(chunks) != 0:
            socket.sendall(Asymmetric_Encryption.EncryptData(b"BufferReceived", ClientKey))

    return "".join(chunks)


def RefreshThreadHandler(MainWindow, database):
    global ProgressList
    ProgressList = [0, 0, 0, 0]

    RefreshDaemon = threading.Thread(  # create thread to download data
        target=RefreshEtsyOrders, args=(MainWindow, database), daemon=True
    )
    RefreshDaemon.start()  # start thread

    # make progress bar
    popup = Window(MainWindow, title="Downloading Data", height=75, width=200)
    progress = Text(popup, text="Downloading Data", size=10)
    percentage = Text(popup, text="0%", size=10)
    totals = Text(popup, text="0/0", size=10)

    popup.repeat(200, UpdateProgress, args=(percentage, totals, popup))

    return


def UpdateProgress(percentage, totals, popup):
    global ProgressList
    try:
        percentage.value = str(int(ProgressList[0] / ProgressList[1] * 100)) + "%"
        totals.value = str(ProgressList[0]) + " / " + str(ProgressList[1]) + " Packets"
        if ProgressList[3] == 1:
            popup.destroy()
    except:
        pass  # things happen man but its just a ui element so who cares


def AuthenticationLoop(s, ServerKey, PrivateKey, app, settings, ShopID, Token):
    while True:
        if Token == "":  # if token is not set then set it up with the server
            app.info(
                "Etsy Oauth Initialization",
                "Request Server needs to access to Etsy Shop.",
            )
            app.info(
                "User Actionable Steps",
                '1. A web browser will open to the Etsy Oauth page. 2. Click "Allow" to allow access to your shop. 3. The Oauth page will redirect to leboeuflasing.ddns.net. User must copy the URL from the address bar and paste it into the dialog box that will appear.',
            )

            s.sendall(
                Asymmetric_Encryption.EncryptData(b"CreateOauthToken", ServerKey)
            )  # send request to server to create token

            data = Asymmetric_Encryption.DecryptData(
                s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
            )  # receive response from server

            if data == b"PrepareOauth":  # if server is ready to receive shop id
                s.sendall(Asymmetric_Encryption.EncryptData(b"PrepareOauthAcknowledged", ServerKey))
            else:
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to prepare for Oauth.",
                )
                return False

            data = Asymmetric_Encryption.DecryptData(
                s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
            )  # receive response from server
            if data == b"SendShopID":  # if server is ready to receive shop id
                s.sendall(
                    Asymmetric_Encryption.EncryptData(
                        Asymmetric_Encryption.StringToBytes(ShopID), ServerKey
                    )
                )  # send shop id to server
            else:
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to receive Shop ID.",
                )
                return False

            UserURL = Asymmetric_Encryption.ArbitraryStringReceive(
                s, ServerKey, PrivateKey
            )  # receive URL from server
            if UserURL == False:  # if URL not received
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to receive URL.",
                )
                return False

            webbrowser.open(UserURL)  # open URL in web browser

            UserURI = app.question(
                "User Actionable Steps",
                "Enter the URL from the address bar of the web browser that was opened.",
            ).strip()

            if UserURI == "":  # if user did not enter URL
                app.warn("Request Server Connection Failed", "User did not enter URL.")
                return False

            Success = Asymmetric_Encryption.ArbitraryStringSend(
                UserURI, s, ServerKey, PrivateKey
            )  # send URL to server
            if not Success:
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to receive URL.",
                )
                return False

            data = Asymmetric_Encryption.DecryptData(
                s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
            )  # receive response from server
            if data == b"AuthenticationSuccess":  # if server had a successful authentication
                s.sendall(
                    Asymmetric_Encryption.EncryptData(  # send acknowledgement to server
                        b"AuthenticationSuccessAcknowledged", ServerKey
                    )
                )

            else:
                app.warn(
                    "Request Server Connection Failed",  # if server did not have a successful authentication
                    "Request Server failed to authenticate.",
                )
                return False

            Token = Asymmetric_Encryption.ArbitraryStringReceive(
                s, ServerKey, PrivateKey
            )  # receive token from server
            if Token == False:  # if token not received
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to receive token.",
                )
                return False

            settings.upsert(
                {"setting_value": Token},
                tinydb.where("setting_name") == "Etsy_Request_Server_Token",
            )  # save token to database

            return True

        else:  # token exists so log in with it
            s.sendall(
                Asymmetric_Encryption.EncryptData(b"AuthenticateSession", ServerKey)
            )  # send request to server to authenticate

            data = Asymmetric_Encryption.DecryptData(
                s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
            )  # receive response from server
            if not data == b"SendShopID":
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to prepare for authentication.",
                )
                return False

            s.sendall(
                Asymmetric_Encryption.EncryptData(
                    Asymmetric_Encryption.StringToBytes(ShopID), ServerKey
                )
            )  # send shop id to server
            data = Asymmetric_Encryption.DecryptData(  # receive response from server
                s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
            )

            if not data == b"ShopIDReceived":
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to receive Shop ID.",
                )
                return False

            Success = Asymmetric_Encryption.ArbitraryStringSend(
                Token, s, ServerKey, PrivateKey
            )  # send token to server
            if not Success:  # if token not sent
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to receive token.",
                )
                return False

            data = Asymmetric_Encryption.DecryptData(
                s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
            )  # receive response from server
            if (
                not data == b"AuthenticationSuccess"
            ):  # if server did not have a successful authentication
                app.warn(
                    "Request Server Connection Failed",
                    "Request Server failed to authenticate.",
                )
                return False

            return True


def QueryTransactionCount(s, ServerKey, PrivateKey, app):
    # query test
    s.sendall(Asymmetric_Encryption.EncryptData(b"QueryShop", ServerKey))

    data = Asymmetric_Encryption.DecryptData(s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey)

    if not data == b"PrepareQueryShop":
        app.warn(
            "Request Server Connection Failed",
            "Request Server failed to prepare for query.",
        )
        return None

    s.sendall(
        Asymmetric_Encryption.EncryptData(  # send acknowledgement to server
            b"PrepareQueryShopAcknowledged", ServerKey
        )
    )

    data = Asymmetric_Encryption.DecryptData(s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey)
    if not data == b"QueryShopSuccess":
        app.warn(
            "Request Server Connection Failed",
            "Request Server failed to serve requested query.",
        )
        return None

    ShopString = Asymmetric_Encryption.ArbitraryStringReceive(s, ServerKey, PrivateKey)
    if ShopString == False:
        app.warn(
            "Request Server Connection Failed",
            "Request Server failed to receive shop.",
        )
        return None

    Shop = json.loads(ShopString)

    return Shop["transaction_sold_count"]


def SaveOrders(Receipts, database):  # save orders to database
    orders = database.table("Orders")
    order_items = database.table("Order_Items")

    # parse receipts
    Receipts = json.loads(Receipts)
    Receipts.reverse()  # reverse receipts so that oldest is first
    for Receipt in Receipts:
        # get receipt data
        Name = Receipt["name"]
        AddressLine1 = Receipt["first_line"]
        AddressLine2 = Receipt["second_line"]
        city = Receipt["city"]
        state = Receipt["state"]
        zip = Receipt["zip"]
        if (
            Receipt["status"].lower() == "paid"
            or Receipt["status"].lower()
            == "unpaid"  # not sure if this is a valid status because the Etsy API documentation is not clear on what values are possible
        ):
            Status = "OPEN"
        else:
            Status = "FULFILLED"
        OrderID = Receipt["receipt_id"]
        Date = datetime.datetime.fromtimestamp(Receipt["create_timestamp"]).strftime("%m-%d-%Y")

        ItemUIDs = Common.MakeUIDs(order_items, len(Receipt["transactions"]))
        count = 0
        for action in Receipt["transactions"]:
            ItemName = action["title"]
            Quantity = action["quantity"]
            UnitPrice = int(action["price"]["amount"]) / int(action["price"]["divisor"])
            order_items.insert(
                {
                    "item_UID": ItemUIDs[count],
                    "item_name": ItemName,
                    "item_quantity": Quantity,
                    "item_unit_price": UnitPrice,
                    "process_status": "UTILIZE",
                    "etsy_item": "TRUE",
                    "product_snapshot": action,
                }
            )
            count += 1

        orders.insert(
            {
                "etsy_order": "TRUE",
                "process_status": "UTILIZE",
                "order_number": str(OrderID),
                "order_date": Date,
                "order_status": Status,
                "order_name": Name,
                "order_address": AddressLine1,
                "order_address2": AddressLine2,
                "order_city": city,
                "order_state": state,
                "order_zip": zip,
                "order_items_UID": ItemUIDs,
                "etsy_snapshot": Receipt,
            }
        )

    return len(Receipts)


def SaveOrdersNoOverwrite(Receipts, database):  # save orders to database
    orders = database.table("Orders")
    order_items = database.table("Order_Items")

    # parse receipts
    Receipts = json.loads(Receipts)
    Receipts.reverse()  # reverse receipts so that oldest is first
    for Receipt in Receipts:
        # get receipt data
        Name = Receipt["name"]
        AddressLine1 = Receipt["first_line"]
        AddressLine2 = Receipt["second_line"]
        city = Receipt["city"]
        state = Receipt["state"]
        zip = Receipt["zip"]
        if (
            Receipt["status"].lower() == "paid"
            or Receipt["status"].lower()
            == "unpaid"  # not sure if this is a valid status because the Etsy API documentation is not clear on what values are possible
        ):
            Status = "OPEN"
        else:
            Status = "FULFILLED"
        OrderID = Common.MakeOrderID(orders)
        Date = datetime.datetime.fromtimestamp(Receipt["create_timestamp"]).strftime("%m-%d-%Y")

        # Check if order already exists
        if len(orders.search(tinydb.where("etsy_snapshot") == Receipt)) > 0:
            break  # will ignore this order
            # however a closed order that already exists but has changed will be added again

        ItemUIDs = Common.MakeUIDs(order_items, len(Receipt["transactions"]))
        count = 0
        for action in Receipt["transactions"]:
            ItemName = action["title"]
            Quantity = action["quantity"]
            UnitPrice = Common.MonetaryDivide(action["price"]["amount"], action["price"]["divisor"])
            order_items.insert(
                {
                    "item_UID": ItemUIDs[count],
                    "item_name": ItemName,
                    "item_quantity": Quantity,
                    "item_unit_price": UnitPrice,
                    "process_status": "UTILIZE",
                    "etsy_item": "TRUE",
                    "product_snapshot": action,
                }
            )
            count += 1

        orders.insert(
            {
                "etsy_order": "TRUE",
                "process_status": "UTILIZE",
                "order_number": str(OrderID),
                "order_date": Date,
                "order_status": Status,
                "order_name": Name,
                "order_address": AddressLine1,
                "order_address2": AddressLine2,
                "order_city": city,
                "order_state": state,
                "order_zip": zip,
                "order_items_UID": ItemUIDs,
                "etsy_snapshot": Receipt,
            }
        )

    return len(Receipts)


def RefreshEtsyOrders(app, database):
    global ProgressList
    # get etsy keys and info
    settings = database.table("Settings")

    ShopID = settings.get(tinydb.where("setting_name") == "Etsy_Shop_ID")["setting_value"]
    Token = settings.get(tinydb.where("setting_name") == "Etsy_Request_Server_Token")[
        "setting_value"
    ]
    RequestServerAddress = settings.get(
        tinydb.where("setting_name") == "Etsy_Request_Server_Address"
    )["setting_value"]

    if ShopID == "":  # if shop id is not set
        UserShopID = app.question(
            "Etsy Ingest Error",
            "Etsy Shop ID not set. Enter now or cancel to exit.",
        ).strip()
        if UserShopID == "":
            app.warn("Etsy Ingest Error", "Etsy Shop ID not set. Ingest cancelled.")
            ProgressList[3] = 1  # completed so delete progress bar
            return
        else:
            settings.upsert(
                {"setting_value": UserShopID},
                tinydb.where("setting_name") == "Etsy_Shop_ID",
            )
            ShopID = UserShopID

    orders = database.table("Orders")
    TotalEtsyOrders = orders.search(tinydb.where("etsy_order") == "TRUE")  # get all etsy orders
    OpenEtsyOrders = orders.search(
        (tinydb.where("etsy_order") == "TRUE") & (tinydb.where("order_status") == "OPEN")
    )  # get all open etsy orders

    # optimize by only getting orders that are not in the database or are open.
    # closed orders can be ignored as they probably will not be updated

    HOST = RequestServerAddress  # The server's hostname or IP address
    PORT = 55555  # The port used by the server
    (
        PrivateKey,
        PublicKey,
    ) = Asymmetric_Encryption.GenerateKeyPair()  # generate key pair

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # connect to server

        data = s.recv(Asymmetric_Encryption.PacketSize())  # receive handshake request
        if data == b"ConnectionDenied":  # if handshake request is not received
            app.warn(
                "Request Server Connection Failed",
                "Request Server denied connection. Ingest cancelled.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        Success, ServerKey = Asymmetric_Encryption.ClientHandshake(
            s, PublicKey, PrivateKey
        )  # handshake with server

        if not Success:
            app.warn(
                "Request Server Connection Failed",
                "Handshake failed, unable to communicate to server.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        # authentication loop. if token is not set, set it up, then log in
        AuthenticationSuccess = AuthenticationLoop(
            s, ServerKey, PrivateKey, app, settings, ShopID, Token
        )
        if not AuthenticationSuccess:
            ProgressList[3] = 1  # completed so delete progress bar
            return

        EarliestOpenOrderDate = datetime.datetime.now().timestamp()
        for OpenOrder in OpenEtsyOrders:  # find the earliest open order date
            if (
                datetime.datetime.strptime(OpenOrder["order_date"], "%m-%d-%Y").timestamp()
                < EarliestOpenOrderDate
            ):
                EarliestOpenOrderDate = datetime.datetime.strptime(
                    OpenOrder["order_date"], "%m-%d-%Y"
                ).timestamp()

        LatestClosedOrderDate = 0
        BestClosedOrderID = ""
        for i in range(len(TotalEtsyOrders)):  # find the latest closed order id
            if (
                datetime.datetime.strptime(TotalEtsyOrders[i]["order_date"], "%m-%d-%Y").timestamp()
                < EarliestOpenOrderDate
                and datetime.datetime.strptime(
                    TotalEtsyOrders[i]["order_date"], "%m-%d-%Y"
                ).timestamp()
                > LatestClosedOrderDate
            ):
                LatestClosedOrderDate = datetime.datetime.strptime(
                    TotalEtsyOrders[i]["order_date"], "%m-%d-%Y"
                ).timestamp()
                BestClosedOrderID = TotalEtsyOrders[i]["etsy_snapshot"]["receipt_id"]

        s.sendall(Asymmetric_Encryption.EncryptData(b"QueryReceipts", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
        )

        if not data == b"EndID":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        s.sendall(
            Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(str(BestClosedOrderID)),
                ServerKey,
            )
        )

        # get receipts
        # Receipts = ProgressChopReceiveCheck(s, ServerKey, PrivateKey) deprecated to arbitrary string receive
        Receipts = ProgressArbitraryStringReceive(s, ServerKey, PrivateKey)  # receive receipts
        if not Receipts:
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed send order data.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        orders = database.table("Orders")
        order_items = database.table("Order_Items")

        # delete items and orders
        orders.remove(
            (tinydb.where("etsy_order") == "TRUE")
            & (tinydb.where("process_status") == "UTILIZE")
            & (tinydb.where("order_status") == "OPEN")
        )

        ItemUIDsToRemove = [
            x["order_items_UID"] for x in OpenEtsyOrders
        ]  # get all order items to remove
        order_items.remove(
            tinydb.where("order_items_UID").one_of(ItemUIDsToRemove)
        )  # remove order items

        OrderCount = SaveOrdersNoOverwrite(Receipts, database)  # save orders

        ProgressList[3] = 1  # completed so delete progress bar
        transients = database.table("Transients")  # make a place to log updated orders
        transients.insert(
            {"transient_name": "Etsy_Orders_Updated", "transient_value": OrderCount}
        )  # log updated orders


def ImportAllThreadHandler(MainWindow, database):
    global ProgressList
    ProgressList = [0, 0, 0, 0]

    AllDaemon = threading.Thread(  # create thread to download data
        target=ImportAllEtsyOrders, args=(MainWindow, database), daemon=True
    )
    AllDaemon.start()  # start thread

    # make progress bar
    popup = Window(MainWindow, title="Downloading Data", height=75, width=200)
    progress = Text(popup, text="Downloading Data", size=10)
    percentage = Text(popup, text="0%", size=10)
    totals = Text(popup, text="0/0", size=10)

    popup.repeat(200, UpdateProgress, args=(percentage, totals, popup))

    return


def ImportAllEtsyOrders(app, database):
    global ProgressList
    # get etsy keys and info
    settings = database.table("Settings")

    ShopID = settings.get(tinydb.where("setting_name") == "Etsy_Shop_ID")["setting_value"]
    Token = settings.get(tinydb.where("setting_name") == "Etsy_Request_Server_Token")[
        "setting_value"
    ]
    RequestServerAddress = settings.get(
        tinydb.where("setting_name") == "Etsy_Request_Server_Address"
    )["setting_value"]

    if ShopID == "":  # if shop id is not set
        UserShopID = app.question(
            "Etsy Ingest Error", "Etsy Shop ID not set. Enter now or cancel to exit."
        ).strip()
        if UserShopID == "":
            app.warn("Etsy Ingest Error", "Etsy Shop ID not set. Ingest cancelled.")
            ProgressList[3] = 1  # completed so delete progress bar
            return
        else:
            settings.upsert(
                {"setting_value": UserShopID},
                tinydb.where("setting_name") == "Etsy_Shop_ID",
            )
            ShopID = UserShopID

    orders = database.table("Orders")

    # optimize by only getting orders that are not in the database or are open.
    # closed orders can be ignored as they probably will not be updated

    HOST = RequestServerAddress  # The server's hostname or IP address
    PORT = 55555  # The port used by the server
    PrivateKey, PublicKey = Asymmetric_Encryption.GenerateKeyPair()  # generate key pair

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # connect to server

        data = s.recv(Asymmetric_Encryption.PacketSize())  # receive handshake request
        if data == b"ConnectionDenied":  # if handshake request is not received
            app.warn(
                "Request Server Connection Failed",
                "Request Server denied connection. Ingest cancelled.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        Success, ServerKey = Asymmetric_Encryption.ClientHandshake(
            s, PublicKey, PrivateKey
        )  # handshake with server

        if not Success:
            app.warn(
                "Request Server Connection Failed",
                "Handshake failed, unable to communicate to server.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        # authentication loop. if token is not set, set it up, then log in
        AuthenticationSuccess = AuthenticationLoop(
            s, ServerKey, PrivateKey, app, settings, ShopID, Token
        )
        if not AuthenticationSuccess:
            ProgressList[3] = 1  # completed so delete progress bar
            return

        s.sendall(Asymmetric_Encryption.EncryptData(b"QueryAllReceipts", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
        )

        if not data == b"QueryFloor":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        s.sendall(
            Asymmetric_Encryption.EncryptData(Asymmetric_Encryption.StringToBytes("0"), ServerKey)
        )

        # get receipts
        # Receipts = ProgressChopReceiveCheck(s, ServerKey, PrivateKey) deprecated to arbitrary string receive
        Receipts = ProgressArbitraryStringReceive(s, ServerKey, PrivateKey)  # receive receipts
        if not Receipts:
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed send order data.",
            )
            ProgressList[3] = 1  # completed so delete progress bar
            return

        orders = database.table("Orders")
        order_items = database.table("Order_Items")

        # delete items and orders
        orders.remove(
            (tinydb.where("etsy_order") == "TRUE") & (tinydb.where("process_status") == "UTILIZE")
        )

        order_items.remove(tinydb.where("etsy_items").exists())  # remove order items

        OrderCount = SaveOrders(Receipts, database)  # save orders

        ProgressList[3] = 1  # completed so delete progress bar
        transients = database.table("Transients")  # make a place to log updated orders
        transients.insert(
            {"transient_name": "Etsy_Orders_Updated", "transient_value": OrderCount}
        )  # log updated orders


def FastAuthentication(app, database):
    # setup authentication before thread starts
    # get etsy keys and info
    settings = database.table("Settings")

    ShopID = settings.get(tinydb.where("setting_name") == "Etsy_Shop_ID")["setting_value"]
    Token = settings.get(tinydb.where("setting_name") == "Etsy_Request_Server_Token")[
        "setting_value"
    ]
    RequestServerAddress = settings.get(
        tinydb.where("setting_name") == "Etsy_Request_Server_Address"
    )["setting_value"]

    if ShopID == "":  # if shop id is not set
        UserShopID = app.question(
            "Etsy Ingest Error", "Etsy Shop ID not set. Enter now or cancel to exit."
        ).strip()
        if UserShopID == "":
            app.warn("Etsy Ingest Error", "Etsy Shop ID not set. Ingest cancelled.")
            return
        else:
            settings.upsert(
                {"setting_value": UserShopID},
                tinydb.where("setting_name") == "Etsy_Shop_ID",
            )
            ShopID = UserShopID

    # optimize by only getting orders that are not in the database or are open.
    # closed orders can be ignored as they probably will not be updated

    HOST = RequestServerAddress  # The server's hostname or IP address
    PORT = 55555  # The port used by the server
    PrivateKey, PublicKey = Asymmetric_Encryption.GenerateKeyPair()  # generate key pair

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # connect to server

        data = s.recv(Asymmetric_Encryption.PacketSize())  # receive handshake request
        if data == b"ConnectionDenied":  # if handshake request is not received
            app.warn(
                "Request Server Connection Failed",
                "Request Server denied connection. Ingest cancelled.",
            )
            return

        Success, ServerKey = Asymmetric_Encryption.ClientHandshake(
            s, PublicKey, PrivateKey
        )  # handshake with server

        if not Success:
            app.warn(
                "Request Server Connection Failed",
                "Handshake failed, unable to communicate to server.",
            )
            return

        # authentication loop. if token is not set, set it up, then log in
        AuthenticationSuccess = AuthenticationLoop(
            s, ServerKey, PrivateKey, app, settings, ShopID, Token
        )
        s.sendall(Asymmetric_Encryption.EncryptData(b"", ServerKey))
        s.close()
        if not AuthenticationSuccess:
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to authenticate.",
            )
            return False
        else:
            return True


def LocalOnlyTokenDelete(app, database):
    check = app.yesno(
        "Delete Etsy Token",
        "Delete local etsy request token? Only do this if token is not in request server.",
    )
    if not check:
        app.info("Stop Delete Etsy Token", "Etsy Authentication token delete canceled.")
        return
    DoubleCheck = app.yesno(
        "Delete Etsy Token",
        "Are you sure you want to delete the LOCAL only Etsy Authentication token? If the token is in the request server, it will not be deleted and you will not be able to recover it.",
    )
    if not DoubleCheck:
        app.info("Stop Delete Etsy Token", "Etsy Authentication token delete canceled.")
        return

    settings = database.table("Settings")
    settings.upsert(
        {"setting_value": ""},
        tinydb.where("setting_name") == "Etsy_Request_Server_Token",
    )

    app.info("Etsy Token Deleted", "LOCAL Etsy Authentication token deleted.")


def DeleteEtsyToken(app, database):
    DoubleCheck = app.yesno(
        "Delete Etsy Token", "Are you sure you want to delete the Etsy Authentication token?"
    )
    if not DoubleCheck:
        app.info("Stop Delete Etsy Token", "Etsy Authentication token delete canceled.")
        return

    # get etsy keys and info
    settings = database.table("Settings")

    ShopID = settings.get(tinydb.where("setting_name") == "Etsy_Shop_ID")["setting_value"]
    Token = settings.get(tinydb.where("setting_name") == "Etsy_Request_Server_Token")[
        "setting_value"
    ]
    RequestServerAddress = settings.get(
        tinydb.where("setting_name") == "Etsy_Request_Server_Address"
    )["setting_value"]

    if ShopID == "":  # if shop id is not set
        app.info("No Etsy Shop ID", "No Etsy Shop ID set. No action taken.")

    # optimize by only getting orders that are not in the database or are open.
    # closed orders can be ignored as they probably will not be updated

    HOST = RequestServerAddress  # The server's hostname or IP address
    PORT = 55555  # The port used by the server
    PrivateKey, PublicKey = Asymmetric_Encryption.GenerateKeyPair()  # generate key pair

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # connect to server

        data = s.recv(Asymmetric_Encryption.PacketSize())  # receive handshake request
        if data == b"ConnectionDenied":  # if handshake request is not received
            app.warn(
                "Request Server Connection Failed",
                "Request Server denied connection. Delete canceled.",
            )
            LocalOnlyTokenDelete(app, database)
            return

        Success, ServerKey = Asymmetric_Encryption.ClientHandshake(
            s, PublicKey, PrivateKey
        )  # handshake with server

        if not Success:
            app.warn(
                "Request Server Connection Failed",
                "Handshake failed, unable to communicate to server.",
            )
            LocalOnlyTokenDelete(app, database)
            return

        # authentication loop. if token is not set, set it up, then log in
        AuthenticationSuccess = AuthenticationLoop(
            s, ServerKey, PrivateKey, app, settings, ShopID, Token
        )
        if not AuthenticationSuccess:
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to authenticate.",
            )
            LocalOnlyTokenDelete(app, database)
            return

        s.sendall(Asymmetric_Encryption.EncryptData(b"RemoveToken", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
        )

        if not data == b"ConfirmRemoveToken":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for delete.",
            )
            return

        s.sendall(Asymmetric_Encryption.EncryptData(b"ConfirmRemoveTokenAcknowledged", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
        )

        if not data == b"ResendToken":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for token delete.",
            )

        success = Asymmetric_Encryption.ArbitraryStringSend(Token, s, ServerKey, PrivateKey)

        if not success:
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to receive token.",
            )

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.PacketSize()), PrivateKey
        )

        if not data == b"RemoveTokenSuccess":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to delete token.",
            )
            return

        settings.upsert(
            {"setting_value": ""},
            tinydb.where("setting_name") == "Etsy_Request_Server_Token",
        )

        app.info("Etsy Token Deleted", "Etsy Authentication token deleted.")
