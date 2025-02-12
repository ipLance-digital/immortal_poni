"""
Модуль схем аутентификации.
Содержит Pydantic модели для работы с токенами.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """
    Схема JWT токена.

    Attributes:
        access_token (str): JWT токен доступа
        token_type (str): Тип токена (обычно "bearer")
    """

    access_token: str
    token_type: str
