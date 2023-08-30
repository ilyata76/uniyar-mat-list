from loguru import logger
import sqlite3
from app.core.database.DBClient import DBClient
from app.core.schemas import UserData, UserDataResult
import app.config as config
from app.core.utils import userDataFromFetchedTuple

class UserDB :
    """
        Объект для управления базой данных пользователей.
        Решение ограничено задачей лишь получением юзера и их регистрацией.
    """

    def __init__(self, db_client : DBClient) :
        try : 
            logger.debug("Инициализация UserDB")
            self.db_client = db_client
            
            if self.db_client.testConnection() :
                with open(config.user_db_init_sql) as file:
                    logger.debug(f"Чтение и исполнение {config.user_db_init_sql}")
                    if not self.db_client.executescript(file.read()) :
                        logger.error("Ошибка при исполнении скрипта SQL userDB")
            else :
                logger.error("Не удалось подключиться к базам данных")
        except Exception as e :
            logger.error("Ошибка при инициализации UserDB : {exc}", exc={e})


    def exceptionUserDataResultHandler(function) :
        """
            Декоратор, оборачивающий методы класса для разрешения
                исключений и возвращаемых кодов
        """

        def wrap(self, *args, **kwargs) -> UserDataResult :
            """
                \n (0, UserData) - всё ок
                \n (1, None) - непредвиденная ошибка (в т.ч. с подключением)
                \n (2, None) - такой пользователь уже существует
                \n (3, None) - такого не существует
                \n (4, None) - нет прав
            """
            res = UserDataResult(code=1, result=None)

            try : 
                if self.db_client.testConnection() :
                    res = function(self, *args, **kwargs)
                else :
                    logger.error("UserDB : Не удалось подключиться к базам данных")

            except sqlite3.DatabaseError as exc:
                if exc.sqlite_errorcode == 1555 :
                    res.code = 2
                    logger.debug("UserDB : add метод. Попытка добавить существующего {exc}", exc=exc)
                    logger.info("UserDB : add метод. Попытка добавить существующего")
                else :
                    logger.error("UserDB : Ошибка с базами данных {code}: {exc}", 
                                        code=exc.sqlite_errorcode , exc=exc)
                    res.code = 2
            except Exception as exc :
                logger.error("UserDB : НЕПРЕДВИДЕННАЯ ОШИБКА : {exc}", exc=exc)
                res.code = 1

            finally :
                return res 

        return wrap


    @exceptionUserDataResultHandler
    def get(self, email : str) -> UserDataResult :
        """
            Получить пользователя, возвращает сформированный класс UserData.
            email - PRIMARY KEY => либо есть, либо нет. Нескольких быть не может.

            Возвращает:
                \n (0, UserData) - всё ок
                \n (1, None) - непредвиденная ошибка
                \n (3, None) - такого пользователя не существует
        """
        res = UserDataResult(code=1, result=None)

        sql = """ SELECT * FROM users WHERE email = ? """

        search = self.db_client.fetchone(sql, (email,))
        
        if search is not None :
            user = userDataFromFetchedTuple(search)
            res = UserDataResult(code=0, result=user)
        else : 
            res.code = 3
        
        logger.debug("UserDB : get метод. res={res}", res=res)
        logger.info("UserDB : get метод. res={res}", res=(res.result is not None))
        return res


    @exceptionUserDataResultHandler
    def add(self, user : UserData | None) -> UserDataResult :
        """
            Добавить пользователя UserData. 
            UserData как класс должны быть УЖЕ валидным.

            Возвращает:
                \n (0, UserData) - всё ок
                \n (1, None) - непредвиденная ошибка
                \n (2, None) - такой пользователь уже существует
        """
        res = UserDataResult(code=1, result=None)
        sql = """ INSERT INTO users VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ) """
        
        if self.db_client.execute( sql, 
                                   ( user.email, user.password,
                                     user.name, user.middle_name,
                                     user.surname, user.university,
                                     user.faculty, user.department,
                                     user.position, user.seniority  ) ) is not None :
            res = self.get(user.email)
                
        logger.debug("UserDB : add метод. res={res}", res=res)
        logger.info("UserDB : add метод. res={res}", res=(res.result is not None))
        return res