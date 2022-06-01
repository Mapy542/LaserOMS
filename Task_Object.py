from datetime import datetime

class Task():
    def __init__(self, name = "", priority = 0, assigned_date = datetime.today().strftime('%m-%d-%Y'), discription = ""):
        self.name = name
        self.priority = priority
        self.date = assigned_date
        self.discription = discription

    def getName(self):
        return self.name

    def getPriority(self):
        return self.priority

    def getDate(self):
        return self.date

    def getStatus(self):
        return self.status

    def getNotes(self):
        return self.notes

    def getDiscription(self):
        return self.discription

    def changeDiscription(self, discription):
        self.discription = discription

    def changeDate(self, date):
        self.date = date

    def changePriority(self, priority):
        self.priority = priority

    def isOrder(self):
        return False
