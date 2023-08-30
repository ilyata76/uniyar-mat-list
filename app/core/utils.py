from hashlib import sha256
from app.core.schemas import UserData, MaterialData

def userDataFromFetchedTuple(tuple) -> UserData :
    """
        результаты SQL-запросов обернуть в UserData модель
    """
    return UserData(
        email=tuple[0],
        password=tuple[1],
        name=tuple[2],
        middle_name=tuple[3],
        surname=tuple[4],
        university=tuple[5],
        faculty=tuple[6],
        department=tuple[7],
        position=tuple[8],
        seniority=tuple[9]
    )


def hash_password(password : str, salt : str) -> str :
    """
        Хранить пароли небезопасно
    """
    password_hash = sha256(password.encode("utf-8")).hexdigest()
    return sha256((password_hash + salt).encode("utf-8")).hexdigest()


def materialDataFromFetchedTuple(tuple, author = True) -> MaterialData :
    """
        результаты SQL-запросов обернуть в модель
    """
    author_name = None
    if author : 
        author_name = f"{tuple[10]}, {tuple[8][0]}."
        if tuple[9] :
            author_name += f" {tuple[9][0]}."

    return MaterialData(
        id=tuple[0],
        name=tuple[1],
        year=tuple[2],
        department=tuple[3],
        file=tuple[4],
        author_email=tuple[5],
        author_name=author_name
    )