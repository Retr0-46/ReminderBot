
import datetime

import pytz

from utils.const import ConstObject
from utils.calendar import Calendar

const = ConstObject()
calendar = Calendar()

class Task:
    def __init__(self, date, time, name):
        self.date = date
        self.time = time
        self.name = name

    def __str__(self):
        return f'{self.date} | {self.time} | {self.name}'

def getDetectedTask(text, timezone: pytz.timezone):
    string = text.lower()
    if any(word in string[:30] for word in const.td.badWords):
        for word in const.td.badWords:
            string = string.replace(word, '', 1)
    currentDate = datetime.datetime.now(timezone)
    nextDayDate = currentDate + datetime.timedelta(days=1)
    next2xDayDate = currentDate + datetime.timedelta(days=2)
    nameMonthCurrentDay = calendar.getMonthByNumber(currentDate.month).cases[1]
    nameMonthNextDay = calendar.getMonthByNumber(nextDayDate.month).cases[1]
    nameMonthNext2xDay = calendar.getMonthByNumber(next2xDayDate.month).cases[1]
    string = string.replace('сегодня', f'{currentDate.day} {nameMonthCurrentDay}')
    string = string.replace('завтра', f'{nextDayDate.day} {nameMonthNextDay}')
    string = string.replace('послезавтра', f'{next2xDayDate.day} {nameMonthNext2xDay}')
    stringList = string.split(maxsplit=3)
    for prep in const.td.prepositions:
        for i in range(3):
            if stringList[i] in prep:
                string = string.replace(prep, '', 1)
                stringList = string.split(maxsplit=3)
    resultMonth = calendar.getMonthByName(stringList[1])
    date = f'{stringList[0]}.{resultMonth.number}'
    time = stringList[2]
    name = stringList[3]
    resultTask = Task(date, time, name)
    return resultTask

