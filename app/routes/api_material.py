from flask import Blueprint, session, request, send_file, render_template
from loguru import logger
from pydantic import ValidationError
from app.core.schemas import Material, MaterialData,\
      MaterialDataResult, MaterialDataListResult, Author
from io import BytesIO
import app.core.database as database
from app.routes.authorized import authorizedHandler

api_material = Blueprint("api_material", __name__, url_prefix="/api/material")


@api_material.route("/", methods=["POST"])
@authorizedHandler
def materialPost() :
    try : 
        if not "year" in request.form or\
           not "department" in request.form or\
           not "name" in request.form or\
           not "file" in request.files or\
           not request.files["file"] :
            print(request.form, request.files)
            return "400", 400

        material = MaterialData( author_email=session["user"]["email"],
                                 name=request.form["name"],
                                 year=request.form["year"],
                                 department=request.form["department"],
                                 file=request.files["file"].stream.read() )
        
        result : MaterialDataResult = database.materialdb.add(material)

        logger.info("/api/material/ : добавление нового материала в базу res={res}",
                                res=(result.result is not None))

        if result.code == 0 :
            mat = Material(**result.result.model_dump())
            return mat.model_dump(), 200
        else :
            return "500", 500
    
    except ValidationError as exc:
        logger.error("/api/material/ : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "422", 422
    except Exception as exc :
        logger.error("/api/material/ : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500


@api_material.route("/", methods=["GET"])
def materialGet() :
    try :

        if "searchby" not in request.args or request.args["searchby"] is None :
            return "400", 400
        
        result : MaterialDataListResult = MaterialDataListResult(code=10, result=None)
        header = "Результат поиска"

        match request.args["searchby"] :
            case "authoremail" :
                result = database.materialdb.getByAuthorEmail(request.args["keyword"])
            case "authorname" : 
                author = request.args["keyword"].split(' ')
                author = Author(surname=author[0] if len(author) > 0 else None, 
                                name=author[1] if len(author) > 1 else None, 
                                middle_name=author[2] if len(author) > 2 else None)
                result = database.materialdb.getByAuthorName(author)
            case "year" :
                result = database.materialdb.getByMaterialYear(request.args["keyword"])
            case "department" :
                result = database.materialdb.getByMaterialDepartment(request.args["keyword"])
            case "name" :
                result = database.materialdb.getByMaterialName(request.args["keyword"])
            case "all" :
                result = database.materialdb.getBySQL(sql="""SELECT * FROM materials LEFT JOIN users ON materials.author_email = users.email """, parameters=None)
                header = "Работы, загруженные в систему"

        logger.info("/api/material/ : получение списка материалов (поиск) res={res}",
                                res=(result.result is not None))

        if result.code == 0 :
            # тут может быть какая-то логика ограничений, разделений и пр.
            resp = []
            for material in result.result :
                resp.append({"author_email" : material.author_email,
                             "author_name" : material.author_name,
                             "name" : material.name,
                             "year" : material.year,
                             "department" : material.department,
                             "id" : material.id})
            #return resp, 200
            context = {"current_user" : None, 
                       "show_logo" : True,
                       "show_footer" : True,
                       "header" : header}
            if "user" in session :
                context["current_user"] = session["user"]
            context["materials"] = resp
            return render_template("search.html", **context)
        elif result.code == 3 :
            #return [], 200
            context = {"current_user" : None, 
                       "show_logo" : True,
                       "show_footer" : True,
                       "header" : header}
            if "user" in session :
                context["current_user"] = session["user"]
            context["materials"] = resp
            return render_template("search.html", **context)
        elif result.code == 10 :
            return "400", 400
        else :
            return "500", 500
    
    except ValidationError as exc:
        logger.error("/api/material/ : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "422", 422
    except Exception as exc :
        logger.error("/api/material/ : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500
    

@api_material.route("/<int:file_id>", methods=["GET"])
def materialGetFile(file_id : int) :
    try : 
        result = database.materialdb.getId(file_id)

        if result.code == 0 :
            mem = BytesIO()
            name = result.result.name + ".pdf"
            mem.write(result.result.file)
            mem.seek(0)
            return send_file(mem, mimetype="application/pdf", download_name=name) # имя страницы плохое
        elif result.code == 3 :
            return "404", 404
        else :
            return "500", 500

    except ValidationError as exc:
        logger.error("/api/material/ : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "422", 422
    except Exception as exc :
        logger.error("/api/material/file_id : ошибка при исполнении хендлера: {exc}", exc=exc)
        return "500", 500