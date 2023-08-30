from flask import session
from loguru import logger
from functools import wraps

def authorizedHandler(function) :
    @wraps(function) # помогает с коллизиями
    def auth_wrap(*args, **kwargs) :
        if "user" in session and session["user"] is not None:
            logger.info("Успешная аутентификация пользователя user={user}", user=session["user"])
            return function(*args, **kwargs)
        else :
            return "403", 403
    return auth_wrap