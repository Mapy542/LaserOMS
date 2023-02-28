import tinydb
import mariadb
import sys


def ImportEasyCartOrders(app, database0):
    settings = database0.table('Settings')
    orders = database0.table('Orders')
    order_items = database0.table('Order_Items')

    DatabaseUsername = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Username")[0]['setting_value']
    DatabasePassword = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Password")[0]['setting_value']
    DatabaseAddress = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Address")[0]['setting_value']
    DatabaseName = settings.search(
        tinydb.Query().setting_name == "Easy_Cart_Database_Name")[0]['setting_value']
    if DatabaseAddress == '' or DatabaseUsername == '' or DatabasePassword == '' or DatabaseName == '':
        app.warn('Easy Cart Sync Error', 'Easy Cart Database Settings Not Set')
        return

    # if using MariaDB
    if settings.search(tinydb.Query().setting_name == "Easy_Cart_Database_Is_MariaDB")[0]['setting_value'] == 'True':
        try:
            conn = mariadb.connect(
                user=DatabaseUsername,
                password=DatabasePassword,
                host=DatabaseAddress,
                port=3306,
                database=DatabaseName
            )
        except mariadb.Error as e:
            app.warn("Sync Error",
                     "Error connecting to MariaDB Platform: " + str(e))
            return

        cursor = conn.cursor()  # create cursor
        cursor.execute("SELECT * FROM ec_order")  # get all orders
        data = [dict(line) for line in [zip(
            [column[0] for column in cursor.description], row) for row in cursor.fetchall()]]  # dictionary of results
        cursor.close()
        conn.close()
