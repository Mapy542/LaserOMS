import os
import urllib.request
import datetime

import tinydb


def UpdatePackages(app):
    # Find and install all required Packages.
    os.system("python3 -m pip install --upgrade pip")  # update pip
    try:
        with open(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "Packages.txt"),
            "r",
        ) as f:
            recs = f.read()
            f.close()
            packages = recs.split(",")
            for i in range(len(packages)):
                os.system("python3 -m pip install --upgrade " + str(packages[i]))
    except:
        app.warn("Update Error", "Unable to find Packages.txt")


def GetUpdateTransients(database):
    """Get the information for software updates from the database if they exist.

    Args:
        database (tinydb): The database object

    Returns:
        bool: True if there was transients data, False otherwise (No information)
        bool: True if there is a software update, False otherwise
        int: utc timestamp of the last update check
    """

    transients = database.table("Transients")

    try:
        updateAvail = transients.search(tinydb.Query().transient_name == "Update_Information")[0]
        return True, updateAvail["update_available"], updateAvail["timestamp"]
    except:
        return False, False, 0


def DoApiQuery(database):
    """Returns if an API query should be done based on the settings and past information.

    Args:
        database (tinydb): The database object

    Returns:
        bool: True if the CheckForUpdate function should be called, False otherwise
    """

    settings = database.table("Settings")
    try:
        UpdateEveryTime = settings.search(tinydb.Query().setting_name == "Update_Every_Open")[0][
            "setting_value"
        ]
    except:
        return True  # if the setting is not found, return True to check for update

    if UpdateEveryTime == "True":  # if setting to update every time is true, return True
        return True

    success, updateAvail, checkTimeStamp = GetUpdateTransients(
        database
    )  # check if there is any update information in the database

    if success and (
        updateAvail or datetime.datetime.now().timestamp() - checkTimeStamp > 86400
    ):  # if there is update information and there is an update available or it has been more than 24 hours since the last check
        return True

    return False


def ModifyUpdateTransients(database, updateAvail, version):
    """Modify the update transients in the database.

    Args:
        database (tinydb): The database object
        updateAvail (bool): True if there is an update available, False otherwise
        version (str, optional): The latest available version.
    """

    transients = database.table("Transients")
    transients.remove(tinydb.Query().transient_name == "Update_Information")

    # add new update information
    transients.insert(
        {
            "transient_name": "Update_Information",
            "update_available": updateAvail,
            "timestamp": datetime.datetime.now().timestamp(),
            "latest_version": version,
        }
    )


def CheckForUpdate(app, database):
    """Check for software updates on the github API.

    Args:
        app (GUIZero Window): The main application window
        database (tinydb): The database object

    Returns:
        bool: True if there is an update available, False otherwise (Checks against update every time setting and past info transients)
    """
    if not DoApiQuery(
        database
    ):  # check if the update should be done or not based on settings and past information
        return False

    # get version number

    url = "https://raw.githubusercontent.com/Mapy542/LaserOMS/main/version.txt"
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode("utf-8")
        VersionIdentifier = text.split(".")
        VersionIdentifier = [int(i) for i in VersionIdentifier]
    except:
        app.warn("Update Error", "Unable to connect to update server")
        return False

    settings = database.table("Settings")
    CurrentVersionString = settings.search(tinydb.Query().setting_name == "LaserOMS_Version")[0][
        "setting_value"
    ]
    CurrentVersion = CurrentVersionString.split(".")
    CurrentVersion = [int(i) for i in CurrentVersion]

    MaxCompare = len(VersionIdentifier)
    if len(CurrentVersion) < MaxCompare:
        MaxCompare = len(CurrentVersion)

    for i in range(MaxCompare):
        if VersionIdentifier[i] > CurrentVersion[i]:
            ModifyUpdateTransients(database, True, text.strip())
            return True

    ModifyUpdateTransients(database, False, text.strip())
    return False


def UpdateSoftware(app, database):
    """Update the software to the latest version from the github repository.

    Args:
        app (GUIZero Window): The main application window (for displaying messages)
        database (tinydb): The database object
    """

    # get version number (try to avoid api query)
    try:
        transients = database.table("Transients")
        version = transients.search(tinydb.Query().transient_name == "Update_Information")[0][
            "latest_version"
        ]
        settings = database.table("Settings")
        settings.update(
            {"setting_value": version}, tinydb.Query().setting_name == "LaserOMS_Version"
        )  # update version number in database
    except:
        url = "https://raw.githubusercontent.com/Mapy542/LaserOMS/main/version.txt"
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode("utf-8")
        settings = database.table("Settings")
        settings.update(
            {"setting_value": text}, tinydb.Query().setting_name == "LaserOMS_Version"
        )  # update version number in database

    import shutil

    # delete all files in current directory
    folder = os.path.realpath(os.path.dirname(__file__))
    for filename in os.listdir(folder):
        if filename == ".git":
            continue
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))

    import io
    import zipfile

    import requests

    r = requests.get(  # download latest version
        "https://github.com/Mapy542/LaserOMS/archive/refs/heads/main.zip"
    )
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(folder)

    # move files from zip
    source = os.path.join(folder, "LaserOMS-main")
    destination = folder

    # code to move the files from sub-folder to main folder.
    files = os.listdir(source)
    for file in files:
        file_name = os.path.join(source, file)
        shutil.move(file_name, destination)

    # delete zip folder
    os.rmdir(source)

    UpdatePackages(app)

    app.info(
        "Update Complete",
        "LaserOMS has been updated to the latest version Restarting...",
    )
    exit()
