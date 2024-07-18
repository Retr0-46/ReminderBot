
class User:
    def __init__(self, userId, dictUser):
        self.userId = userId
        self.login = dictUser['login']
        self.fullname = dictUser['fullname']
        self.permission = dictUser['permission']

    def isDefault(self):
        return self.permission == 'default'

    def isAdmin(self):
        return self.permission == 'admin'

class Task:
    def __init__(self, dictTask):
        self.date = dictTask['date']
        self.time = dictTask['time']
        self.name = dictTask['name']