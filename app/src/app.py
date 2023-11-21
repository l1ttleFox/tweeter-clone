from flask import Flask
from flasgger import Swagger
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = "./media/"
db = SQLAlchemy()


def create_app():
    application = Flask(
        __name__,
        static_url_path="",
        static_folder="static",
        template_folder="static"
    )
    application.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:postgres@postgres:5432"
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    application.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    db.init_app(application)
    with application.app_context():
        db.create_all()

        from models import User
        u = User(name="Alex", api_key="test")
        db.session.add(u)
        db.session.commit()

    spec = APISpec(
        title="Twitter Clone",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
        ]
    )
    swagger = Swagger(app=application, template_file="swagger.json")
    
    return application

