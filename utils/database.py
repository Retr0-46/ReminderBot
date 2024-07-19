
import json
import os

from utils.funcs import joinPath
from utils.const import ConstObject
from utils.objects.db import User, Task

const = ConstObject()

class dbWorker():
    def __init__(self, databasePath):
        folderPath = databasePath.split('/')
        self.fileName = folderPath.pop(-1)
        self.folderPath = '/'.join(folderPath)
        if not self.isExists(): self.save({})

    def isExists(self):
        files = os.listdir(self.folderPath if len(self.folderPath) > 0 else None)
        return self.fileName in files

    def get(self):
        with open(joinPath(self.folderPath, self.fileName)) as file:
            dbData = json.load(file)
        return dbData

    def save(self, dbData):
        with open(joinPath(self.folderPath, self.fileName), 'w', encoding='utf-8') as file:
            json.dump(dbData, file, indent=4, ensure_ascii=False)

class dbLocalWorker():
    def __init__(self):
        self.db = {}

    def isUserExists(self, userId):
        return str(userId) in self.db

    def addNewUser(self, userId):
        self.db[str(userId)] = dict(lastRecognizedText=None,
                                    lastDetectedTask=None)

    def setLastRecognizedText(self, userId, text):
        self.db[str(userId)]['lastRecognizedText'] = text

    def getLastRecognizedText(self, userId):
        return self.db[str(userId)]['lastRecognizedText']

    def setLastDetectedTask(self, userId, task):
        self.db[str(userId)]['lastDetectedTask'] = task

    def getLastDetectedTask(self, userId):
        return self.db[str(userId)]['lastDetectedTask']

class dbUsersWorker(dbWorker):
    def getUserIds(self):
        dbData = self.get()
        userIds = tuple(dbData['users'].keys())
        return userIds

    def isUserExists(self, userId):
        dbData = self.get()
        return str(userId) in dbData['users']

    def addNewUser(self, userId, login, fullname, permission):
        dbData = self.get()
        newUser = dict(login=login,
                       fullname=fullname,
                       permission=permission)
        dbData['users'][str(userId)] = newUser
        self.save(dbData)

    def getUser(self, userId):
        dbData = self.get()
        dictUser = dbData['users'][str(userId)]
        user = User(str(userId), dictUser)
        return user

    def getPermissions(self):
        dbData = self.get()
        permissions = tuple(dbData['permissions'].values())
        return permissions

class dbTasksWorker(dbWorker):
    def getUserIds(self):
        dbData = self.get()
        userIds = tuple(dbData.keys())
        return userIds

    def isUserExists(self, userId):
        dbData = self.get()
        return str(userId) in dbData

    def addNewUser(self, userId):
        dbData = self.get()
        dbData[str(userId)] = []
        self.save(dbData)

    def isTaskExists(self, userId, task):
        dbData = self.get()
        userTasks = dbData[str(userId)]
        for dictTask in userTasks:
            if dictTask['date'] == task.date and dictTask['time'] == task.time:
                return True
        return False

    def addNewTask(self, userId, date, time, name):
        dbData = self.get()
        dictTask = dict(date=date,
                        time=time,
                        name=name)
        dbData[str(userId)].append(dictTask)
        self.save(dbData)

    def removeTask(self, userId, name):
        dbData = self.get()
        userTasks = dbData[str(userId)]
        needIndex = -1
        for index, dictTask in enumerate(userTasks):
            if dictTask['name'] == name:
                needIndex = index
                break
        if needIndex != -1: dbData[str(userId)].pop(needIndex)
        self.save(dbData)


    def getTasksByUser(self, userId):
        dbData = self.get()
        userTasks = tuple([Task(dictTask) for dictTask in dbData[str(userId)]])
        return userTasks

    def getTaskByDate(self, userId, date, time=None):
        dbData = self.get()
        userTasks = dbData[str(userId)]
        for dictTask in userTasks:
            if dictTask['date'] == date:
                if time is not None and dictTask['time'] != time: continue
                resultTask = Task(dictTask)
                return resultTask