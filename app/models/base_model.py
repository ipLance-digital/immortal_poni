from sqlalchemy.orm import declarative_base, Session

from app.database import get_db

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def get_db_session(cls):
        """
        Получает сессию базы данных.
        """
        return next(get_db())

    @classmethod
    def filter(cls, **kwargs):
        """
        Статический метод для фильтрации по переданным аргументам.
        Возвращает запрос, который можно дополнительно использовать.
        """
        db_session = cls.get_db_session()
        return db_session.query(cls).filter_by(**kwargs)

    @classmethod
    def all(cls):
        """
        Возвращает все записи из таблицы.
        """
        db_session = cls.get_db_session()
        return db_session.query(cls).all()

    @classmethod
    def save(cls, obj, db_session=None):
        """
        Сохраняет объект в базе данных (вставка или обновление).
        Если объект уже существует (по наличию id), он будет обновлен.
        Если нет - вставлен.
        """
        if db_session is None:
            db_session = cls.get_db_session()
        db_session.add(obj)
        db_session.commit()
        db_session.refresh(obj)
        return obj
