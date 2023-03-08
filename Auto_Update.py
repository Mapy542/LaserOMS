import os
import urllib.request
import tinydb


def CheckForUpdate(app, database):
    url = "https://raw.githubusercontent.com/Mapy542/LaserOMS/main/version.txt"
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


def UpdateSoftware(app, database):
    if not CheckForUpdate(app, database):  # double check available update
        return

    # get version number
    url = "https://raw.githubusercontent.com/Mapy542/LaserOMS/main/version.txt"
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    settings = database.table('Settings')
    settings.update({'setting_value': text}, tinydb.Query(
    ).setting_name == "LaserOMS_Version")  # update version number in database

    import shutil
    folder = os.getcwd()  # delete all files in current directory
    for filename in os.listdir(folder):
        if filename == '.git':
            continue
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    import requests
    import zipfile
    import io
    r = requests.get(  # download latest version
        'https://github.com/Mapy542/LaserOMS/archive/refs/heads/main.zip')
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(folder)

    # move files from zip
    source = os.path.join(os.getcwd(), "LaserOMS-main")
    destination = os.getcwd()

    # code to move the files from sub-folder to main folder.
    files = os.listdir(source)
    for file in files:
        file_name = os.path.join(source, file)
        shutil.move(file_name, destination)
    print("Files Moved")

    # delete zip folder
    os.rmdir(source)

    # Find and install all required Packages.
    os.system("python3 -m pip install --upgrade pip")  # update pip
    try:
        with open("Packages.txt", "r") as f:
            recs = f.read()
            print(recs)
            f.close()
            packages = recs.split(',')
            for i in range(len(packages)):
                os.system("pip install --upgrade " + str(packages[i]))
    except:
        app.warn('Update Error', 'Unable to find Packages.txt')

    app.info('Update Complete',
             'LaserOMS has been updated to the latest version Restarting...')
    exit()
