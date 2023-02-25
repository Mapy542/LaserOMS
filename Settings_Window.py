from guizero import Text, TextBox, CheckBox, Combo, PushButton, ListBox, Window
from datetime import datetime
import difflib as dl
import tinydb, hashlib

def PasswordHash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def VerifySettings(database):
    settings = database.table('Settings')
    MadeUpdate = False
    if not settings.search((tinydb.Query().setting_name == 'Empty')):
        settings.insert({'setting_name': 'Empty','setting_value': 'Empty', 'setting_type': 'BOOLEAN', 'process_status': "IGNORE"})
        MadeUpdate = True
    if not settings.search((tinydb.Query().setting_name == 'Google_Sheet_Link')):
        settings.insert({'setting_name': 'Google_Sheet_Link', 'setting_value': '','setting_type': 'TEXT', 'process_status': "UTILIZE"})
        MadeUpdate = True
    if not settings.search((tinydb.Query().setting_name == 'Show_Task_Priority')):
        settings.insert({'setting_name': 'Show_Task_Priority', 'setting_value': 'True','setting_type': 'BOOLEAN', 'process_status': "UTILIZE"})
        MadeUpdate = True
    if not settings.search((tinydb.Query().setting_name == 'Settings_Password')):
        settings.insert({'setting_name': 'Settings_Password', 'setting_value': PasswordHash('admin'),'setting_type': 'PASSWORD', 'process_status': "UTILIZE"})
        MadeUpdate = True
    return MadeUpdate

def reset(window, database):
    result = window.yesno("Reset Settings", "Are you sure you want to reset settings to default values?")
    if not result:
        return
    settings = database.table('Settings')
    password = settings.search(tinydb.Query().setting_name == "Settings_Password")[0]['setting_value']
    database.drop_table('Settings')
    settings = database.table('Settings')  # Form settings table
    settings.insert({'setting_name': 'Empty',
                    'setting_value': 'Empty', 'process_status': "IGNORE"})
    settings.insert({'setting_name': 'Settings_Password', 'setting_value': password, 'setting_type': 'PASSWORD', 'process_status': "UTILIZE"})
    VerifySettings(database)
    ShowSettings(database)


def save():
    global window
    window.destroy()


def ShowSettings(database):
    global listview
    settings = database.table('Settings')
    visiblesettings = settings.search(
        tinydb.Query().process_status == "UTILIZE")
    settingnames = []
    settingsvalues = []
    maxlengthsettingname = 0
    for i in range(len(visiblesettings)):
        settingnames.append(visiblesettings[i]['setting_name'])
        settingsvalues.append(visiblesettings[i]['setting_value'])
        if len(visiblesettings[i]['setting_name']) > maxlengthsettingname:
            maxlengthsettingname = len(visiblesettings[i]['setting_name'])
    for i in range(len(settingnames)):
        settingnames[i] = settingnames[i] + \
            (maxlengthsettingname - len(settingnames[i])) * " "
        settingsvalues[i] = settingsvalues[i]

    listview.clear()
    for i in range(len(settingnames)):
        listview.append(settingnames[i] + " : " + settingsvalues[i])


def updatesetting():
    global window, listview, databaseglob
    settings = databaseglob.table('Settings')
    settingname = listview.value.split(" : ")[0].strip()
    settingvalue = listview.value.split(" : ")[1].strip()
    valuetype = settings.search(tinydb.Query().setting_name == settingname)[0]['setting_type']
    if valuetype == "BOOLEAN":
        result = window.yesno(settingname, "Change " + settingname + " from " + settingvalue + " to true/false (True:Yes, False:No)")
        if result:
            settings.update({'setting_value': "True"}, tinydb.Query().setting_name == settingname)
        else:
            settings.update({'setting_value': "False"}, tinydb.Query().setting_name == settingname)
    elif valuetype == "TEXT":
        result = window.question(settingname, "Change " + settingname + " from " + settingvalue + " to new value")
        if result:
            settings.update({'setting_value': result}, tinydb.Query().setting_name == settingname)
    elif valuetype == "PASSWORD":
        result1 = window.question("Admin Password", "Enter new password.")
        result2 = window.question("Admin Password", "Re-enter new password.")
        if result1 == result2:
            settings.update({'setting_value': PasswordHash(result1)}, tinydb.Query().setting_name == settingname)
    ShowSettings(databaseglob)

def Settings(main_window, database):
    global window, listview, databaseglob
    databaseglob = database

    window = Window(main_window, title="Settings", width=680, height=600, layout="grid")

    settings = database.table('Settings')
    password = window.question("Enter password", "Enter admin password to access settings")
    if not PasswordHash(password) == settings.search(tinydb.Query().setting_name == "Settings_Password")[0]['setting_value']:
        window.warn("Incorrect Password", "Incorrect password entered.")
        window.destroy()
        return

    settingstext = Text(window, text="Settings", size=20, grid=[0, 0, 2, 1])
    listview = ListBox(window, items=[], width=600, height=300,
                       scrollbar=True, grid=[0, 1, 4, 5])
    listview.font = "Courier"
    listview.when_double_clicked = updatesetting

    resetbutton = PushButton(window, text="Reset to Defaults", grid=[
                             0, 7, 1, 1], command=reset, args=[window, database])
    savebutton = PushButton(window, text="Exit", grid=[
                            1, 7, 1, 1], command=save)
    ShowSettings(database)
