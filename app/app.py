from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin

db = SQLAlchemy()
UPLOAD_FOLDER = "./media/"


def create_app():
    application = Flask(
        __name__,
        static_url_path="",
        static_folder="static",
        template_folder="static"
    )
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///debug.db"
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    application.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    
    db.init_app(application)
    spec = APISpec(
        title="Twitter Clone",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
        ]
    )
    swagger = Swagger(app=application, template_file="../swagger.json")
    
    return application

