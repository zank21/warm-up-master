import telebot
from telebot.types import Message
import logging
from my_types import server_send, KeyboardTelegram
from setting import TELEGRAM_TOKEN

log_format = '[%(asctime)s] [%(levelname)s] - %(name)s - %(message)s'
logging.basicConfig(filename="log.log", level=logging.DEBUG, format=log_format)
logger = logging.getLogger('telegram_handler')

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(content_types=['text'])
def send_text(message: Message):
    response = server_send('_'.join((message.text, str(message.chat.id))))
    response = response.split('_')

    keyboard = KeyboardTelegram()
    if response[0] == 'assessment':
        question_text = response[1]
        answers = response[2].split(',')
        keyboard = keyboard.assessment(question_text=question_text, answers=answers)
    else:
        keyboard = keyboard.nul()

    bot.send_message(chat_id=message.chat.id, text=response[1], reply_markup=keyboard)

    bot.polling()
