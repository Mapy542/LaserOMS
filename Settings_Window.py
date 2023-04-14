from guizero import Text, PushButton, ListBox, Window
import tinydb
import hashlib
import os


def PasswordHash(password):  # Hashes password using sha256 into a 64 character string
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Verifies that all settings are present in the database, if not, adds them
def VerifySettings(database):
    settings = database.table('Settings')
    MadeUpdate = False
    if not settings.contains((tinydb.Query().setting_name == 'Empty')):
        settings.insert({'setting_name': 'Empty', 'setting_value': 'Empty',
                        'setting_type': 'BOOLEAN', 'setting_rank': 0, 'process_status': "IGNORE"})
        MadeUpdate = True

    # Version
    if not settings.contains((tinydb.Query().setting_name == 'LaserOMS_Version')):
        settings.insert({'setting_name': 'LaserOMS_Version', 'setting_value': '1.0.0',
                        'setting_type': 'STATIC', 'setting_rank': 1, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 1},
                    tinydb.Query().setting_name == 'LaserOMS_Version')

    # Product Sync Settings
    if not settings.contains((tinydb.Query().setting_name == 'Google_Sheet_Link')):
        settings.insert({'setting_name': 'Google_Sheet_Link', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 2, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 2},
                    tinydb.Query().setting_name == 'Google_Sheet_Link')

    # Main Visual Settings
    if not settings.contains((tinydb.Query().setting_name == 'Show_Task_Priority')):
        settings.insert({'setting_name': 'Show_Task_Priority', 'setting_value': 'True',
                        'setting_type': 'BOOLEAN', 'setting_rank': 3, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 3}, tinydb.Query(
    ).setting_name == 'Show_Task_Priority')

    # Images
    if not settings.contains((tinydb.Query().setting_name == 'Images_Folder_Path')):
        settings.insert({'setting_name': 'Images_Folder_Path', 'setting_value': os.path.join(os.path.realpath(os.path.dirname(__file__)),
                                                                                             '../LaserOMS_Images'),
                        'setting_type': 'FOLDER', 'setting_rank': 4, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 4}, tinydb.Query(
    ).setting_name == 'Images_Folder_Path')

    # Settings Password
    if not settings.contains((tinydb.Query().setting_name == 'Settings_Password')):
        settings.insert({'setting_name': 'Settings_Password', 'setting_value': PasswordHash(
            'admin'), 'setting_type': 'PASSWORD', 'setting_rank': 5, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 5},
                    tinydb.Query().setting_name == 'Settings_Password')

    # Easy Cart Settings
    if not settings.contains((tinydb.Query().setting_name == 'Synchronize_Easy_Cart')):
        settings.insert({'setting_name': 'Synchronize_Easy_Cart', 'setting_value': 'False',
                        'setting_type': 'BOOLEAN', 'setting_rank': 6, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 6}, tinydb.Query(
    ).setting_name == 'Synchronize_Easy_Cart')
    if not settings.contains((tinydb.Query().setting_name == 'Easy_Cart_Database_Is_MariaDB')):
        settings.insert({'setting_name': 'Easy_Cart_Database_Is_MariaDB', 'setting_value': 'True',
                        'setting_type': 'BOOLEAN', 'setting_rank': 7, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 7}, tinydb.Query(
    ).setting_name == 'Easy_Cart_Database_Is_MariaDB')
    if not settings.contains((tinydb.Query().setting_name == 'Easy_Cart_Database_Address')):
        settings.insert({'setting_name': 'Easy_Cart_Database_Address', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 8, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 8}, tinydb.Query(
    ).setting_name == 'Easy_Cart_Database_Address')
    if not settings.contains((tinydb.Query().setting_name == 'Easy_Cart_Database_Username')):
        settings.insert({'setting_name': 'Easy_Cart_Database_Username', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 9, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 9}, tinydb.Query(
    ).setting_name == 'Easy_Cart_Database_Username')
    if not settings.contains((tinydb.Query().setting_name == 'Easy_Cart_Database_Password')):
        settings.insert({'setting_name': 'Easy_Cart_Database_Password', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 10, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 10}, tinydb.Query(
    ).setting_name == 'Easy_Cart_Database_Password')
    if not settings.contains((tinydb.Query().setting_name == 'Easy_Cart_Database_Name')):
        settings.insert({'setting_name': 'Easy_Cart_Database_Name', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 11, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 11}, tinydb.Query(
    ).setting_name == 'Easy_Cart_Database_Name')

    # Etsy Settings
    if not settings.contains((tinydb.Query().setting_name == 'Synchronize_Etsy')):
        settings.insert({'setting_name': 'Synchronize_Etsy', 'setting_value': 'False',
                        'setting_type': 'BOOLEAN', 'setting_rank': 12, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 12},
                    tinydb.Query().setting_name == 'Synchronize_Etsy')
    if not settings.contains((tinydb.Query().setting_name == 'Etsy_Request_Server_Address')):
        settings.insert({'setting_name': 'Etsy_Request_Server_Address', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 13, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 13}, tinydb.Query(
    ).setting_name == 'Etsy_Request_Server_Address')
    if not settings.contains((tinydb.Query().setting_name == 'Etsy_Request_Server_Token')):
        settings.insert({'setting_name': 'Etsy_Request_Server_Token', 'setting_value': '',
                        'setting_type': 'STATIC', 'setting_rank': 14, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 14}, tinydb.Query(
    ).setting_name == 'Etsy_Request_Server_Token')
    if not settings.contains((tinydb.Query().setting_name == 'Etsy_Shop_ID')):
        settings.insert({'setting_name': 'Etsy_Shop_ID', 'setting_value': '',
                        'setting_type': 'TEXT', 'setting_rank': 17, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 17}, tinydb.Query(
    ).setting_name == 'Etsy_Shop_ID')

    # Packing Slip Settings
    if not settings.contains((tinydb.Query().setting_name == 'Packing_Slip_Text_Color')):
        settings.insert({'setting_name': 'Packing_Slip_Text_Color', 'setting_value': '#000000',
                        'setting_type': 'COLOR', 'setting_rank': 18, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 18}, tinydb.Query(
    ).setting_name == 'Packing_Slip_Text_Color')
    if not settings.contains((tinydb.Query().setting_name == 'Packing_Slip_Background_Path')):
        settings.insert({'setting_name': 'Packing_Slip_Background_Path', 'setting_value': '',
                        'setting_type': 'PATH', 'setting_rank': 19, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 19}, tinydb.Query(
    ).setting_name == 'Packing_Slip_Background_Path')
    if not settings.contains((tinydb.Query().setting_name == 'Packing_Slip_Include_Prices')):
        settings.insert({'setting_name': 'Packing_Slip_Include_Prices', 'setting_value': 'True',
                        'setting_type': 'BOOLEAN', 'setting_rank': 20, 'process_status': "UTILIZE"})
        MadeUpdate = True
    settings.update({'setting_rank': 20}, tinydb.Query(
    ).setting_name == 'Packing_Slip_Include_Prices')


    # Expense and Financial Settings
    if not settings.contains((tinydb.Query().setting_name == 'Show_Expenses_Without_Image_Verification')):
        settings.insert({'setting_name': 'Show_Expenses_Without_Image_Verification', 'setting_value': 'True',
                        'setting_type': 'BOOLEAN', 'setting_rank': 21, 'process_status': "UTILIZE"})
    settings.update({'setting_rank': 20}, tinydb.Query(
    ).setting_name == 'Show_Expenses_Without_Image_Verification')
        MadeUpdate = True


    return MadeUpdate


def reset(window, database):  # Resets settings to default values
    # Ask user if they are sure they want to reset settings
    result = window.yesno(
        "Reset Settings", "Are you sure you want to reset settings to default values?")
    if not result:
        return
    settings = database.table('Settings')  # Get settings table
    password = settings.search(tinydb.Query().setting_name == "Settings_Password")[
        0]['setting_value']  # Get current password
    database.drop_table('Settings')  # Drop settings table
    settings = database.table('Settings')  # Form settings table
    settings.insert({'setting_name': 'Empty',
                    'setting_value': 'Empty', 'process_status': "IGNORE"})
    settings.insert({'setting_name': 'Settings_Password', 'setting_value': password,
                    'setting_type': 'PASSWORD', 'process_status': "UTILIZE"})  # Insert password
    VerifySettings(database)  # Verify settings
    ShowSettings(database)  # Show settings


def save():  # Save settings
    global window
    window.destroy()  # Close window (settings are saved automatically on change)


def ShowSettings(database):
    global listview
    settings = database.table('Settings')  # Get settings table
    VisibleSettings = settings.search(
        tinydb.Query().process_status == "UTILIZE")  # Get all settings that are to be shown
    # Sort settings by rank
    VisibleSettings = sorted(VisibleSettings, key=lambda k: k['setting_rank'])
    SettingNames = []
    SettingValues = []
    MaxSettingNameLength = 0
    for i in range(len(VisibleSettings)):  # Get longest setting name
        SettingNames.append(VisibleSettings[i]['setting_name'])
        SettingValues.append(VisibleSettings[i]['setting_value'])
        if len(VisibleSettings[i]['setting_name']) > MaxSettingNameLength:
            MaxSettingNameLength = len(VisibleSettings[i]['setting_name'])
    for i in range(len(SettingNames)):  # Pad setting names to be the same length
        SettingNames[i] = SettingNames[i] + \
            (MaxSettingNameLength - len(SettingNames[i])) * " "
        SettingValues[i] = SettingValues[i]

    listview.clear()
    for i in range(len(SettingNames)):  # Add settings to listview
        listview.append(SettingNames[i] + " : " + SettingValues[i])


def UpdateSetting():
    global window, listview, ForwardDataBase
    settings = ForwardDataBase.table('Settings')  # Get settings table
    SettingName = listview.value.split(" : ")[0].strip()  # Get setting name
    SettingValue = listview.value.split(" : ")[1].strip()  # Get setting value
    ValueType = settings.search(tinydb.Query().setting_name == SettingName)[
        0]['setting_type']  # Get setting type
    if ValueType == "BOOLEAN":  # If setting is boolean, ask user if they want to change it to true or false
        result = window.yesno(SettingName, "Change " + SettingName +
                              " from " + SettingValue + " to true/false (True:Yes, False:No)")
        if result:  # If user wants to change to true, change to true
            settings.update({'setting_value': "True"},
                            tinydb.Query().setting_name == SettingName)
        else:  # If user wants to change to false, change to false
            settings.update({'setting_value': "False"},
                            tinydb.Query().setting_name == SettingName)
    elif ValueType == "TEXT":  # If setting is text, ask user for new value
        result = window.question(
            SettingName, "Change " + SettingName + " from " + SettingValue + " to new value")
        if result:
            settings.update({'setting_value': result},
                            tinydb.Query().setting_name == SettingName)
    elif ValueType == "PASSWORD":  # If setting is password, ask user for new password twice
        result1 = window.question("Admin Password", "Enter new password.")
        result2 = window.question("Admin Password", "Re-enter new password.")
        if result1 == result2:
            settings.update({'setting_value': PasswordHash(result1)},
                            tinydb.Query().setting_name == SettingName)
        else:  # If passwords do not match, warn user
            window.warn("Passwords do not match",
                        "Passwords do not match. Password not changed.")
    elif ValueType == "PATH":  # If setting is path, ask user for new path
        result = window.select_file(title="Select file", folder=".", filetypes=[
                                    ["All files", "*.*"]], save=False, filename="")
        if result:
            settings.update({'setting_value': result},
                            tinydb.Query().setting_name == SettingName)
    elif ValueType == "COLOR":  # If setting is color, ask user for new color
        result = window.select_color(color=None)
        if result:
            settings.update({'setting_value': result},
                            tinydb.Query().setting_name == SettingName)
    elif ValueType == "FOLDER":  # If setting is folder, ask user for new folder path
        result = window.select_folder(title="Select folder", folder=".")
        if result:
            settings.update({'setting_value': result},
                            tinydb.Query().setting_name == SettingName)
    ShowSettings(ForwardDataBase)  # Show settings


def Settings(main_window, database):  # Settings window
    global window, listview, ForwardDataBase
    ForwardDataBase = database

    window = Window(main_window, title="Settings", width=680,
                    height=600, layout="grid")  # Create window

    settings = database.table('Settings')  # Get settings table
    password = window.question(
        "Enter password", "Enter admin password to access settings")  # Ask user for password
    if not password:  # If user does not enter password, close window
        window.destroy()
        return
    if not PasswordHash(password) == settings.search(tinydb.Query().setting_name == "Settings_Password")[0]['setting_value']:
        # If password is incorrect, warn user
        window.warn("Incorrect Password", "Incorrect password entered.")
        window.destroy()  # Close window
        return

    SettingsText = Text(window, text="Settings", size=20,
                        grid=[0, 0, 2, 1])  # Create text
    listview = ListBox(window, items=[], width=600, height=300,
                       scrollbar=True, grid=[0, 1, 4, 5])  # Create listview of settings
    # Set font to courier (Monospaced so padding works)
    listview.font = "Courier"
    # When setting is double clicked, update setting
    listview.when_double_clicked = UpdateSetting

    ResetButton = PushButton(window, text="Reset to Defaults", grid=[
                             0, 7, 1, 1], command=reset, args=[window, database])  # Create reset button
    SaveButton = PushButton(window, text="Exit", grid=[
                            1, 7, 1, 1], command=save)  # Create save button
    ShowSettings(database)  # Show settings
