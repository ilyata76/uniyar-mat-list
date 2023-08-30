from pydantic import BaseModel
from typing import Any
from app.core.schemas.User import UserData
from app.core.schemas.Material import MaterialData


class Result(BaseModel) :
    """
        Модель, возвращаемая слоем базы данных, содержащая
            полезную нагрузку и код возврата
    """
    code    : int
    result  : Any | None = None


class UserDataResult(Result) :
    result  : UserData | None = None


class MaterialDataResult(Result) :
    result  : MaterialData | None = None


class MaterialDataListResult(Result) :
    result  : list[MaterialData] | None = None