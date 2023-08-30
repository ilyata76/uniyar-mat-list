from pydantic import BaseModel
from typing import Optional



class User(BaseModel) :
    """
        Базовый юзер, взаимодействие с интерфейсами.

        Всё в строках, т.к. решение ограниченное и не
            предполагает логику
    """
    email       : str
    name        : str
    middle_name : str | None = None
    surname     : str
    university  : str
    faculty     : str
    department  : str
    position    : str
    seniority   : str


class UserRegistration(User) :
    """
        Модель для регистрации. Расширяет User
    """
    password    : str


class UserData(UserRegistration) :
    """
        Модель для базы данных, расширяет самую последнюю интерфейсную часть
    """
    # date

#################

class UserLogin(BaseModel) :
    """
        Модель для логина
    """
    email       : str
    password    : str