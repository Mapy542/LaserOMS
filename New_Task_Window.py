from guizero import Text, TextBox, PushButton, Window
import tinydb


def export():
    global finish, name, discription, priority
    global window2
    global tasks

    existing_tasks = tasks.search(tinydb.Query().task_name == name.value)
    if len(existing_tasks) != 0:
        name.value = name.value + '- Copy'
    tasks.insert({'task_name': name.value, 'task_discription': discription.value,
                  'task_priority': priority.value, 'Process_Status': 'UTILIZE'})
    window2.destroy()


def NewTask(main_window, tasks):
    global finish, name, discription, priority
    global window2

    window2 = Window(main_window, title="New Task",
                     layout="grid", width=1100, height=700)
    welcome_message = Text(window2, text='Task Maker',
                           size=18, font="Times New Roman", grid=[1, 0])

    name_text = Text(window2, text='Task Name', size=15,
                     font="Times New Roman", grid=[0, 1])
    name = TextBox(window2, grid=[1, 1], width=30)
    # shipping info
    discription_text = Text(window2, text='Discription',
                            size=15, font="Times New Roman", grid=[0, 3])
    discription = TextBox(window2, grid=[1, 3], width=60)
    prioirty_text = Text(window2, text='Priority', size=15,
                         font="Times New Roman", grid=[0, 7])
    priority = TextBox(window2, grid=[1, 7], width=10)
    # items header

    finish = PushButton(window2, command=export, text='Save', grid=[0, 19])
