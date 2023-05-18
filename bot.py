from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
import os
from aiogram.filters import BaseFilter
from dotenv import load_dotenv
import logging
import requests
import logging
from datetime import datetime
import json
load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')

# Инициализируем Redis
redis: Redis = Redis(host='localhost')

# Инициализируем хранилище (создаем экземпляр класса RedisStorage)
storage: RedisStorage = RedisStorage(redis=redis)

# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=storage)

logging.basicConfig(level=logging.INFO)

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[int, str ]] = {}







class FilmInBase(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        r = requests.post('https://90a5-89-109-50-12.ngrok-free.app/api/v1/check_film', json={"film_name":  message.text})
        print(message.text)
        print(r.status_code)
        if r.status_code== 200:
            print('Yess')
            return True
        else:
            print('NOOOO')
            return False

class FSM(StatesGroup):
    fill_name = State()
    fill_fisrt_film=State()
    fill_second_film=State()
    fill_third_film=State()
    recomendation=State()


def log(message):
    file_object = open('logs.txt', 'a')
    file_object.write("<!------!>\n")

    file_object.write(str(datetime.now()))
    file_object.write("\nСообщение от {0} {1} (id = {2}) \nText: {3}\n".format(message.from_user.first_name,
                                                              message.from_user.last_name,
                                                              str(message.from_user.id), message.text))
    file_object.close()

# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    name=message.from_user.first_name

    await message.answer(text=f'Приветствую тебя {message.from_user.first_name} {message.from_user.last_name}\n'
                              'Чтобы перейти к заполнению анкеты - '
                              'отправьте команду /fillform')
    log(message)







# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    log(message)
    await message.answer(text='Отменять нечего\n\n'
                              'Чтобы перейти к заполнению анкеты - '
                              'отправьте команду /fillform')

@dp.message(Command(commands='help'))
async def process_start_command(message: Message):
    log(message)
    await message.answer(text=f'Я команда hel[]')




# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    log(message)
    await message.answer(text='Произошел сброс!\n\n'
                              'Чтобы снова перейти к заполнению анкеты - '
                              'отправьте команду /fillform')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Я вежливый бот, поэтому,'
                         'пожалуйста, напиши,как к тебе лучше обращаться)')
    log(message)
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSM.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@dp.message(StateFilter(FSM.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    log(message)
    await message.answer(text=f"Спасибо, {message.text}!\n\nА теперь давай перейдем к твоим предпочтениям в фильмах!\n"
                         'Cейчас я тебя попрошу написать отдельными сообщениями по очереди три твоих любимых фильма\n'
                         'И на их основе мы дадим тебе лучшую рекомендацию)))\n\n'
                         'Введи пожалуйста первый фильм:')
    # Устанавливаем состояние ожидания ввода возраста

    await state.set_state(FSM.fill_fisrt_film)



# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@dp.message(StateFilter(FSM.fill_name))
async def warning_not_name(message: Message):
    log(message)
    await message.answer(text='То, что вы отправили не похоже на имя\n\n'
                              'Пожалуйста, введите ваше имя\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')


@dp.message(StateFilter(FSM.fill_fisrt_film), FilmInBase())
async def process_fisrt_film_sent(message: Message, state: FSMContext):
    await state.update_data(first_film=message.text)
    await message.answer(text='Отлично!\n\nА теперь еще один!')
    log(message)
    await state.set_state(FSM.fill_second_film)

@dp.message(StateFilter(FSM.fill_second_film), FilmInBase())
async def process_second_film_sent(message: Message, state: FSMContext):
    await state.update_data(second_film=message.text)
    await message.answer(text='Превосходно!\n\nОсталось совсем чуть чуть, нужно всего лишь ввести еще один фильм '
                         'и ты получишь шикарную рекомендацию по анимэ')
    log(message)
    await state.set_state(FSM.fill_third_film)

@dp.message(StateFilter(FSM.fill_third_film), FilmInBase())
async def process_third_film_sent(message: Message, state: FSMContext):
    await state.update_data(third_film=message.text)

    user_dict[message.from_user.id] = await state.get_data()
    await message.answer(text=f'Поздравляю {user_dict[message.from_user.id]["name"]}, ты успешно заполнил форму!\n\n'
                         'Подожди пожалуйста немного и у тебя появится возможность получить свою рекомендацию')
    r = requests.post('https://90a5-89-109-50-12.ngrok-free.app/api/v1/get_recommendations', json={
                                                                                            "film_name1":  user_dict[message.from_user.id]["first_film"],
                                                                                            "film_name2": user_dict[message.from_user.id]["second_film"],
                                                                                           "film_name3": user_dict[message.from_user.id]["third_film"]})


    resp_dict = r.json()
    print(type(resp_dict))
    print(resp_dict)
    recomendation_string:str="\n"

    for anime in resp_dict:
        print(type(resp_dict[anime]))
        for key, value in resp_dict[anime].items():
            recomendation_string= recomendation_string+ "\n"+str(key) +" : "+ str(value)

        recomendation_string= recomendation_string+ "\n"

    print(recomendation_string)



    await state.update_data(recomendation=recomendation_string)
    user_dict[message.from_user.id]= await state.get_data()
    await message.answer(text='Нажми команду /getrecomedation и получишь список того что тебе точно стоит посмотреть)')
    log(message)
    await state.clear()




# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@dp.message(Command(commands='getrecomedation'), StateFilter(default_state))
async def process_getrecomedation_command(message: Message):
    file_object = open('logs.txt', 'a')
    # Append 'hello' at the end of file
    file_object.write(f'\n{message.from_user.full_name}  {message.from_user.id} getrecomedation')
    # Close the file
    file_object.close()
    log(message)
    if message.from_user.id in user_dict:


        await message.answer(
            text=f' {user_dict[message.from_user.id]["name"]}, ты выбрал\n'
                    f'{user_dict[message.from_user.id]["first_film"]} первым любимым фильмом\n'
                    f'{user_dict[message.from_user.id]["second_film"]} вторым\n'
                    f'{user_dict[message.from_user.id]["third_film"]} третьим\n'
                    f'Держи свою рекомендацю))\n'
                     f'{user_dict[message.from_user.id]["recomendation"]}\n')
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(text='Вы еще не заполняли анкету. '
                                  'Чтобы приступить - отправьте '
                                  'команду /fillform')

@dp.message(StateFilter(FSM.fill_fisrt_film))
@dp.message(StateFilter(FSM.fill_second_film))
@dp.message( StateFilter(FSM.fill_third_film))
async def warning_not_film(message: Message):
    log(message)
    await message.answer(

        text='К сожалению фильма нет в нашей базе\n\n'
             'Попробуйте еще раз\n\nПроверьте корректно ли введены данные\n'
             'Чтобы отменить заполнение анкеты - отправьте команду /cancel')



# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    log(message)
    await message.reply(text='Извините, не очень понял, что вы хотите, если сомневаетесь, что делаете все правильно, нажмите команду /help')


# Запускаем поллинг
if __name__ == '__main__':
    dp.run_polling(bot)
