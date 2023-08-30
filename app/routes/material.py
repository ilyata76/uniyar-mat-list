from flask import Blueprint, session, render_template
from loguru import logger
import app.core.database as database

material = Blueprint("material", __name__)


@material.route("/post", methods=["GET"])
def materialPostPage() :
    """
        GET  - выдавать страницу для добавления материала
    """
    context = {"current_user" : None, 
               "show_logo" : True,
               "show_footer" : True}
    if "user" not in session :
        return "409", 409
    else :
        context["current_user"] = session["user"]
    
    logger.info("/post : загрузить материал")

    return render_template("upload_material.html", **context), 200


@material.route("/my", methods=["GET"])
def materialMy() :
    """
        GET  - выдавать страницу своих материалов
    """
    context = {"current_user" : None, 
               "show_logo" : True,
               "show_footer" : True}
    if "user" not in session :
        return "409", 409
    else :
        context["current_user"] = session["user"]
    result = database.materialdb.getByAuthorEmail(session["user"]["email"])
    resp = []
    for material in result.result :
        resp.append({"name" : material.name,
                     "year" : material.year,
                     "department" : material.department,
                     "id" : material.id})
    context["materials"] = resp
    return render_template("my_materials.html", **context), 200


# @material.route("/additional_search", methods=["GET"])
# def materialSearch() :
#     """
#     """
#     context = {"current_user" : None, 
#                "show_logo" : True,
#                "show_footer" : True}
#     if "user" in session : context["current_user"] = session["user"]
#     return render_template("additional_search.html", **context), 200