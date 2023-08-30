from flask import Blueprint, session, render_template
from loguru import logger


user = Blueprint("user", __name__)


@user.route("/registration", methods=["GET"])
def registrationPage() :
    """
        GET  - выдавать страницу регистрации с формой.
    """
    context = {"current_user" : None, 
               "show_logo" : True,
               "show_footer" : True}
    if "user" in session :
        return "409", 409
    
    logger.info("/registration : зарегистрироваться")
    
    return render_template("registration.html", **context), 200


@user.route("/login", methods=["GET"])
def loginPage() :
    """
        GET  - выдавать страницу логина с формой.
    """
    context = {"current_user" : None, 
               "show_logo" : True,
               "show_footer" : True}
    if "user" in session :
        return "409", 409
    
    logger.info("/login : авторизоваться")

    return render_template("login.html", **context), 200