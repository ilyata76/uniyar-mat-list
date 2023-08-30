from flask import Blueprint, session, request, redirect, url_for, render_template
from loguru import logger
from pydantic import ValidationError
from app.core.schemas import User,\
        UserRegistration, UserData, UserDataResult, UserLogin
import app.core.database as database
from app.core.utils import hash_password
from app.routes.authorized import authorizedHandler

api_user = Blueprint("api_user", __name__, url_prefix="/api/user")


@api_user.route("/me", methods=["GET"])
@authorizedHandler
def me() :
    """
        Вернуть информацию по себе из сессии
    """
    try : 
        user = database.userdb.get(session["user"]["email"]).result
        if user :
            logger.info("/api/user/me")
            user = (user).model_dump()
            return User(**user).model_dump(), 200
        else :
            return "403", 403
    except Exception as exc :
        logger.error("/api/user/me : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500
    

@api_user.route("/<string:email>", methods=["GET"])
def getUser(email : str) :
    """
        Вернуть информацию, что пользователь существует
    """
    try : 
        user = database.userdb.get(email).result
        if user :
            return "200", 200
        else :
            return "404", 404
    except Exception as exc :
        logger.error("/api/user/<email> : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500



@api_user.route("/registration", methods=["POST"])
def registration() :
    """
        POST - принимать запрос с формой для регистрации юзера.
    """
    try :
        user_to_registration = UserRegistration(**request.form)

        # т.к. это одна сеть и нет как таковых "запросов" - безопасно хешировать здесь
        user_to_registration.password = hash_password(user_to_registration.password,
                                                      user_to_registration.email)
        # может быть логика здесь дополнительная
        user_to_database = UserData(**user_to_registration.model_dump())
        
        # все ошибки обрабатываются уже внутри, датабаза возвращает лишь коды
        result : UserDataResult = database.userdb.add(user=user_to_database)

        logger.info("/api/user/registration : регистрация пользователя res={res}",
                                res=(result.result is not None))

        if result.code == 0 :
            user = User(**result.result.model_dump()).model_dump()
            session["user"] = user
            #return user, 200
            return redirect(url_for("root", _method="GET")), 302
        elif result.code == 2 :
            return "409", 409
        else : 
            return "500", 500
        
    except ValidationError :
        return "422", 422
    except Exception as exc :
        logger.error("/api/user/registration : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500
    

@api_user.route("/login", methods=["POST"])
def login() :
    """
        POST - принимать запрос с формой для логина юзера.
    """
    try :
        user_to_login = UserLogin(**request.form)

        # т.к. это одна сеть и нет как таковых "запросов" - безопасно хешировать здесь
        user_to_login.password = hash_password( user_to_login.password,
                                                user_to_login.email )
                
        # все ошибки обрабатываются уже внутри, датабаза возвращает лишь коды
        result : UserDataResult = database.userdb.get(user_to_login.email)

        if result.result is not None and result.result.password != user_to_login.password :
            result = UserDataResult(code=4, result=None) # нет прав

        logger.info("/api/user/login : авторизация пользователя res={res}",
                                res=(result.result is not None))

        if result.code == 0 :
            user = User(**result.result.model_dump()).model_dump()
            session["user"] = user
            #return user, 200
            return redirect(url_for('root', _method="GET")), 302
        elif result.code == 3 :
            #return "404", 404
            context = {"current_user" : None, 
               "show_logo" : True,
               "show_footer" : True,
               "message" : f"Такого пользователя ({user_to_login.email}) не существует"}
            return render_template("login.html", **context), 200
        elif result.code == 4 :
            #return "403", 403
            context = {"current_user" : None, 
               "show_logo" : True,
               "show_footer" : True,
               "message" : "Неправильный логин или пароль"}
            return render_template("login.html", **context), 200
        else : 
            return "500", 500
        
    except ValidationError :
        return "422", 422
    except Exception as exc :
        logger.error("/api/user/login : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500
    

@api_user.route("/logout", methods=["POST"])
@authorizedHandler
def logout() :
    """
        POST - принимать запрос с формой для логина юзера.
    """
    try :
       logger.info("/api/user/logout")
       del session["user"]
       return redirect(url_for('root', _method="GET")), 302
    except Exception as exc :
        logger.error("/api/user/logout : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500