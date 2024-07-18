
from traceback import format_exc
import datetime
import asyncio
import logging
import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram import F

from utils.const import ConstObject
from utils.funcs import joinPath, getConfigObject, getLogFileName
from utils.database import dbUsersWorker, dbTasksWorker, dbLocalWorker
from utils.objects.client import UserInfo, CallbackUserInfo
from utils.demotivator.main import getDemotivator
from utils.recognizer.main import recognizeTextByAudio
from utils.task.main import getDetectedTask

const = ConstObject()
botConfig = getConfigObject(joinPath(const.path.config, const.file.config))
const.addConstFromConfig(botConfig)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO, filename=joinPath(const.path.logs, getLogFileName()), filemode='w', format=const.logging.format)
dbUsers = dbUsersWorker(joinPath(const.path.users, const.file.database))
dbTasks = dbTasksWorker(joinPath(const.path.tasks, const.file.database))
dbLocal = dbLocalWorker()
bot = Bot(const.telegram.token, default=DefaultBotProperties(parse_mode=const.default.parseMode))
dp = Dispatcher()


def getTranslation(userInfo, key, inserts=[]):
    user = dbUsers.getUser(userInfo.userId)
    try:
        with open(joinPath(const.path.lang, f'{const.data.defaultLang}.json'), encoding='utf-8') as langFile:
            langJson = json.load(langFile)
        text = langJson[key]
        if not inserts: return text
        for ins in inserts: text = text.replace('%{}%', str(ins), 1)
        return text
    except Exception:
        if user.isAdmin(): return getTranslation(userInfo, 'error.message', [format_exc()])
        else: return getTranslation(userInfo, 'error.message', ['access denied'])

def getUserInfo(message):
    userInfo = UserInfo(message)
    if not dbUsers.isUserExists(userInfo.userId):
        permissions = dbUsers.getPermissions()
        dbUsers.addNewUser(userInfo.userId, userInfo.username, userInfo.userFullName, permissions[0])
    if not dbTasks.isUserExists(userInfo.userId):
        dbTasks.addNewUser(userInfo.userId)
    if not dbLocal.isUserExists(userInfo.userId):
        dbLocal.addNewUser(userInfo.userId)
    userLogInfo = f'{userInfo} | {dbLocal.db[str(userInfo.userId)]}'
    logging.info(userLogInfo)
    print(userLogInfo)
    return userInfo

@dp.message(Command('start'))
async def startHandler(message: types.Message):
    userInfo = getUserInfo(message)
    await message.answer(getTranslation(userInfo, 'start.message', [userInfo.userFirstName]))
    detailsKeyboard = getDetailsKeyboard(userInfo)
    await message.answer(getTranslation(userInfo, 'about.message.1'), reply_markup=detailsKeyboard)

def getDetailsKeyboard(userInfo):
    inlineButtons = [[types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.details'),
                                                 callback_data=const.callback.details),
                      types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.listtasks'),
                                                 callback_data=const.callback.listtasks)]]
    inlineKeyboard = types.InlineKeyboardMarkup(inline_keyboard=inlineButtons)
    return inlineKeyboard

def getMoreDetailsKeyboard(userInfo):
    inlineButtons = [[types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.demotivator'),
                                                 callback_data=const.callback.demotivator),
                      types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.voice'),
                                                 callback_data=const.callback.voice)]]
    inlineKeyboard = types.InlineKeyboardMarkup(inline_keyboard=inlineButtons)
    return inlineKeyboard

@dp.callback_query(F.data == const.callback.details)
async def detailsCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    moreDetailsKeyboard = getMoreDetailsKeyboard(userInfo)
    await callback.message.answer(text=getTranslation(userInfo, 'about.message.2'), reply_markup=moreDetailsKeyboard)
@dp.callback_query(F.data == const.callback.demotivator)
async def aboutDemotivatorCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    await callback.message.answer(text=getTranslation(userInfo, 'about.demotivator'))

@dp.callback_query(F.data == const.callback.voice)
async def aboutVoiceCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    await callback.message.answer(text=getTranslation(userInfo, 'about.voice'))

def getRecognizerKeyboard(userInfo):
    inlineButtons = [[types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.todo'),
                                                 callback_data=const.callback.todo)]]
    inlineKeyboard = types.InlineKeyboardMarkup(inline_keyboard=inlineButtons)
    return inlineKeyboard

@dp.message(F.voice | F.audio)
async def voiceHandler(message: types.Message):
    userInfo = getUserInfo(message)

    fileId = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(fileId)
    fileData = await bot.download_file(file.file_path)
    recognizedText = recognizeTextByAudio(fileData)

    if recognizedText.error:
        await message.answer(getTranslation(userInfo, 'recognizer.error', [recognizedText.error]))
        return
    dbLocal.setLastRecognizedText(userInfo.userId, recognizedText.text.lower())
    recognizerKeyboard = getRecognizerKeyboard(userInfo)
    await message.reply(getTranslation(userInfo, 'recognizer.success', [recognizedText.text]), reply_markup=recognizerKeyboard)

def getReplaceTaskKeyboard(userInfo):
    inlineButtons = [[types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.yes'),
                                                 callback_data=const.callback.rtyes),
                      types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.no'),
                                                 callback_data=const.callback.rtno)]]
    inlineKeyboard = types.InlineKeyboardMarkup(inline_keyboard=inlineButtons)
    return inlineKeyboard

def getListTasksKeyboard(userInfo):
    inlineButtons = [[types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.listtasks'),
                                                 callback_data=const.callback.listtasks)]]
    inlineKeyboard = types.InlineKeyboardMarkup(inline_keyboard=inlineButtons)
    return inlineKeyboard

async def recognizerHandler(userInfo):
    recognizedText = dbLocal.getLastRecognizedText(userInfo.userId)
    try:
        detectedTask = getDetectedTask(recognizedText)
        currentDate = datetime.datetime.now()
        day, month = map(int, detectedTask.date.split('.'))
        hour, minutes = map(int, detectedTask.time.split(':'))
    except:
        await bot.send_message(userInfo.userId, getTranslation(userInfo, 'todo.denied.recognize'))
        return

    if currentDate > datetime.datetime(currentDate.year, month, day, hour, minutes):
        await bot.send_message(userInfo.userId, getTranslation(userInfo, 'todo.denied.past'))
    elif dbTasks.isTaskExists(userInfo.userId, detectedTask):
        dbLocal.setLastDetectedTask(userInfo.userId, detectedTask)
        existingTask = dbTasks.getTaskByDate(userInfo.userId, detectedTask.date, detectedTask.time)
        replaceTaskKeyboard = getReplaceTaskKeyboard(userInfo)
        await bot.send_message(userInfo.userId, getTranslation(userInfo, 'todo.success.replace', [existingTask.name]), reply_markup=replaceTaskKeyboard)
    else:
        dbTasks.addNewTask(userInfo.userId, detectedTask.date, detectedTask.time, detectedTask.name)
        listTasksKeyboard = getListTasksKeyboard(userInfo)
        await bot.send_message(userInfo.userId, getTranslation(userInfo, 'todo.success.add'), reply_markup=listTasksKeyboard)
    dbLocal.setLastRecognizedText(userInfo.userId, None)

@dp.callback_query(F.data == const.callback.todo)
async def todoCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    await recognizerHandler(userInfo)

def isListTaskCommand(userInfo):
    return userInfo.userText.lower() in ['мои планы', '/tasks']

async def sendListTaskHandler(userInfo):
    userTasks = dbTasks.getTasksByUser(userInfo.userId)
    if not userTasks:
         await bot.send_message(userInfo.userId, getTranslation(userInfo, 'tasks.empty'))
         return
    resultText = getTranslation(userInfo, 'tasks.list')
    for task in userTasks:
        textTask = f'{task.date} в {task.time} - {task.name}'
        resultText += f'{textTask}\n'
    await bot.send_message(userInfo.userId, resultText)

@dp.callback_query(F.data == const.callback.listtasks)
async def listTaskCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    await sendListTaskHandler(userInfo)

@dp.callback_query(F.data == const.callback.rtyes)
async def replaceTaskYesCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    detectedTask = dbLocal.getLastDetectedTask(userInfo.userId)
    existingTask = dbTasks.getTaskByDate(userInfo.userId, detectedTask.date, detectedTask.time)
    dbLocal.setLastDetectedTask(userInfo.userId, None)
    dbTasks.removeTask(userInfo.userId, existingTask.name)
    dbTasks.addNewTask(userInfo.userId, detectedTask.date, detectedTask.time, detectedTask.name)
    listTasksKeyboard = getListTasksKeyboard(userInfo)
    await callback.message.answer(getTranslation(userInfo, 'tasks.replace', [existingTask.name, detectedTask.name]), reply_markup=listTasksKeyboard)

@dp.message(F.photo)
async def demotivatorHandler(message: types.Message):
    userInfo = getUserInfo(message)
    userInfo.userText = message.caption

    fileId = message.photo[-1].file_id
    fileInfo = await bot.get_file(fileId)
    image = await bot.download_file(fileInfo.file_path)

    demotivatorPath = getDemotivator(image, userInfo.userText, userInfo.userId)
    await message.answer_photo(types.FSInputFile(demotivatorPath))
    os.remove(demotivatorPath)

def isUnknownCommand(userInfo):
    return userInfo.userText and userInfo.userText[0] == '/'

async def unknownCommandHandler(userInfo, message):
    await message.answer(getTranslation(userInfo, 'unknown.command.message'))

@dp.message()
async def mainHandler(message: types.Message):
    userInfo = getUserInfo(message)

    if isListTaskCommand(userInfo):
        await sendListTaskHandler(userInfo)
        return

    elif isUnknownCommand(userInfo):
        await unknownCommandHandler(userInfo, message)
        return

    dbLocal.setLastRecognizedText(userInfo.userId, userInfo.userText)
    await recognizerHandler(userInfo)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())