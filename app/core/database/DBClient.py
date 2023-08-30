import sqlite3
from loguru import logger
from typing import Any
import app.config as config


class DBClient :
    """
        Объект для управления базой данных SQLite
    """

    def __init__(self) :
        logger.debug("Инициализация DBClient")
        self._connection = sqlite3.connect(config.database_sqlite)
        self._connected = False


    def connection(self) -> sqlite3.Connection | None:
        """
            Открывает подключение к базе данных. Возвращает его, в противном
            случае None.
        """
        res = None
        try : 
            self._connection = sqlite3.connect(config.database_sqlite)
            res = self._connection
        except Exception as exc:
            logger.error("DBClient: ошибка при подключении к базе данных : {exc}", exc=exc)
            res = None

        logger.debug("DBClient : connection метод. res={res}", res=res)
        return res


    def testConnection(self) -> bool :
        """
            Сделать тестовое подключение к базе SQLite
        """
        res = False

        if not self._connected :
            # тут может быть логика проверки подключения
            self._connected = True

        res = self._connected

        logger.debug("DBClient : testConnection метод. res={res}", res=res)
        return res


    def connectionHandler(function) :
        """
            wrapped-функция возвращает результат обёрнутой функции,
                в противном случае - None
            В остальных случаях поднимается исключение.

            Декоратор обеспечивает логику, оборачивающуюся вокруг
                исполняемой операции над базой данных (execute в частности)
        """

        def wrap(self, *args, **kwargs) -> bool:

            logger.debug("DBClient : вошёл в connectionHandler декоратор")

            self.connection()

            if not self._connected :
                self._connection = sqlite3.connect(config.database_sqlite) # на всякий случай
                self.testConnection()

            res = None

            if self._connected : 
                try : 
                    with self._connection :
                        self._connection.execute("PRAGMA foreign_keys = ON;")
                        self._connection.execute("PRAGMA case_sensitive_like = true;")
                        res = function(self, *args, **kwargs)
                    self._connection.close()
                    self._connected = False
                except sqlite3.DatabaseError as exc : 
                    logger.debug("DBClient : исключение при операции с базой данных : {exc}", exc=exc)
                    raise exc
                except Exception as exc:
                    logger.error("DBClient : ошибка при операции с базой данных : {exc}", exc=exc)
                    raise exc

            return res
        
        return wrap
    

    @connectionHandler
    def executescript(self, sql_script : str) -> sqlite3.Cursor | None :
        """
            Выполнение скрипта SQL из строки sql_script.
            Возвращает sqlite3.Cursor в случае успеха. None - в остальных
        """
        res = self._connection.executescript(sql_script)
        logger.debug("DBClient : executescript метод")
        return res


    @connectionHandler
    def execute(self, sql : str, parameters = None) -> sqlite3.Cursor | None :
        """
            Выполнение sql-запроса с параметрами parameters.
            Возвращает sqlite3.Cursor в случае успеха. None - в остальных
        """
        res = self._connection.execute(sql, parameters) if parameters\
                else self._connection.execute(sql)
        logger.debug("DBClient : execute метод. sql={sql}", sql=sql)
        return res


    @connectionHandler
    def fetchone(self, sql : str, parameters = None) -> Any | None :
        """
            Выполнение sql-запроса с параметрами parameters.
            Возвращает результат sqlite.fetchone() в случае успеха. None - в остальных
        """
        res = self._connection.execute(sql, parameters).fetchone() if parameters\
                else self._connection.execute(sql).fetchone()
        logger.debug("DBClient : execute метод. sql={sql}", sql=sql)
        return res
    

    @connectionHandler
    def fetchall(self, sql : str, parameters = None) -> Any | None :
        """
            Выполнение sql-запроса с параметрами parameters.
            Возвращает езультат sqlite.fetchall() в случае успеха. None - в остальных
        """
        res = self._connection.execute(sql, parameters).fetchall() if parameters\
                else self._connection.execute(sql).fetchall()
        logger.debug("DBClient : execute метод. sql={sql}", sql=sql)
        return res