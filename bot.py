import telebot
from telebot.types import Message, CallbackQuery

from logger import logger as log
from settings import *
from database.queries import *


log.debug("Connect to Bot with token...")
bot = telebot.TeleBot(TG_TOKEN)

MY_COMMANDS = {
    "/add": lambda message: handle_add_author(message),
    "/check": lambda message: handle_check_author(message),
}
if len(MY_COMMANDS.keys()) != len(bot.get_my_commands()):
    log.warning("Check that all commands are in the variable `MY_COMMANDS`!")


@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    log.info(f"User {message.from_user.username} start launched a bot")
    bot.clear_step_handler(message)
    create_session(message.from_user.id)
    bot.send_message(chat_id=message.chat.id, message_thread_id=message.message_thread_id,
                     text=f"Привет, {message.from_user.username}!\nВведи команду /check для проверки авторов.")


@db_session
def format_author_info(author: Author, admin: bool = False) -> str:
    """
    Получение текста об авторе в зависимости от уровня доступа.

    :param author: модель автора из БД.
    :type author: Author
    :param admin: уровень доступа
    :type admin: bool

    :return: Текст с информацией об авторе
    :rtype: str
    """
    log.debug("Formatting author info")
    text = str()
    if admin:
        text += f"Имя: {author.name}"
        if DEBUG:
            text += f"\ndb_id: {author.id}"
        text += f"\nid: {get_external_id_for_author(author.id)}"
        text += f"\nДата добавления: {author.created_at.strftime('%H:%M:%S %d.%m.%Y')}"
        if author.created_at != author.modified_at:
            text += f"\nДата обновления id: {author.modified_at.strftime('%H:%M:%S %d.%m.%Y')}"
            text += f"\nСтарые id: {get_old_external_ids(author.id)}"
        reviews = get_reviews(author.id)
        text += f"\n\nОтзывы({len(reviews)}):"
        if len(reviews) > 0:
            for num, review_text, review_date in reviews:
                text += f"\n{num}. {review_text} [{review_date}]"
        else:
            text += " У автора пока нет отзывов."
    else:
        text += f"Имя: {author.name}"
        reviews = get_reviews(author.id)
        text += f"\n\nОтзывы({len(reviews)}):"
        if len(reviews) > 0:
            for num, review_text, review_date in reviews:
                text += f"\n{num}. {review_text} [{review_date}]"
        else:
            text += " У автора пока нет отзывов."
    return text


@bot.message_handler(commands=['add'])
def handle_add_author(message: Message) -> None:
    """
    Добавление автора в БД.

    :param message: сообщение.
    :type message: Message

    :return: None
    """
    bot.clear_step_handler(message)
    create_session(message.from_user.id)
    admin = message.from_user.id == TG_ADMIN_ID or message.from_user.id == TG_DEV_ADMIN_ID
    if not admin:
        log.info(f"User {message.from_user.username} tried to add the author.")
        bot.send_message(message.chat.id, 'Для доступа к функции необходимо обладать правами администратора.')
    else:
        log.info(f"Admin {message.from_user.username} adding author...")
        bot.send_message(message.chat.id, 'Введите имя автора')
    bot.register_next_step_handler(message, get_author_name)


def get_author_name(message: Message) -> None:
    if message.text in MY_COMMANDS:
        create_session(message.from_user.id)  # todo: clear session
        MY_COMMANDS[message.text](message)
    else:
        log.info(f"Admin {message.from_user.username} enters the author's name")
        add_session_data(message.from_user.id, {"name": message.text})
        bot.send_message(message.chat.id, 'Введите внешний id автора')
        bot.register_next_step_handler(message, get_external_id)


def get_external_id(message: Message) -> None:
    if message.text in MY_COMMANDS:
        create_session(message.from_user.id)  # todo: clear session
        MY_COMMANDS[message.text](message)
    else:
        log.info(f"Admin {message.from_user.username} enters the author's external id")
        secondary_id = message.text
        name = get_session_data(message.from_user.id)["name"]
        author = add_author(name, secondary_id)
        admin = message.from_user.id == TG_ADMIN_ID or message.from_user.id == TG_DEV_ADMIN_ID
        text = format_author_info(author, admin)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text="✏️ Изменить id", callback_data=f"modify_id_{author.id}"))
        markup.add(telebot.types.InlineKeyboardButton(text="➕ Добавить отзыв", callback_data=f"add_review_{author.id}"))
        bot.send_message(message.chat.id, 'Новый автор добавлен\n\n' + text, reply_markup=markup)
        create_session(message.from_user.id)   # todo: clear session


@bot.message_handler(commands=['check'])
def handle_check_author(message: Message) -> None:
    """
    Получение информации об авторе.

    :param message: сообщение.
    :type message: Message

    :return: None
    """
    bot.clear_step_handler(message)
    bot.send_message(message.chat.id, 'Введите id автора')
    bot.register_next_step_handler(message, get_author_id)


def get_author_id(message: Message) -> None:
    if message.text in MY_COMMANDS:
        create_session(message.from_user.id)  # todo: clear session
        MY_COMMANDS[message.text](message)
    else:
        author = get_author_from_external_id(message.text)
        if author is None:
            bot.send_message(message.chat.id, "Автора с таким id нет в базе данных.")
            return
        admin = message.from_user.id == TG_ADMIN_ID or message.from_user.id == TG_DEV_ADMIN_ID
        text = format_author_info(author, admin)
        markup = telebot.types.InlineKeyboardMarkup()
        if admin:
            markup.add(telebot.types.InlineKeyboardButton(text="✏️ Изменить id", callback_data=f"modify_id_{author.id}"))
            if DEBUG:
                markup.add(telebot.types.InlineKeyboardButton(text="➕ Добавить отзыв", callback_data=f"add_review_{author.id}"))
        else:
            markup.add(telebot.types.InlineKeyboardButton(text="➕ Добавить отзыв", callback_data=f"add_review_{author.id}"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        create_session(message.from_user.id)  # todo: clear session


@bot.callback_query_handler(func=lambda call: call.data.startswith("modify_id_"))
def handle_modify_id(call: CallbackQuery) -> None:
    """
    Добавление автору вторичного id.

    :param call: вызов.
    :type call: CallbackQuery

    :return: None
    """
    bot.clear_step_handler(call.message)
    create_session(call.from_user.id)
    author_id = call.data[len("modify_id_"):]
    add_session_data(call.from_user.id, {"author_id": author_id})
    bot.send_message(call.message.chat.id, 'Введите новый внешний id')
    bot.register_next_step_handler(call.message, get_new_external_id)


def get_new_external_id(message: Message) -> None:
    if message.text in MY_COMMANDS:
        MY_COMMANDS[message.text](message)
    else:
        author_id = int(get_session_data(message.from_user.id)["author_id"])
        external_id = message.text
        modify_id(author_id=author_id, external_id=external_id)
        text = format_author_info(get_author_from_id(author_id), True)
        bot.send_message(message.chat.id, text)
        create_session(message.from_user.id)   # todo: clear session


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_review_"))
def handle_add_review(call: CallbackQuery) -> None:
    """
    Добавление автору отзыва.

    :param call: вызов.
    :type call: CallbackQuery

    :return: None
    """
    bot.clear_step_handler(call.message)
    create_session(call.from_user.id)
    author_id = call.data[len("add_review_"):]
    add_session_data(call.from_user.id, {"author_id": author_id})
    bot.send_message(call.message.chat.id, 'Напишите отзыв')
    bot.register_next_step_handler(call.message, get_review_text)


def get_review_text(message: Message) -> None:
    if message.text in MY_COMMANDS:
        create_session(message.from_user.id)  # todo: clear session
        MY_COMMANDS[message.text](message)
    else:
        author_id = int(get_session_data(message.from_user.id)["author_id"])
        add_review(author_id, message.text)
        admin = message.from_user.id == TG_ADMIN_ID or message.from_user.id == TG_DEV_ADMIN_ID
        text = format_author_info(get_author_from_id(author_id), admin)
        bot.send_message(message.chat.id, text)
        create_session(message.from_user.id)   # todo: clear session
