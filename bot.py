import telebot # библиотека telebot
from config import token # импорт токена
import re

bot = telebot.TeleBot(token) 

bad_words = ['капибара', 'собака', 'нельза']  # список запрещённых слов
user_warnings = {}
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для управления чатом.")

@bot.message_handler(func=lambda message: True)
def check_message_for_links(message):
    url_pattern = r"https?://[^\s]+"
    
    if re.search(url_pattern, message.text):
        chat_id = message.chat.id # сохранение id чата
         # сохранение id и статуса пользователя, отправившего сообщение
        user_id = message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status

        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id) 
            bot.reply_to(message, f"Пользователь @{message.from_user.username} был забанен за отправку ссылки.")
    else:
        bot.reply_to(message, "Ваше сообщение не содержит ссылок.") 


@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message: #проверка на то, что эта команда была вызвана в ответ на сообщение 
        chat_id = message.chat.id # сохранение id чата
         # сохранение id и статуса пользователя, отправившего сообщение
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status 
         # проверка пользователя
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id) # пользователь с user_id будет забанен в чате с chat_id
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите забанить.")

@bot.message_handler(content_types=['left_chat_member'])
def handle_member_left(message):
    left_user = message.left_chat_member  # Это объект пользователя, который покинул чат
    chat_id = message.chat.id

    # Вы можете сделать что-то, например, вывести сообщение о том, что пользователь покинул чат
    bot.send_message(chat_id, f"Пользователь {left_user.first_name} покинул чат.")

    # Если нужно, можно сохранить информацию или выполнить другие действия
    print(f"Пользователь {left_user.id} покинул чат {chat_id}")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if contains_bad_words(message.text):
        process_bad_words(message, user_id, chat_id)
    else:
        bot.reply_to(message, "Сообщение принято. Спасибо за соблюдение правил.")

def contains_bad_words(text):
    """Проверяет текст на наличие запрещённых слов."""
    return any(bad_word in text.lower() for bad_word in bad_words)

def process_bad_words(message, user_id, chat_id):
    """Обрабатывает сообщение, содержащее ненормативную лексику."""
    # Увеличиваем количество предупреждений для пользователя
    if user_id in user_warnings:
        user_warnings[user_id] += 1
    else:
        user_warnings[user_id] = 1

    # Если пользователь нарушает впервые, предупреждаем его
    if user_warnings[user_id] == 1:
        bot.reply_to(message, "Предупреждение: Пожалуйста, воздержитесь от использования ненормативной лексики.")
    # Если нарушение происходит второй раз, баним пользователя
    elif user_warnings[user_id] >= 2:
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status != 'administrator' and user_status != 'creator':
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{message.from_user.username} был забанен за многократное использование ненормативной лексики.")

bot.infinity_polling(none_stop=True)
