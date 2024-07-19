
class Month:
    def __init__(self, number, cases):
        self.number = number
        self.cases = tuple(cases)

class Calendar:
    def __init__(self):
        self.january = Month(1, 'январь;января;январю;январь;январе;январе'.split(';'))
        self.february = Month(2, 'февраль;февраля;февралю;февраль;февралем;феврале'.split(';'))
        self.march = Month(3, 'март;марта;марту;март;мартом;марте'.split(';'))
        self.april = Month(4, 'апрель;апреля;апрелю;апрель;апрелем;апреле'.split(';'))
        self.may = Month(5, 'май;мая;маю;май;маем;мае'.split(';'))
        self.june = Month(6, 'июнь;июня;июню;июнь;июнем;июне'.split(';'))
        self.july = Month(7, 'июль;июля;июлю;июль;июлем;июле'.split(';'))
        self.august = Month(8, 'август;августа;августу;август;августом;августе'.split(';'))
        self.september = Month(9, 'сентябрь;сентября;сентябрю;сентябрь;сентябрем;сентябре'.split(';'))
        self.october = Month(10, 'октябрь;октября;октябрю;октябрь;октябрем;октябре'.split(';'))
        self.november = Month(11, 'ноябрь;ноября;ноябрю;ноябрь;ноябрем;ноябре'.split(';'))
        self.december = Month(12, 'декабрь;декабря;декабрю;декабрь;декабрем;декабре'.split(';'))
        self.monthList = [self.january, self.february, self.march, self.april, self.may, self.june, self.july,
                          self.august, self.september, self.october, self.november, self.december]

    def getMonthByNumber(self, number):
        return self.monthList[number - 1]

    def getMonthByName(self, name):
        for month in self.monthList:
            if name.lower() in month.cases:
                return month