import os

from apispec import APISpec                             # type: ignore
from apispec_webframeworks.flask import FlaskPlugin     # type: ignore
from flasgger import Swagger                            # type: ignore
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = "/usr/share/nginx/html/media/"
db = SQLAlchemy()


def create_app(testing: bool = False, create_test_data: bool = False):
    application = Flask(
        __name__, static_url_path="", static_folder="static", template_folder="static"
    )
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if testing == 1:
        application.config["TESTING"] = True
        application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        application.config["UPLOAD_FOLDER"] = ""

    else:
        application.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
        application.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "postgresql+psycopg2://postgres:postgres@postgres:5432"

    from models import Follower, Like, Media, Tweet, User

    db.init_app(application)
    with application.app_context():
        db.create_all()

        if create_test_data:
            user = User(name="Alex", api_key="test")
            u = User(name="TestUser", api_key="qweqwe")
            db.session.add(user)
            db.session.add(u)

            tweet = Tweet(content="Image 1", author_id=2)
            t = Tweet(content="asdfuasfub", author_id=2)
            f = Follower(content_maker_id=2, follower_id=1)
            db.session.add(tweet)
            db.session.add(t)
            db.session.add(f)

            path = os.path.join(application.config["UPLOAD_FOLDER"], "1.jpeg")
            m = Media(filename=path, tweet_id=1)
            db.session.add(m)

            db.session.commit()

    APISpec(
        title="Twitter Clone",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
        ],
    )
    Swagger(app=application, template_file="swagger.json")

    return application
