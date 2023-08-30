import sqlite3
from loguru import logger
from app.core.database.DBClient import DBClient
from app.core.schemas import MaterialDataResult, MaterialData, MaterialDataListResult, Author
import app.config as config
from app.core.utils import materialDataFromFetchedTuple


class MaterialDB :
    """
        Класс для управления базой данных загружаемых работ
    """

    def __init__(self, db_client : DBClient) :
        try : 
            logger.debug("Инициализация MaterialDB")
            self.db_client = db_client
            
            if self.db_client.testConnection() :
                with open(config.material_db_initi_sql) as file:
                    self.db_client.execute("PRAGMA foreign_keys = ON;")
                    logger.debug(f"Чтение и исполнение {config.material_db_initi_sql}")
                    if not self.db_client.executescript(file.read()) :
                        logger.error("Ошибка при исполнении скрипта SQL materialDB")
            else :
                logger.error("Не удалось подключиться к базам данных")
        except Exception as e :
            logger.error("Ошибка при инициализации MaterialDB : {exc}", exc={e})


    def exceptionMaterialDataResultHandler(function) :
        """
            Декоратор, оборачивающий методы класса для разрешения
                исключений и возвращаемых кодов
        """
 
        def wrap(self, *args, **kwargs) -> MaterialDataResult :
            """
                \n (0, MaterialData) - всё ок
                \n (1, None) - непредвиденная ошибка (в т.ч. с подключением)
                \n (3, None) - такого не существует
            """
            res = MaterialDataResult(code=1, result=None)
 
            try : 
                if self.db_client.testConnection() :
                    res = function(self, *args, **kwargs)
                else :
                    logger.error("MaterialDB : Не удалось подключиться к базам данных")
 
            except Exception as exc :
                logger.error("MaterialDB : НЕПРЕДВИДЕННАЯ ОШИБКА : {exc}", exc=exc)
                res.code = 1
 
            finally :
                return res 
 
        return wrap
    

    @exceptionMaterialDataResultHandler
    def getId(self, id : int) :
        """
            Поиск материала по его ID (для внутренних нужд)
        """
        
        res = MaterialDataResult(code=1, result=None)
        sql = """ SELECT * FROM materials WHERE id = ? """
        search = self.db_client.fetchone(sql, (id,))
        
        if search is not None :
            material = materialDataFromFetchedTuple(search, author=False)
            res = MaterialDataResult(code=0, result=material)
        else : 
            res.code = 3
        
        logger.debug("MaterialDB : getID метод. res={res}", res=(res is not None))
        logger.info("MaterialDB : getID метод. res={res}", res=(res.result is not None))
        return res


    @exceptionMaterialDataResultHandler
    def add(self, material : MaterialData) -> MaterialDataResult:
        """
            Добавить материал в базу данных. MaterialData хранит инф-ю о добавляющем.
            MaterialData должно быть валидным.
        """
        res = MaterialDataResult(code=1, result=None)
        sql = """ INSERT INTO materials(name, year, department, file, author_email) VALUES ( ?, ?, ?, ?, ? ) """
        blob_file = sqlite3.Binary(material.file)

        if self.db_client.execute( sql, 
                                   ( material.name, material.year,
                                     material.department, blob_file,
                                     material.author_email  ) ) is not None :
            res = MaterialDataResult(code=0, result=material)

        logger.debug("MaterialDB : add метод. res={res}", res=res.result.name)
        logger.info("MaterialDB : add метод. res={res}", res=(res.result is not None))
        return res
    


    def exceptionMaterialDataListResultHandler(function) :
        """
            Декоратор, оборачивающий методы класса для разрешения
                исключений и возвращаемых кодов в случае возвращаемых СПИСКОВ
        """
 
        def wrap(self, *args, **kwargs) -> MaterialDataListResult :
            """
                \n (0, [MaterialData]) - всё ок
                \n (0, []) - всё ок, но ни одного нет
                \n (1, None) - непредвиденная ошибка (в т.ч. с подключением)
            """
            res = MaterialDataListResult(code=1, result=None)
 
            try : 
                if self.db_client.testConnection() :
                    res = function(self, *args, **kwargs)
                else :
                    logger.error("MaterialDB : Не удалось подключиться к базам данных")
 
            except Exception as exc :
                logger.error("MaterialDB : НЕПРЕДВИДЕННАЯ ОШИБКА : {exc}", exc=exc)
                res.code = 1
 
            finally :
                return res 
 
        return wrap
    

    def getBySQL(self, sql : str = """ SELECT * FROM materials WHERE author_email = ? """,
                       parameters = ("example@ya.ru",)) -> MaterialDataListResult :
        """
            Для внутреннего пользования
        """
        
        res = MaterialDataListResult(code=1, result=None)
        search = self.db_client.fetchall(sql, parameters)
        
        if search is not None :
            materials : list[MaterialData] = [] 
            for row in search :
                material = materialDataFromFetchedTuple(row)
                materials.append(material)
            res = MaterialDataListResult(code=0, result=materials)
        else : 
            res.code = 3
        
        logger.debug("MaterialDB : getBySQL метод. sql={sql} res={res}", sql=sql, 
                     res=(res.result.__len__() if res.result else None))
        logger.info("MaterialDB : getBySQL метод. res={res}", res=(res.result is not None))
        return res
    

    @exceptionMaterialDataListResultHandler
    def getByAuthorEmail(self, email : str) -> MaterialDataListResult :
        logger.info("MaterialDB : getByEmail метод")
        return self.getBySQL(sql=""" SELECT * FROM materials LEFT JOIN users ON materials.author_email = users.email WHERE materials.author_email LIKE ? """,
                             parameters=(f"%{email}%",))


    @exceptionMaterialDataListResultHandler
    def getByMaterialYear(self, year : str) -> MaterialDataListResult :
        logger.info("MaterialDB : getByYear метод")
        return self.getBySQL(sql=""" SELECT * FROM materials LEFT JOIN users ON materials.author_email = users.email WHERE materials.year LIKE ? """,
                             parameters=(f"%{year}%",))
    

    @exceptionMaterialDataListResultHandler
    def getByMaterialDepartment(self, department : str) -> MaterialDataListResult :
        logger.info("MaterialDB : getByDepartment метод")
        return self.getBySQL(sql=""" SELECT * FROM materials LEFT JOIN users ON materials.author_email = users.email WHERE materials.department LIKE ? """,
                             parameters=(f"%{department}%",))
    

    @exceptionMaterialDataListResultHandler
    def getByMaterialName(self, name : str) -> MaterialDataListResult :
        logger.info("MaterialDB : getByMaterialName метод")
        return self.getBySQL(sql=""" SELECT * FROM materials LEFT JOIN users ON materials.author_email = users.email WHERE materials.name LIKE ? """,
                             parameters=(f"%{name}%",))
    

    @exceptionMaterialDataListResultHandler
    def getByAuthorName(self, author : Author) -> MaterialDataListResult :
        logger.info("MaterialDB : getByAuthorName метод")
        
        conditions, parameters = [], []
        
        if author.name and author.name != '-':
            conditions.append("users.name LIKE ?")
            parameters.append(f"%{author.name}%")
        if author.middle_name and author.middle_name != '-':
            conditions.append("users.middle_name LIKE ?")
            parameters.append(f"%{author.middle_name}%")
        if author.surname and author.surname != '-':
            conditions.append("users.surname LIKE ?")
            parameters.append(f"%{author.surname}%")
        
        condition_sql = " AND ".join(conditions)
        sql = f"SELECT * FROM materials LEFT JOIN users ON materials.author_email = users.email"
        
        if conditions:
            sql += f" WHERE {condition_sql}"

        return self.getBySQL(sql=sql, parameters=(tuple(parameters) if parameters else None))