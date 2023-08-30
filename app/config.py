import os

debug = bool(os.environ.get("DEBUG", False))
user_db_init_sql = os.environ.get("USER_DB_INIT_SQL", "user_db_init.sql")
material_db_initi_sql = os.environ.get("MATERIAL_DB_INIT_SQL", "material_db_init.sql")
database_sqlite = os.environ.get("DB_FILE", "test.db")
cookies_session_key = os.environ.get("SESSION_KEY", "you-will-never-guess")