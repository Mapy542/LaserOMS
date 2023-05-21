import mariadb
import tinydb

import Common


def ImportEasyCartOrders(app, database0):
    EasyCartOrderStatusLookup = {
        1: "Status Not Found",
        2: "FULFILLED",
        3: "OPEN",
        4: "OPEN",
        5: "OPEN",
        6: "OPEN",
        7: "FAILED",
        8: "OPEN",
        9: "FAILED",
        10: "OPEN",
        11: "FULFILLED",
        12: "OPEN",
        14: "OPEN",
        15: "OPEN",
        16: "FAILED",
        17: "FULFILLED",
        18: "FULFILLED",
        19: "FAILED",
    }

    settings = database0.table("Settings")
    orders = database0.table("Orders")
    order_items = database0.table("Order_Items")

    DatabaseUsername = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Username"
    )[0]["setting_value"]
    DatabasePassword = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Password"
    )[0]["setting_value"]
    DatabaseAddress = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Address"
    )[0]["setting_value"]
    DatabaseName = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Name"
    )[0]["setting_value"]
    if (
        DatabaseAddress == ""
        or DatabaseUsername == ""
        or DatabasePassword == ""
        or DatabaseName == ""
    ):
        app.warn("Easy Cart Sync Error", "Easy Cart Database Settings Not Set")
        return

    # if using MariaDB
    if (
        settings.search(tinydb.Query().setting_name == "Easy_Cart_Database_Is_MariaDB")[
            0
        ]["setting_value"]
        == "True"
    ):
        try:
            conn = mariadb.connect(
                user=DatabaseUsername,
                password=DatabasePassword,
                host=DatabaseAddress,
                port=3306,
                database=DatabaseName,
            )
        except mariadb.Error as e:
            app.warn("Sync Error", "Error connecting to MariaDB Platform: " + str(e))
            return

        cursor = conn.cursor()  # create cursor

        cursor.execute("SELECT * FROM ec_order")  # get all orders
        OrderData = [
            dict(line)
            for line in [
                zip([column[0] for column in cursor.description], row)
                for row in cursor.fetchall()
            ]
        ]  # dictionary of results
        for order in OrderData:
            for value in order:
                order[value] = str(order[value])

        cursor.execute("SELECT * FROM ec_orderdetail")  # get all order items
        OrderItemData = [
            dict(line)
            for line in [
                zip([column[0] for column in cursor.description], row)
                for row in cursor.fetchall()
            ]
        ]  # dictionary of results
        for OrderItem in OrderItemData:
            for value in OrderItem:
                OrderItem[value] = str(OrderItem[value])

        cursor.close()
        conn.close()

        # clear orders in tinydb
        orders.remove(
            (tinydb.where("process_status") == "UTILIZE")
            & (tinydb.where("easy_cart_order") == "TRUE")
        )
        order_items.remove(
            (tinydb.where("process_status") == "UTILIZE")
            & (tinydb.where("easy_cart_item") == "TRUE")
        )

        # transpose items to tinydb format
        OrderToItemUID = {}
        for order in OrderData:
            OrderToItemUID[order["order_id"]] = []

        for OrderItem in OrderItemData:
            ItemUID = Common.MakeUIDs(order_items, 1)[0]
            OrderToItemUID[OrderItem["order_id"]].append(ItemUID)
            DBOrderItem = {}
            DBOrderItem["item_UID"] = ItemUID
            DBOrderItem["item_name"] = OrderItem["title"]
            DBOrderItem["item_quantity"] = OrderItem["quantity"]
            DBOrderItem["item_unit_price"] = OrderItem["unit_price"]
            DBOrderItem["easy_cart_item"] = "TRUE"
            DBOrderItem["process_status"] = "UTILIZE"
            DBOrderItem["product_snapshot"] = OrderItem
            order_items.insert(DBOrderItem)

        # transpose orders to tinydb format
        for order in OrderData:
            DBOrder = {}
            DBOrder["easy_cart_order"] = "TRUE"
            DBOrder["process_status"] = "UTILIZE"

            exists = orders.contains(tinydb.where("order_id") == order["order_id"])
            if exists:
                DBOrder["order_number"] = order["order_id"] + " (DUPLICATE)"
            else:
                DBOrder["order_number"] = order["order_id"]

            DBOrder["order_name"] = (
                order["billing_first_name"] + " " + order["billing_last_name"]
            )

            DBOrder["order_address"] = order["shipping_address_line_1"]
            DBOrder["order_address2"] = order["shipping_address_line_2"]
            DBOrder["order_city"] = order["shipping_city"]
            DBOrder["order_state"] = order["shipping_state"]
            DBOrder["order_zip"] = order["shipping_zip"]

            date = order["order_date"].split(" ")[0].split("-")
            DBOrder["order_date"] = date[1] + "-" + date[2] + "-" + date[0]

            DBOrder["order_status"] = EasyCartOrderStatusLookup[
                int(order["orderstatus_id"])
            ]

            DBOrder["order_items_UID"] = OrderToItemUID[order["order_id"]]

            DBOrder["easy_cart_snapshot"] = order

            orders.insert(DBOrder)

        return len(OrderData)
