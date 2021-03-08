import telebot
import logging
from my_types import server_send, User, server_send, Game, Keyboard
from setting import TELEGRAM_TOKEN
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, Message, \
    CallbackQuery
import subprocess
import shelve


class Menu:
    def add_message(self):
        pass


class DataBase:
    def __init__(self):
        d = shelve.open('user_status')
        d.close()
        self.users = list(User)
        self.games = list(Game)

    def get_user_obj(self, user_id: int):
        for user in self.users:
            if user.id == user_id:
                return user

        user = User(user_id=user_id)
        self.users.append(user)
        return user

    def get_game_obj(self, user: User) -> Game:
        for game in self.games:
            if user in game.users_list:
                return game


log_format = '[%(asctime)s] [%(levelname)s] - %(name)s - %(message)s'
logging.basicConfig(filename="log.log", level=logging.DEBUG, format=log_format)
logger = logging.getLogger('telegram_handler')

bot = telebot.TeleBot(TELEGRAM_TOKEN)


class Server:
    def __init__(self, server_id: int):
        self.id = server_id
        self.port = str(5000 + server_id)
        self.game_begin = False

    def start(self):
        subprocess.Popen(
            [r"C:\Users\Александр Мурадов\AppData\Local\Programs\Python\Python39\python.exe", 'game_server.py',
             self.port])


server_id_count = 1
servers = []
database = DataBase()


@bot.message_handler(content_types=['start'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text='Добро пожаловать!', reply_markup=Keyboard().menu())


@bot.callback_query_handlers(func=lambda call: True)
def callback_inline(call: CallbackQuery):
    pass


@bot.message_handler(content_types=['text'])
def assembler(message: Message):
    user = database.get_user_obj(message.chat.id)
    user_status = user.status
    if user_status == 'menu':
        menu_status_handler(message)

    elif user_status == 'game':
        game_status_handler(message=message, user=user)


def menu_status_handler(message: Message):
    if message.text == 'О игре':
        rules(message)

    elif message.text == 'Найти игру':
        search_game(message)


def game_status_handler(message: Message, user: User):
    game = database.get_game_obj(user)
    last_command_data = user.last_command.split('_')
    last_command = last_command_data[0]
    if last_command == 'write.question':
        game.add_question(author=user, text=message.text)
    elif last_command == 'question':
        question_id = int(last_command_data[1])
        game.add_answer(text=message.text, author=user, question_id=question_id)




bot.polling(none_stop=True)


# Добавить try expert везде
