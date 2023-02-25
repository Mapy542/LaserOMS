from guizero import Text, TextBox, PushButton, Window
import tinydb


def export(database):
    global finish, name, description, priority
    global window2
    tasks = database.table('Tasks')

    existing_tasks = tasks.search(tinydb.Query().task_name == name.value)
    if len(existing_tasks) != 0:
        name.value = name.value + '- Copy'
    tasks.insert({'task_name': name.value, 'task_description': description.value,
                  'task_priority': priority.value, 'process_status': 'UTILIZE'})
    window2.destroy()

def canceltask():
    global finish, name, description, priority
    global window2

    if(name.value == '' and description.value == '' and priority.value == '0'):
        window2.destroy()
    else:
        result = window2.yesno("Cancel", "Are you sure you want to cancel?")
        if result == True:
            window2.destroy()

def NewTask(main_window, database):
    global finish, name, description, priority
    global window2

    window2 = Window(main_window, title="New Task",
                     layout="grid", width=1100, height=700)
    welcome_message = Text(window2, text='Task Maker',
                           size=18, font="Times New Roman", grid=[1, 0])

    name_text = Text(window2, text='Task Name', size=15,
                     font="Times New Roman", grid=[0, 1])
    name = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    description_text = Text(window2, text='Description',
                            size=15, font="Times New Roman", grid=[0, 3])
    description = TextBox(window2, grid=[1, 3], width=60, multiline=True, height=15)
    priority_text = Text(window2, text='Priority', size=15,
                         font="Times New Roman", grid=[0, 7])
    priority = TextBox(window2, grid=[1, 7], width=10, text='0')
    # items header

    finish = PushButton(window2, command=export, text='Save', grid=[0, 19], args=[database])
    cancel = PushButton(window2, command=canceltask, text='Cancel', grid=[1, 19])

