from pydantic import BaseModel


class Material(BaseModel) :
    """
        Интерфейсная модель материала
    """
    author_email  : str | None = None # FOREIGN PRIMARY KEY 
    author_name   : str | None = None
    name          : str
    year          : str
    department    : str


class MaterialData(Material) :
    """
        Дополняет Material самым бинарным PDF-материалом и id файла
    """
    id      : int | None = None # PRIMARY KEY
    file    : bytes

#######################

class Author(BaseModel) :
    """
        Модель автора для поиска по базе материалов
    """
    surname     : str | None = None
    middle_name : str | None = None
    name        : str | None = None