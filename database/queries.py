from logger import logger as log

from pony.orm import db_session, select, commit

from database.db import *


@db_session
def add_author(name: str, external_id: str) -> Author:
    """
    Добавление автора в БД по имени и второстепенному id.

    :param name: имя автора.
    :type name: str
    :param external_id: второстепенный id автора.
    :type external_id: str

    :return: автор
    :rtype: Author

    :doc-author: Max Myslivets
    """
    log.info(f"Author's addendum `{name}` id: {external_id}")
    external_id_db = ExternalID(external_id=external_id)
    commit()
    author = Author(name=name,
                    external_id=external_id_db.id,
                    created_at=external_id_db.created_at,
                    modified_at=external_id_db.created_at)
    commit()
    external_id_db.author = author.id
    return author


@db_session
def modify_id(author_id: int, external_id: str) -> None:
    """
    Добавление второстепенного id автору по его основному id в БД.

    :param author_id: id автора.
    :type author_id: int
    :param external_id: второстепенный id автора.
    :type external_id: str

    :return: None

    :doc-author: Max Myslivets
    """
    log.info(f"Addendum new id `{external_id}` for author `{Author[author_id].name}`")
    external_id_db = ExternalID(author=author_id, external_id=external_id)
    commit()
    author = Author[author_id]
    author.set(external_id=external_id_db.id, modified_at=external_id_db.created_at)


@db_session
def add_review(author_id: int, text: str) -> None:
    """
    Добавление отзыва об авторе по id автора.

    У бота запрашивается список авторов, вывод в виде кейбордов, при нажатии
    на кейборд появляется запрос на ввод отзыва.

    После отправки отзыва производится проверка, вернулся ли id отзыва, и
    отправляется уведомление об успешной отправке отзыва

    :param author_id: id автора.
    :type author_id: int
    :param text: отзыв.
    :type text: str

    :return: None

    :doc-author: Max Myslivets
    """
    log.info(f"Addendum review for author `{Author[author_id].name}`")
    Review(author=author_id, text=text)


@db_session
def get_author_from_external_id(external_id: str) -> Author:
    """
    Получение информации об авторе.

    :param external_id: внешний id автора.
    :type external_id: str

    :return: author
    :rtype: Author

    :doc-author: Max Myslivets
    """
    log.info(f"Getting author with external_id `{external_id}`")
    author_id = select(eid.author for eid in ExternalID if eid.external_id == external_id).first()
    return Author.get(id=author_id)


@db_session
def get_author_from_id(author_id: int) -> Author:
    log.info(f"Getting author with id `{author_id}`")
    return Author.get(id=author_id)


@db_session
def create_session(user_id: int) -> int:
    """
    Создание или очистка сессии.

    :param user_id: id юзера.
    :type user_id: int

    :return: id сессии
    :rtype: int

    :doc-author: Max Myslivets
    """
    log.info(f"Created session for user with id `{user_id}`")
    session = Session.get(user_id=user_id)
    if session:
        # если сессия с id есть, то очищаем data
        session.data = {}
    else:
        # если нет, то создаем новую
        session = Session(user_id=user_id)
    return session.id


@db_session
def add_session_data(user_id: int, data: dict) -> int:
    """
    Добавление данных в сессию.

    :param user_id: id юзера
    :type user_id: int
    :param data: данные сессии
    :type data: dict

    :return: id сессии
    :rtype: int

    :doc-author: Max Myslivets
    """
    log.info(f"User with id `{user_id}` addendum data to session")
    session = Session.get(user_id=user_id)
    if session.data is None:
        session.data = data
    else:
        old_data = session.data
        session.data = old_data | data
    return session.id


@db_session
def get_session_data(user_id: int) -> dict:
    """
    Добавление данных в сессию.

    :param user_id: id юзера
    :type user_id: int

    :return: данные сессии
    :rtype: dict

    :doc-author: Max Myslivets
    """
    log.info(f"User with id `{user_id}` getting data from session")
    return Session.get(user_id=user_id).data


def get_external_id_for_author(author_id: int) -> str:
    id_external_id = Author[author_id].external_id
    return ExternalID[id_external_id].external_id


def get_old_external_ids(author_id: int) -> str:
    now_external_id = get_external_id_for_author(author_id)
    old_external_ids = list(select(eid.external_id for eid in ExternalID if eid.author == author_id)[:])
    old_external_ids.remove(now_external_id)
    return ', '.join(old_external_ids)


def get_reviews(author_id: int) -> list[tuple[int, str, str]]:
    reviews = select(r for r in Review if r.author.id == author_id).order_by(Review.created_at)
    return [(num+1, review.text, review.created_at.strftime('%H:%M %d.%m.%Y')) for num, review in enumerate(reviews)]
