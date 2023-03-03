import os
import urllib.request
import tinydb


def CheckForUpdate(app, database):
    url = "https://raw.githubusercontent.com/Mapy5542/LaserOMS/main/version.txt"
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
        VersionIdentifier = text.split('.')
        VersionIdentifier = [int(i) for i in VersionIdentifier]
    except:
        app.warn('Update Error', 'Unable to connect to update server')
        return False

    settings = database.table('Settings')
    CurrentVersionString = settings.search(
        tinydb.Query().setting_name == "LaserOMS_Version")[0]['setting_value']
    CurrentVersion = CurrentVersionString.split('.')
    CurrentVersion = [int(i) for i in CurrentVersion]

    MaxCompare = len(VersionIdentifier)
    if len(CurrentVersion) < MaxCompare:
        MaxCompare = len(CurrentVersion)

    for i in range(MaxCompare):
        if VersionIdentifier[i] > CurrentVersion[i]:
            return True

    return False
