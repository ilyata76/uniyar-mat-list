from app.core.database.DBClient import DBClient
from app.core.database.UserDB import UserDB
from app.core.database.MaterialDB import MaterialDB

db_client  : DBClient   | None = None
userdb     : UserDB     | None = None
materialdb : MaterialDB | None = None