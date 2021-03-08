import telebot
from telebot.types import Message, CallbackQuery

from my_types import Game
from my_types import Keyboard
from setting import TELEGRAM_TOKEN

bot = telebot.TeleBot(TELEGRAM_TOKEN)
game = Game()


def write_question():
    send_message_all(text='Вопросы можно писать... Сейчас!', register_next_step_handler=add_question)
    game.users.ready_false()


def end_write_question():
    send_message_all(text='Отлично, все написали по своему вопросу!')


def start_write_answer():
    game.users.ready_false()
    send_message_all(text='Немножечко перемишаем... Ах, вот!')
    for user in game.users.list:
        question = get_question(user.id)
        message = bot.send_message(chat_id=user.id, text=f'Ответьте на вопрос: {question.text}')
        bot.register_next_step_handler(message, add_answer)


def rules():
    send_message_all(text='Тут типо должны были написанны правила, но мне впадлу писать, соре :)')


def send_message_all(text: str, register_next_step_handler=None, keyboard=Keyboard().nul()):
    for user in game.users.list:
        message = bot.send_message(chat_id=user.id, text=text, reply_markup=keyboard)
        if register_next_step_handler is not None:
            bot.register_next_step_handler(message, register_next_step_handler)


def add_question(message: Message):
    game.round.add_question(text=message.text, author_id=message.chat.id)
    message = bot.send_message(chat_id=message.chat.id, text='Ваш вопрос принят!')
    bot.register_next_step_handler(message, question_is_done)


def question_is_done(message: Message):
    game.users.ready_true(user_id=message.chat.id)
    message = bot.send_message(chat_id=message.chat.id, text='Вы уже написали вопрос, подождите других')
    bot.register_next_step_handler(message, question_is_done)


def write_answer(message: Message):
    user_id = message.chat.id
    question = get_question(user_id)
    if question.text != '':
        message = bot.send_message(chat_id=message.chat.id, text=f'Ответьте на вопрос: {question.text}')
        bot.register_next_step_handler(message, add_answer)
    else:
        answer_is_empty(message)


def get_question(user_id):
    question = game.round.get_question(user_id)
    return question


def add_answer(message: Message):
    game.round.add_answer(text=message.text, author_id=message.chat.id)
    bot.send_message(text='Ваш ответ принят!', chat_id=message.chat.id)
    write_answer(message)


def answer_is_empty(message: Message):
    game.users.ready_true(user_id=message.chat.id)
    message = bot.send_message(chat_id=message.chat.id, text='Вопросы закончились, ожидайте')
    bot.register_next_step_handler(message, answer_is_empty)


def end_write_answers():
    send_message_all(text='Отлично, все написали свои гадкие ответы!')


def start_answer_question():
    send_message_all(text='Перейдем к самому сладкому, к оцениванию!')
    send_answer_question()


def send_answer_question():
    response = game.round.get_answers_question()
    if response[0] != '':
        send_message_all(text=f'Какой самый смешной вариант на вопрос: {response[0]}',
                         keyboard=Keyboard().answer_question(response[1]),
                         register_next_step_handler=add_point)
    else:
        send_message_all(text='Оценивание закончилось', register_next_step_handler=answer_question_is_empty)


def answer_question_is_empty(message: Message):
    bot.send_message(chat_id=message.chat.id, text='Оценивание закончилось, пожауйста, подождите')


def add_point(message: Message, call: CallbackQuery):
    game.round.add_vote_answer(answer_id=call.message)
    bot.send_message(chat_id=message.chat.id, text='Ваш голос принят!')
