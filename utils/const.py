
from utils.funcs import joinPath

class configCategoryObject:
    def __init__(self, config, nameCategory):
        self.config = config
        self.nameCategory = nameCategory

    def get(self, elm):
        return self.config.get(self.nameCategory, elm)

class Telegram(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Telegram')
        self.token = self.get('token')
        self.alias = self.get('alias')

class Data(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Data')
        self.defaultLang = self.get('defaultLang')

class Logging:
    def __init__(self):
        self.format = '%(asctime)s %(levelname)s %(message)s'

class Path:
    def __init__(self):
        self.project = joinPath('/', *__file__.split('/')[:-2])
        self.cache = joinPath(self.project, 'cache')
        self.client = joinPath(self.project, 'client')
        self.config = joinPath(self.client, 'config')
        self.lang = joinPath(self.client, 'lang')
        self.logs = joinPath(self.client, 'logs')
        self.db = joinPath(self.project, 'db')
        self.tasks = joinPath(self.db, 'tasks')
        self.users = joinPath(self.db, 'users')
        self.utils = joinPath(self.project, 'utils')
        self.demotivator = joinPath(self.utils, 'demotivator')
        self.objects = joinPath(self.utils, 'objects')

class File:
    def __init__(self):
        self.config = 'bot.ini'
        self.database = 'database.json'

class Default:
    def __init__(self):
        self.parseMode = 'HTML'

class Demotivator:
    def __init__(self):
        self.fontPath = joinPath('assets', 'Roboto-Regular.ttf')
        self.backgroundPath = joinPath('assets', 'background.png')
        self.textColor = 'white'

class Callback:
    def __init__(self):
        self.details = 'dts'
        self.demotivator = 'dmt'
        self.voice = 'voc'
        self.todo = 'tdo'
        self.listtasks = 'ltt'
        self.rtyes = 'rty'
        self.rtno = 'rtn'

class TaskDetector:
    def __init__(self):
        self.badWords = tuple('запиши;хочу;в список дел;в дела;добавь;запланируй;/add;поставь;в записки'.split(';'))
        self.prepositions = tuple('в;на;за;под;над'.split(';'))
        self.startWords = tuple('добавь;запланируй;запиши;в дела;в список дел'.split(';'))

class ConstObject:
    def __init__(self, config=None):
        if config: self.addConstFromConfig(config)
        self.path = Path()
        self.default = Default()
        self.logging = Logging()
        self.file = File()
        self.dem = Demotivator()
        self.callback = Callback()
        self.td = TaskDetector()

    def addConstFromConfig(self, config):
        self.telegram = Telegram(config)
        self.data = Data(config)