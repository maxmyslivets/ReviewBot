from datetime import datetime
import pytz

from pony.orm import Database, PrimaryKey, Optional, Required, Set, Json

db = Database()

# Получаем объект часового пояса для Москвы
tz_moscow = pytz.timezone('Europe/Moscow')


class Author(db.Entity):
    """
    Модель автора работы.
    Содержит информацию об имени автора, его внешнем id и времени добавления/изменения автора в систему.
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str)  # имя автора
    external_id = Required(int, unique=True)  # внешний id (из любой системы) автора
    reviews = Set('Review', cascade_delete=True)  # связь с отзывами об авторе
    created_at = Required(datetime, default=lambda: datetime.now(tz_moscow))  # время добавления автора в систему
    modified_at = Required(datetime, default=lambda: datetime.now(tz_moscow))  # время последнего изменения внешнего id


class ExternalID(db.Entity):
    """
    Модель предыдущего внешнего id (из любой системы) автора.
    Содержит информацию об авторе и его предыдущем внешнем id.
    """
    id = PrimaryKey(int, auto=True)
    author = Optional(int)  # связь с автором
    external_id = Required(str)  # предыдущий внешний id автора
    created_at = Required(datetime, default=lambda: datetime.now(tz_moscow))


class Review(db.Entity):
    """
    Модель отзыва об авторе.
    Содержит информацию об авторе и тексте отзыва.
    """
    id = PrimaryKey(int, auto=True)
    author = Required(Author)  # связь с автором
    text = Required(str)  # текст отзыва об авторе
    created_at = Required(datetime, default=lambda: datetime.now(tz_moscow))


class Session(db.Entity):
    _table_ = 'sessions'
    id = PrimaryKey(int, auto=True)     # id автора
    user_id = Required(int)    # id юзера
    data = Optional(Json)    # ячейка для хранения данных сессии
