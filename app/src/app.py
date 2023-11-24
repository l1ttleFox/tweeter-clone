from flask import Flask
from flasgger import Swagger
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = "/usr/share/nginx/html/media/"
db = SQLAlchemy()


def create_app(testing: bool = False):
    application = Flask(
        __name__,
        static_url_path="",
        static_folder="static",
        template_folder="static"
    )
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    if testing:
        application.config["TESTING"] = True,
        application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        application.config["UPLOAD_FOLDER"] = ""
    
    else:
        application.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
        application.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "postgresql+psycopg2://postgres:postgres@postgres:5432"
    
    from .models import User, Tweet, Like, Follower, Media
    db.init_app(application)
    with application.app_context():
        db.create_all()
    
    APISpec(
        title="Twitter Clone",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
        ]
    )
    Swagger(app=application, template_file="swagger.json")
    
    return application
