import logging
from aiogram import Bot, Dispatcher, executor, types
from take_tasks import init, get_leaderboard, get_task, check_task
import ranks, botToken, re
from aiogram.types import ReplyKeyboardRemove
API_TOKEN = '5213341891:AAFjB6UwX6WsyBXYJ5RHXYSGeUQZGUDvITk' # your code
tasks_list = init()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

current_task = dict()
current_command = dict()
train_mode = dict()
user_ids = set()

def change_current_command(user : int, command : str):
    global current_command
    current_command[user] = command

def change_current_task(user : int, task : str):
    global current_task
    current_task[user] = task

@dp.message_handler(commands=['start', 'help'])
async def send_help(message: types.Message):
    await message.answer("""Привет, это бот для подготовки к ЕГЭ по русскому языку, автор не гарантирует наличие всех заданий, их актуальность и правильность.

Список команд:
Команды /help и /start вызывают данное меню

Для получения задания, напишите /task и в следующем сообщении выберите номер задания

Для получения таблицы лидеров по данному заданию, напишите /leaderboard и в следующем сообщении выберите номер задания

Для получения рангов напишите /ranks

У бота есть режим тренировки - это бесконечный поток определённых заданий, для того чтобы войти в режим тренировки пропишите /train и в следующем сообщении выберите номер задания.\nДля выхода из режима тренировки - пропишите /exit """)

@dp.message_handler(commands=['rank', 'ranks'])
async def send_ranks(message: types.Message):
    full_ranks = "Звания:\n"
    for [x, y] in ranks.ranks.items():
        if x == -1000000000:
            full_ranks += 'До ' + str(-9) + ' очков - ' + str(y) + '\n'
        else:
            full_ranks += 'C ' + str(x) + ' очков - ' + str(y) + '\n'
    await message.answer(full_ranks)


@dp.message_handler(commands=['exit'])
async def exit_from_train(message: types.Message):
    user = message.from_user
    userid = user.id
    if (userid in user_ids) == False:
        train_mode[userid] = False
        user_ids.add(userid)
        current_task[userid] = -1
        current_command[userid] = ''
    if train_mode[userid] == False:
        await message.answer("Вы должны быть в режиме тренировки, чтобы выходить.")
        return
    current_command[userid] = ''
    current_task[userid] = -1
    train_mode[userid] = False
    await message.answer("Вы успешно вышли из режима тренировки")


@dp.message_handler(commands=['train'])
async def get_train(message: types.Message):
    user = message.from_user
    userid = user.id

    if (userid in user_ids) == False:
        train_mode[userid] = False
        user_ids.add(userid)
        current_task[userid] = -1
        current_command[userid] = ''

    if current_task[userid] != -1:
        await message.answer("Вы забыли ответить на предыдущий вопрос. Попробуйте ещё раз")
        return
    if current_command[userid] == 'task' or current_command[userid] == 'train':
        await message.answer("Вы должны указать номер задания, а не команду!\nПопробуйте ещё раз.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [str(c) for c in tasks_list]
    keyboard.add(*buttons)
    await message.answer("Укажите следующим сообщением номер задания", reply_markup=keyboard)
    change_current_command(message.from_user.id, 'train')


@dp.message_handler(commands=['task'])
async def get_tasks(message: types.Message):
    user = message.from_user
    userid = user.id

    if (userid in user_ids) == False:
        train_mode[userid] = False
        user_ids.add(userid)
        current_task[userid] = -1
        current_command[userid] = ''
    if current_task[userid] != -1:
        await message.answer("Вы забыли ответить на предыдущий вопрос. Попробуйте ещё раз")
        return
    if current_command[userid] == 'task' or current_command[userid] == 'train':
        await message.answer("Вы должны указать номер задания, а не команду!\nПопробуйте ещё раз.")
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [str(c) for c in tasks_list]
    keyboard.add(*buttons)
    await message.answer("Выберете номер задания", reply_markup=keyboard)
    change_current_command(message.from_user.id, 'task')


@dp.message_handler(commands=['leaderboard'])
async def get_results(message: types.Message):
    user = message.from_user
    userid = user.id

    if (userid in user_ids) == False:
        user_ids.add(userid)
        train_mode[userid] = False
        current_task[userid] = -1
        current_command[userid] = ''

    if current_task[userid] != -1:
        await message.answer("Вы забыли ответить на предыдущий вопрос. Попробуйте ещё раз")
        return

    if current_command[userid] == 'leaderboard':
        await message.answer("Вы должны указать номер задания, а не команду!\nПопробуйте ещё раз.")
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['все'] + [str(c) for c in tasks_list]
    keyboard.add(*buttons)
    await message.answer("Укажите следующим сообщением номер задания", reply_markup=keyboard)
    change_current_command(message.from_user.id, 'leaderboard')


@dp.message_handler()
async def simple_message(message: types.Message):
    print(message.from_user.username)
    user = message.from_user
    userid = user.id
    if (userid in user_ids) == False:
        train_mode[userid] = False
        user_ids.add(userid)
        current_task[userid] = -1
        current_command[userid] = ''

    if train_mode[userid] == True:
        result = check_task(user, current_task[userid], message.text)
        if result == 'True':
            await message.answer("Правильный ответ!😎")
        else:
            
            await message.answer("Неправильный ответ!😢")
            await message.answer(result)
        if current_task[userid] == 4:
            task = get_task(user, current_task[userid])
            answers_list = task.split('\n')
            answers_list.pop(0)
            try:
                answers_list.remove('\n')
                answers_list.remove(' ')
            except ValueError:
                print('all ok')
            answers_list = [re.sub("[\(\[].*?[\)\]]", "", c) for c in answers_list]
            answers_list = [c.lower() for c in answers_list]
            answers_list = [c.replace(' ', '') for c in answers_list]
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = answers_list
            keyboard.add(*buttons)
            await message.answer(task, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await message.answer(get_task(user, current_task[userid]), parse_mode='Markdown')
    elif current_command[userid] == '':
        if current_task[userid] == -1:
            await message.answer("Я не понимаю, что тут написано😭\nВоспульзуйтесь командами из меню слева!")
            return
        result = check_task(user, current_task[userid], message.text)
        if result == 'True':
            await message.answer("Правильный ответ!😎",parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
            
        else:
            await message.answer("Неправильный ответ!😢",parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
            await message.answer(result, parse_mode='Markdown', disable_web_page_preview=True)
        change_current_task(userid, -1)
    elif current_command[userid] == 'task':
        try:
            num = int(message.text)
        except ValueError:
            await message.answer("Вы должны указать число!\nПопробуйте ещё раз")
            return
        
        if (1 <= num and num <= 26) == False:
            await message.answer("Вы должны указать число в диапазоне от 1 до 26!\nПопробуйте ещё раз")
            return
        if tasks_list.count(num) == 0:
            await message.answer("К сожалению данное задание ещё не добавлено😭\nПопробуйте ещё раз")
            return

        change_current_task(userid, num)
        if current_task[userid] == 4:
            task = get_task(user, current_task[userid])
            answers_list = task.split('\n')
            answers_list.pop(0)
            try:
                answers_list.remove('\n')
                answers_list.remove(' ')
            except ValueError:
                print('all ok')
            answers_list = [re.sub("[\(\[].*?[\)\]]", "", c) for c in answers_list]
            answers_list = [c.lower() for c in answers_list]
            answers_list = [c.replace(' ', '') for c in answers_list]
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = answers_list
            keyboard.add(*buttons)
            await message.answer(task, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await message.answer(get_task(user, current_task[userid]), parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
            
            
        change_current_command(userid, '')
    elif current_command[userid] == 'train':
        try:
            num = int(message.text)
        except ValueError:
            await message.answer("Вы должны указать число!\nПопробуйте ещё раз")
            return
        
        if (1 <= num and num <= 26) == False:
            await message.answer("Вы должны указать число в диапазоне от 1 до 26!\nПопробуйте ещё раз")
            return
        if tasks_list.count(num) == 0:
            await message.answer("К сожалению данное задание ещё не добавлено😭\nПопробуйте ещё раз")
            return

        train_mode[userid] = True
        change_current_task(userid, num)
        if current_task[userid] == 4:
            task = get_task(user, current_task[userid])
            answers_list = task.split('\n')
            answers_list.pop(0)
            try:
                answers_list.remove('\n')
                answers_list.remove(' ')
            except ValueError:
                print('all ok')
            answers_list = [re.sub("[\(\[].*?[\)\]]", "", c) for c in answers_list]
            answers_list = [c.lower() for c in answers_list]
            answers_list = [c.replace(' ', '') for c in answers_list]
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = answers_list
            keyboard.add(*buttons)
            await message.answer(task, parse_mode='Markdown', reply_markup=keyboard)
        else:
            await message.answer(get_task(user, current_task[userid]), parse_mode='Markdown')
        change_current_command(userid, '')
    elif current_command[userid] == 'leaderboard':
        if message.text == "все":
            num = 0
        else:
            try:
                num = int(message.text)
            except ValueError:
                await message.answer("Вы должны указать число!\nПопробуйте ещё раз")
                return
            
            if (1 <= num and num <= 26) == False:
                await message.answer("Вы должны указать число в диапазоне от 1 до 26!\nПопробуйте ещё раз")
                return
            if tasks_list.count(num) == 0:
                await message.answer("К сожалению данное задание ещё не добавлено😭\nПопробуйте ещё раз")
                return

        await message.answer(get_leaderboard(user, num), disable_web_page_preview=True)
        
        change_current_command(userid, '')

if __name__ == '__main__':
    print(tasks_list)
    executor.start_polling(dp, skip_updates=True)
