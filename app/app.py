import sys
from flask import Flask, request, session, render_template
from loguru import logger
import app.config as config


logger.remove(0)

logger.add(sys.stderr, level="WARNING")

if config.debug : 
    logger.add(sys.stdout, level="DEBUG")
    logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="4 MB", compression="zip")
else : 
    logger.add(sys.stdout, level="INFO")
    logger.add("log.log", format="{time} {level} {message}", level="INFO", rotation="4 MB", compression="zip")


logger.info("Создание приложения")

app = Flask(
    import_name = __name__,
    static_folder = "static",
    template_folder = "templates"
)

##########

logger.info("Конфигурация приложения")

app.config['SECRET_KEY'] = config.cookies_session_key

from app.routes import user, api_user, api_material, material

app.register_blueprint(api_user)
app.register_blueprint(api_material)
app.register_blueprint(user)
app.register_blueprint(material)

##########

logger.info("Конфигурация базы данных")

import app.core.database as database

database.db_client = database.DBClient()
database.userdb = database.UserDB(database.db_client)
database.materialdb = database.MaterialDB(database.db_client)

##########


@app.get("/")
@app.get("/index")
def root() :
    context = {"current_user" : None, 
               "show_logo" : False,
               "show_footer" : False}
    if "user" in session :
        context["current_user"] = session["user"]

    logger.info("/ : главная страница")

    return render_template("index.html", **context)