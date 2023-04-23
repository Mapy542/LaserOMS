import tinydb
import json
import socket
import datetime
import webbrowser
from Etsy_Request_Server import Asymmetric_Encryption
import New_Order_Window


def RefreshEtsyOrders(app, database):
    # get etsy keys and info
    settings = database.table("Settings")

    ShopID = settings.get(tinydb.where("setting_name") == "Etsy_Shop_ID")[
        "setting_value"
    ]
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
            return 0
        else:
            settings.upsert(
                {"setting_value": UserShopID},
                tinydb.where("setting_name") == "Etsy_Shop_ID",
            )
            ShopID = UserShopID

    orders = database.table("Orders")
    TotalEtsyOrders = orders.search(
        tinydb.where("etsy_order") == "TRUE"
    )  # get all etsy orders
    OpenEtsyOrders = orders.search(
        (tinydb.where("etsy_order") == "TRUE")
        & (tinydb.where("order_status") == "OPEN")
    )  # get all open etsy orders

    # optimize by only getting orders that are not in the database or are open.
    # closed orders can be ignored as they probably will not be updated

    HOST = RequestServerAddress  # The server's hostname or IP address
    PORT = 55555  # The port used by the server
    PrivateKey, PublicKey = Asymmetric_Encryption.GenerateKeyPair()  # generate key pair

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # connect to server

        data = s.recv(Asymmetric_Encryption.BufferSize())  # receive handshake request
        if data == b"ConnectionDenied":  # if handshake request is not received
            app.warn(
                "Request Server Connection Failed",
                "Request Server denied connection. Ingest cancelled.",
            )
            return 0

        Success, ServerKey = Asymmetric_Encryption.ClientHandshake(
            s, PublicKey, PrivateKey
        )  # handshake with server

        if not Success:
            app.warn(
                "Request Server Connection Failed",
                "Handshake failed, unable to communicate to server.",
            )
            return 0

        # authentication loop. if token is not set, set it up, then log in
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
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server

                if data == b"PrepareOauth":  # if server is ready to receive shop id
                    s.sendall(
                        Asymmetric_Encryption.EncryptData(
                            b"PrepareOauthAcknowledged", ServerKey
                        )
                    )
                else:
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to prepare for Oauth.",
                    )
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
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
                    return 0

                UserURL = Asymmetric_Encryption.ChopReceiveCheck(
                    s, ServerKey, PrivateKey
                )  # receive URL from server
                if UserURL == False:  # if URL not received
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive URL.",
                    )
                    return 0

                webbrowser.open(UserURL)  # open URL in web browser

                UserURI = app.question(
                    "User Actionable Steps",
                    "Enter the URL from the address bar of the web browser that was opened.",
                ).strip()

                if UserURI == "":  # if user did not enter URL
                    app.warn(
                        "Request Server Connection Failed", "User did not enter URL."
                    )
                    return 0

                Success = Asymmetric_Encryption.ChopSendCheck(
                    UserURI, s, ServerKey, PrivateKey
                )  # send URL to server
                if not Success:
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive URL.",
                    )
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server
                if (
                    data == b"AuthenticationSuccess"
                ):  # if server had a successful authentication
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
                    return 0

                Token = Asymmetric_Encryption.ChopReceiveCheck(
                    s, ServerKey, PrivateKey
                )  # receive token from server
                if Token == False:  # if token not received
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive token.",
                    )
                    return 0

                settings.upsert(
                    {"setting_value": Token},
                    tinydb.where("setting_name") == "Etsy_Request_Server_Token",
                )  # save token to database

            else:  # token exists so log in with it
                s.sendall(
                    Asymmetric_Encryption.EncryptData(b"AuthenticateSession", ServerKey)
                )  # send request to server to authenticate

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server
                if not data == b"SendShopID":
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to prepare for authentication.",
                    )
                    return 0

                s.sendall(
                    Asymmetric_Encryption.EncryptData(
                        Asymmetric_Encryption.StringToBytes(ShopID), ServerKey
                    )
                )  # send shop id to server
                data = (
                    Asymmetric_Encryption.DecryptData(  # receive response from server
                        s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                    )
                )

                if not data == b"ShopIDReceived":
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive Shop ID.",
                    )
                    return 0

                Success = Asymmetric_Encryption.ChopSendCheck(
                    Token, s, ServerKey, PrivateKey
                )  # send token to server
                if not Success:  # if token not sent
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive token.",
                    )
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server
                if (
                    not data == b"AuthenticationSuccess"
                ):  # if server did not have a successful authentication
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to authenticate.",
                    )
                    return 0

                break

        # query test
        s.sendall(Asymmetric_Encryption.EncryptData(b"QueryShop", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
        )

        if not data == b"PrepareQueryShop":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            return 0

        s.sendall(
            Asymmetric_Encryption.EncryptData(  # send acknowledgement to server
                b"PrepareQueryShopAcknowledged", ServerKey
            )
        )

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
        )
        if not data == b"QueryShopSuccess":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to serve requested query.",
            )
            return 0

        ShopString = Asymmetric_Encryption.ChopReceiveCheck(s, ServerKey, PrivateKey)
        if ShopString == False:
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to receive shop.",
            )
            return 0

        Shop = json.loads(ShopString)

        TransactionCount = Shop["transaction_sold_count"]

        HighOrder = TransactionCount
        LowOrder = len(TotalEtsyOrders) - len(OpenEtsyOrders)  # update only open orders
        if LowOrder < 0:
            LowOrder = 0

        print("LowOrder: " + str(LowOrder))
        print("HighOrder: " + str(HighOrder))

        if LowOrder == HighOrder:
            return 0

        s.sendall(Asymmetric_Encryption.EncryptData(b"QueryReceipts", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
        )

        if not data == b"QueryLow":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            return 0

        s.sendall(
            Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(str(LowOrder)), ServerKey
            )
        )

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
        )

        if not data == b"QueryHigh":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            return 0

        s.sendall(
            Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(str(HighOrder)), ServerKey
            )
        )
        Receipts = Asymmetric_Encryption.ChopReceiveCheck(s, ServerKey, PrivateKey)

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

        # parse receipts
        Receipts = json.loads(Receipts)
        for Receipt in Receipts:
            # get receipt data
            Name = Receipt["name"]
            AddressLine1 = Receipt["first_line"]
            AddressLine2 = Receipt["second_line"]
            city = Receipt["city"]
            state = Receipt["state"]
            zip = Receipt["zip"]
            if Receipt["status"] == "paid":
                Status = "OPEN"
            else:
                Status = "FULFILLED"
            OrderID = New_Order_Window.MakeOrderID(orders)
            Date = datetime.datetime.fromtimestamp(
                Receipt["create_timestamp"]
            ).strftime("%m-%d-%Y")

            ItemUIDs = New_Order_Window.MakeUIDs(
                order_items, len(Receipt["transactions"])
            )
            count = 0
            for action in Receipt["transactions"]:
                Name = action["title"]
                Quantity = action["quantity"]
                UnitPrice = int(action["price"]["amount"]) / int(
                    action["price"]["divisor"]
                )
                order_items.insert(
                    {
                        "item_UID": ItemUIDs[count],
                        "item_name": Name,
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
                    "order_address1": AddressLine1,
                    "order_address2": AddressLine2,
                    "order_city": city,
                    "order_state": state,
                    "order_zip": zip,
                    "order_items_UID": ItemUIDs,
                    "etsy_snapshot": Receipt,
                }
            )

    return len(Receipts)


def ImportAllEtsyOrders(app, database):
    # get etsy keys and info
    settings = database.table("Settings")

    ShopID = settings.get(tinydb.where("setting_name") == "Etsy_Shop_ID")[
        "setting_value"
    ]
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
            return 0
        else:
            settings.upsert(
                {"setting_value": UserShopID},
                tinydb.where("setting_name") == "Etsy_Shop_ID",
            )
            ShopID = UserShopID

    HOST = RequestServerAddress  # The server's hostname or IP address
    PORT = 55555  # The port used by the server
    PrivateKey, PublicKey = Asymmetric_Encryption.GenerateKeyPair()  # generate key pair

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # connect to server

        data = s.recv(Asymmetric_Encryption.BufferSize())  # receive handshake request
        if data == b"ConnectionDenied":  # if handshake request is not received
            app.warn(
                "Request Server Connection Failed",
                "Request Server denied connection. Ingest cancelled.",
            )
            return 0

        Success, ServerKey = Asymmetric_Encryption.ClientHandshake(
            s, PublicKey, PrivateKey
        )  # handshake with server

        if not Success:
            app.warn(
                "Request Server Connection Failed",
                "Handshake failed, unable to communicate to server.",
            )
            return 0

        # authentication loop. if token is not set, set it up, then log in
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
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server

                if data == b"PrepareOauth":  # if server is ready to receive shop id
                    s.sendall(
                        Asymmetric_Encryption.EncryptData(
                            b"PrepareOauthAcknowledged", ServerKey
                        )
                    )
                else:
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to prepare for Oauth.",
                    )
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
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
                    return 0

                UserURL = Asymmetric_Encryption.ChopReceiveCheck(
                    s, ServerKey, PrivateKey
                )  # receive URL from server
                if UserURL == False:  # if URL not received
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive URL.",
                    )
                    return 0

                webbrowser.open(UserURL)  # open URL in web browser

                UserURI = app.question(
                    "User Actionable Steps",
                    "Enter the URL from the address bar of the web browser that was opened.",
                ).strip()

                if UserURI == "":  # if user did not enter URL
                    app.warn(
                        "Request Server Connection Failed", "User did not enter URL."
                    )
                    return 0

                Success = Asymmetric_Encryption.ChopSendCheck(
                    UserURI, s, ServerKey, PrivateKey
                )  # send URL to server
                if not Success:
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive URL.",
                    )
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server
                if (
                    data == b"AuthenticationSuccess"
                ):  # if server had a successful authentication
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
                    return 0

                Token = Asymmetric_Encryption.ChopReceiveCheck(
                    s, ServerKey, PrivateKey
                )  # receive token from server
                if Token == False:  # if token not received
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive token.",
                    )
                    return 0

                settings.upsert(
                    {"setting_value": Token},
                    tinydb.where("setting_name") == "Etsy_Request_Server_Token",
                )  # save token to database

            else:  # token exists so log in with it
                s.sendall(
                    Asymmetric_Encryption.EncryptData(b"AuthenticateSession", ServerKey)
                )  # send request to server to authenticate

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server
                if not data == b"SendShopID":
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to prepare for authentication.",
                    )
                    return 0

                s.sendall(
                    Asymmetric_Encryption.EncryptData(
                        Asymmetric_Encryption.StringToBytes(ShopID), ServerKey
                    )
                )  # send shop id to server
                data = (
                    Asymmetric_Encryption.DecryptData(  # receive response from server
                        s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                    )
                )

                if not data == b"ShopIDReceived":
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive Shop ID.",
                    )
                    return 0

                Success = Asymmetric_Encryption.ChopSendCheck(
                    Token, s, ServerKey, PrivateKey
                )  # send token to server
                if not Success:  # if token not sent
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to receive token.",
                    )
                    return 0

                data = Asymmetric_Encryption.DecryptData(
                    s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
                )  # receive response from server
                if (
                    not data == b"AuthenticationSuccess"
                ):  # if server did not have a successful authentication
                    app.warn(
                        "Request Server Connection Failed",
                        "Request Server failed to authenticate.",
                    )
                    return 0

                break

        # query test
        s.sendall(Asymmetric_Encryption.EncryptData(b"QueryShop", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
        )

        if not data == b"PrepareQueryShop":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            return 0

        s.sendall(
            Asymmetric_Encryption.EncryptData(  # send acknowledgement to server
                b"PrepareQueryShopAcknowledged", ServerKey
            )
        )

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
        )
        if not data == b"QueryShopSuccess":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to serve requested query.",
            )
            return 0

        ShopString = Asymmetric_Encryption.ChopReceiveCheck(s, ServerKey, PrivateKey)
        if ShopString == False:
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to receive shop.",
            )
            return 0

        Shop = json.loads(ShopString)

        TransactionCount = Shop["transaction_sold_count"]

        s.sendall(Asymmetric_Encryption.EncryptData(b"QueryReceipts", ServerKey))

        data = Asymmetric_Encryption.DecryptData(
            s.recv(Asymmetric_Encryption.BufferSize()), PrivateKey
        )
        if not data == b"QueryLow":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            return 0

        s.sendall(
            Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(str(0)), ServerKey
            )
        )
        if not data == b"QueryHigh":
            app.warn(
                "Request Server Connection Failed",
                "Request Server failed to prepare for query.",
            )
            return 0

        s.sendall(
            Asymmetric_Encryption.EncryptData(
                Asymmetric_Encryption.StringToBytes(str(TransactionCount)), ServerKey
            )
        )
        Receipts = Asymmetric_Encryption.ChopReceiveCheck(s, ServerKey, PrivateKey)

        orders = database.table("Orders")
        order_items = database.table("Order_Items")

        # delete items and orders
        orders.remove(
            (tinydb.where("etsy_order") == "TRUE")
            & (tinydb.where("process_status") == "UTILIZE")
        )
        order_items.remove(
            (tinydb.where("etsy_item") == "TRUE")
            & (tinydb.where("process_status") == "UTILIZE")
        )

        # parse receipts
        Receipts = json.loads(Receipts)
        for Receipt in Receipts:
            # get receipt data
            Name = Receipt["name"]
            AddressLine1 = Receipt["first_line"]
            AddressLine2 = Receipt["second_line"]
            city = Receipt["city"]
            state = Receipt["state"]
            zip = Receipt["zip"]
            if Receipt["status"] == "paid":
                Status = "OPEN"
            else:
                Status = "FULFILLED"
            OrderID = New_Order_Window.MakeOrderID(orders)
            Date = datetime.datetime.fromtimestamp(
                Receipt["create_timestamp"]
            ).strftime("%m-%d-%Y")

            ItemUIDs = New_Order_Window.MakeUIDs(
                order_items, len(Receipt["transactions"])
            )
            count = 0
            for action in Receipt["transactions"]:
                Name = action["title"]
                Quantity = action["quantity"]
                UnitPrice = int(action["price"]["amount"]) / int(
                    action["price"]["divisor"]
                )
                order_items.insert(
                    {
                        "item_UID": ItemUIDs[count],
                        "item_name": Name,
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
                    "order_address1": AddressLine1,
                    "order_address2": AddressLine2,
                    "order_city": city,
                    "order_state": state,
                    "order_zip": zip,
                    "order_items_UID": ItemUIDs,
                    "etsy_snapshot": Receipt,
                }
            )

    return len(Receipts)
