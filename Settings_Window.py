from guizero import Text, TextBox, CheckBox, Combo, PushButton, ListBox, Window
from datetime import datetime
import difflib as dl
import tinydb

def VerifySettings(database):
    settings = database.table('Settings')
    MadeUpdate = False
    if not settings.search((tinydb.Query().setting_name == 'Empty')):
        settings.insert({'setting_name': 'Empty', 'setting_value': 'Empty', 'process_status': "IGNORE"})
        MadeUpdate = True
    if not settings.search((tinydb.Query().setting_name == 'Google_Sheet_Link')):
        settings.insert({'setting_name': 'Google_Sheet_Link', 'setting_value': '', 'process_status': "UTILIZE"})
        MadeUpdate = True
    return MadeUpdate


def updatevalue(database):
    global settingsvalue, settingname
    settingsdatabase = database.table('Settings')
    settingsdatabase.update({'setting_value': settingsvalue.value}, tinydb.Query().setting_name == settingname.value)
    ShowSettings(database)
    

def reset(database):
    database.drop_table('Settings')
    settings = database.table('Settings')  # Form settings table
    settings.insert({'setting_name': 'Empty', 'setting_value': 'Empty', 'process_status': "IGNORE"})
    VerifySettings(database)
    ShowSettings(database)

def save():
    global window
    window.destroy()

def ShowSettings(database):
    global listview
    settings = database.table('Settings')
    visiblesettings = settings.search(tinydb.Query().process_status == "UTILIZE")
    settingnames = []
    settingsvalues = []
    maxlengthsettingname = 0
    for i in range(len(visiblesettings)):
        settingnames.append(visiblesettings[i]['setting_name'])
        settingsvalues.append(visiblesettings[i]['setting_value'])
        if len(visiblesettings[i]['setting_name']) > maxlengthsettingname:
            maxlengthsettingname = len(visiblesettings[i]['setting_name'])
    for i in range(len(settingnames)):
        settingnames[i] = settingnames[i] + (maxlengthsettingname - len(settingnames[i])) * " "
        settingsvalues[i] = settingsvalues[i]

    listview.clear()
    for i in range(len(settingnames)):
        listview.append(settingnames[i] + " : " + settingsvalues[i])

def updatemodifier():
    global listview, settingsvalue, settingname
    settingsvalue.value = listview.value.split(" : ")[1].strip()
    settingname.value = listview.value.split(" : ")[0].strip()

def Settings(main_window, database):
    global window, listview, settingsvalue, settingname

    settings = database.table('Settings')

    window = Window(main_window, title="Settings", width=680, height=600, layout="grid")
    settingstext = Text(window, text="Settings", size=20, grid=[0, 0, 2, 1])
    listview = ListBox(window, items=[], width=400,height=200, scrollbar=True, grid=[0, 1, 4, 5], command=updatemodifier)
    listview.font = "Courier"
    
    settingname = Text(window, text="Setting Name:", grid=[0, 6, 1, 1])
    settingsvalue = TextBox(window, grid=[1, 6, 2, 1], width=30)
    submitbutton = PushButton(window, text="Update", grid=[3, 6, 1, 1], command=updatevalue, args=[database])

    resetbutton = PushButton(window, text="Reset to Defaults", grid=[0, 7, 1, 1], command=reset, args=[database])
    savebutton = PushButton(window, text="Exit", grid=[1, 7, 1, 1], command=save)
    ShowSettings(database)




    

    