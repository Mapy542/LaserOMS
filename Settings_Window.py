import hashlib
import os
import traceback

import tinydb
from guizero import ListBox, PushButton, Text, TitleBox, Window

import Auto_Update
import Etsy_Ingest


def PasswordHash(password):  # Hashes password using sha256 into a 64 character string
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def RelativePath(path):
    return os.path.join(os.path.realpath(os.path.dirname(__file__)), path)


# Verifies that all settings are present in the database, if not, adds them
def VerifySettings(database):
    settings = database.table("Settings")

    MadeUpdate = False

    # load default settings from csv file
    try:
        with open(RelativePath("Settings.csv")) as file:
            data = file.readlines()  # read all lines and put them in a list

            SettingsNames = []

            rank = 0
            for line in data:
                if line[0] == "~":  # ignore commented lines
                    continue

                line = line.strip().split(",")  # split the line into a list of values

                name = line[0]

                SettingsNames.append(name)

                defaultValue = line[1]
                if len(defaultValue) > 0 and defaultValue[0] == "!":
                    defaultValue = defaultValue[1:]  # remove the ! from the start of the string
                    defaultValue = defaultValue.split(":")  # split the string into a list of values

                    operator = defaultValue[0]
                    value = defaultValue[1]

                    if operator == "RelativePath":
                        defaultValue = RelativePath(value)

                    if operator == "PasswordHash":
                        defaultValue = PasswordHash(value)

                settingType = line[2]

                processStatus = line[3]

                if (
                    len(settings.search(tinydb.Query().setting_name == name)) > 0
                ):  # if the setting already exists in the database, then skip its value and name update
                    modify = settings.upsert(
                        {
                            "setting_type": settingType,
                            "process_status": processStatus,
                            "setting_rank": int(rank),
                        },
                        tinydb.Query().setting_name == name,
                    )
                    rank += 1
                    continue

                modify = settings.upsert(  # insert the setting into the database
                    {
                        "setting_name": name,
                        "setting_value": defaultValue,
                        "setting_type": settingType,
                        "process_status": processStatus,
                        "setting_rank": int(rank),
                    },
                    tinydb.Query().setting_name == name,
                )

                if modify:  # if the setting was modified, then an update was made
                    MadeUpdate = True

                rank += 1  # increment the rank

            # remove settings that are no longer in the csv file
            settings.remove(~(tinydb.Query().setting_name.one_of(SettingsNames)))

    except:
        print(traceback.format_exc())

    return MadeUpdate


def TrimDatabase(app, database):  # remove excess lines from the database
    """Get rid of all excess entries in the database. Cleanup unused entries. This does not remove any data, only redundant rows.

    Args:
        app (GuiZero Window): The main window of the program.
        database (TinyDb): The database to clean.
    """

    app.warn(
        "Database Trim",
        "This will cleanup the database by removing all excess entries. This will not remove any data. It may take a while to complete.",
    )
    CleaningTotal = 0

    transients = database.table("Transients")  # clean transients table
    CleaningTotal += len(
        transients.remove(~(tinydb.Query().transient_name.one_of(["Empty"])))
    )  # remove all transients except for the empty one

    # clean orders table
    orders = database.table("Orders")
    CleaningTotal += len(
        orders.remove(~(tinydb.Query().process_status == "UTILIZE"))
    )  # remove all orders except for ones that are to be utilized

    # clean items table
    AllUtilizedItemUIDs = []
    for order in orders.all():  # get all utilized item UIDs
        AllUtilizedItemUIDs += order["order_items_UID"]

    items = database.table("Order_Items")
    CleaningTotal += len(
        items.remove(~(tinydb.Query().item_UID.one_of(AllUtilizedItemUIDs)))
    )  # remove all items except for ones that are utilized

    app.info("Database Trim", "Removed " + str(CleaningTotal) + " excess entries from database")


def reset(window, database):  # Resets settings to default values
    # Ask user if they are sure they want to reset settings
    result = window.yesno(
        "Reset Settings", "Are you sure you want to reset settings to default values?"
    )
    if not result:
        return
    settings = database.table("Settings")  # Get settings table
    password = settings.search(tinydb.Query().setting_name == "Settings_Password")[0][
        "setting_value"
    ]  # Get current password
    database.drop_table("Settings")  # Drop settings table
    settings = database.table("Settings")  # Form settings table
    settings.insert({"setting_name": "Empty", "setting_value": "Empty", "process_status": "IGNORE"})
    settings.insert(
        {
            "setting_name": "Settings_Password",
            "setting_value": password,
            "setting_type": "PASSWORD",
            "process_status": "UTILIZE",
        }
    )  # Insert password
    VerifySettings(database)  # Verify settings
    ShowSettings(database)  # Show settings


def save():  # Save settings
    global window
    window.destroy()  # Close window (settings are saved automatically on change)


def ShowSettings(database):
    global listview
    settings = database.table("Settings")  # Get settings table
    VisibleSettings = settings.search(
        tinydb.Query().process_status == "UTILIZE"
    )  # Get all settings that are to be shown
    # Sort settings by rank
    VisibleSettings = sorted(VisibleSettings, key=lambda k: k["setting_rank"])
    SettingNames = []
    SettingValues = []
    MaxSettingNameLength = 0
    for i in range(len(VisibleSettings)):  # Get longest setting name
        SettingNames.append(VisibleSettings[i]["setting_name"])
        SettingValues.append(VisibleSettings[i]["setting_value"])
        if len(VisibleSettings[i]["setting_name"]) > MaxSettingNameLength:
            MaxSettingNameLength = len(VisibleSettings[i]["setting_name"])
    for i in range(len(SettingNames)):  # Pad setting names to be the same length
        SettingNames[i] = SettingNames[i] + (MaxSettingNameLength - len(SettingNames[i])) * " "
        SettingValues[i] = SettingValues[i]

    listview.clear()
    for i in range(len(SettingNames)):  # Add settings to listview
        listview.append(SettingNames[i] + " : " + SettingValues[i])


def UpdateSetting():
    global window, listview, ForwardDataBase
    settings = ForwardDataBase.table("Settings")  # Get settings table
    SettingName = listview.value.split(" : ")[0].strip()  # Get setting name
    SettingValue = listview.value.split(" : ")[1].strip()  # Get setting value
    ValueType = settings.search(tinydb.Query().setting_name == SettingName)[0][
        "setting_type"
    ]  # Get setting type
    if (
        ValueType == "BOOLEAN"
    ):  # If setting is boolean, ask user if they want to change it to true or false
        result = window.yesno(
            SettingName,
            "Change "
            + SettingName
            + " from "
            + SettingValue
            + " to true/false (True:Yes, False:No)",
        )
        if result:  # If user wants to change to true, change to true
            settings.update({"setting_value": "True"}, tinydb.Query().setting_name == SettingName)
        else:  # If user wants to change to false, change to false
            settings.update({"setting_value": "False"}, tinydb.Query().setting_name == SettingName)
    elif ValueType == "TEXT":  # If setting is text, ask user for new value
        result = window.question(
            SettingName,
            "Change " + SettingName + " from " + SettingValue + " to new value",
        )
        if result:
            settings.update({"setting_value": result}, tinydb.Query().setting_name == SettingName)
    elif ValueType == "PASSWORD":  # If setting is password, ask user for new password twice
        result1 = window.question("Admin Password", "Enter new password.")
        result2 = window.question("Admin Password", "Re-enter new password.")
        if result1 == result2:
            settings.update(
                {"setting_value": PasswordHash(result1)},
                tinydb.Query().setting_name == SettingName,
            )
        else:  # If passwords do not match, warn user
            window.warn(
                "Passwords do not match",
                "Passwords do not match. Password not changed.",
            )
    elif ValueType == "PATH":  # If setting is path, ask user for new path
        result = window.select_file(
            title="Select file",
            folder=".",
            filetypes=[["All files", "*.*"]],
            save=False,
            filename="",
        )
        if result:
            settings.update({"setting_value": result}, tinydb.Query().setting_name == SettingName)
    elif ValueType == "COLOR":  # If setting is color, ask user for new color
        result = window.select_color(color=None)
        if result:
            settings.update({"setting_value": result}, tinydb.Query().setting_name == SettingName)
    elif ValueType == "FOLDER":  # If setting is folder, ask user for new folder path
        result = window.select_folder(title="Select folder", folder=".")
        if result:
            settings.update({"setting_value": result}, tinydb.Query().setting_name == SettingName)
    ShowSettings(ForwardDataBase)  # Show settings


def RefreshPackages():
    global window
    Auto_Update.UpdatePackages(window)


def Settings(main_window, database):  # Settings window
    global window, listview, ForwardDataBase
    ForwardDataBase = database

    window = Window(
        main_window, title="Settings", width=680, height=600, layout="grid"
    )  # Create window

    settings = database.table("Settings")  # Get settings table
    password = window.question(
        "Enter password", "Enter admin password to access settings"
    )  # Ask user for password
    if not password:  # If user does not enter password, close window
        window.destroy()
        return
    if (
        not PasswordHash(password)
        == settings.search(tinydb.Query().setting_name == "Settings_Password")[0]["setting_value"]
    ):
        # If password is incorrect, warn user
        window.warn("Incorrect Password", "Incorrect password entered.")
        window.destroy()  # Close window
        return

    SettingsText = Text(window, text="Settings", size=20, grid=[0, 0, 2, 1])  # Create text
    listview = ListBox(
        window, items=[], width=600, height=300, scrollbar=True, grid=[0, 1, 4, 5]
    )  # Create listview of settings
    # Set font to courier (Monospaced so padding works)
    listview.font = "Courier"
    # When setting is double clicked, update setting
    listview.when_double_clicked = UpdateSetting

    SettingsDiv = TitleBox(
        window, text="Settings", grid=[0, 6, 2, 1], layout="grid"
    )  # Create title box

    ResetButton = PushButton(
        SettingsDiv,
        text="Reset to Defaults",
        grid=[1, 0, 1, 1],
        command=reset,
        args=[window, database],
    )  # Create reset button
    SaveButton = PushButton(
        SettingsDiv, text="Exit", grid=[0, 0, 1, 1], command=save
    )  # Create save button

    SynchronizeDiv = TitleBox(
        window, text="Synchronize", grid=[0, 7, 3, 1], layout="grid"
    )  # Create title box

    RefreshPackagesButton = PushButton(
        SynchronizeDiv,
        text="Refresh Packages",
        grid=[1, 0, 1, 1],
        command=RefreshPackages,
    )  # Create refresh packages button

    """UpdateAllOrdersButton = PushButton(
        SynchronizeDiv,
        text="Update All Orders",
        grid=[0, 0, 1, 1],
        command=Etsy_Ingest.SyncAllOrders,
        args=[window, database],
    )"""  # main window button does the same thing

    DeleteEtsyTokenButton = PushButton(
        SynchronizeDiv,
        text="Delete Etsy Token",
        grid=[0, 0, 1, 1],
        command=Etsy_Ingest.DeleteEtsyToken,
        args=[window, database],
    )

    TrimDatabaseButton = PushButton(
        SynchronizeDiv,
        text="Trim Database",
        grid=[2, 0, 1, 1],
        command=TrimDatabase,
        args=[window, database],
    )

    ShowSettings(database)  # Show settings
