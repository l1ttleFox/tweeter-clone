from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin

db = SQLAlchemy()


def create_app():
    app = Flask(
        __name__,
        static_url_path="",
        static_folder="static",
        template_folder="static"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///debug.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    spec = APISpec(
        title="Twitter Clone",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
        ]
    )
    swagger = Swagger(app=app, template_file="../swagger.json")
    
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")
    
    @app.route("/api/tweets", methods=["GET", "POST"])
    def get_or_post_tweets():
        pass
    
    @app.route("/api/medias", methods=["POST"])
    def post_media():
        pass
    
    @app.route("/api/tweets/<int:id>", methods=["DELETE"])
    def delete_twit(id):
        pass
    
    @app.route("/api/tweets/<int:id>/likes", methods=["POST", "DELETE"])
    def like_or_dislike(id):
        pass
    
    @app.route("/api/users/<int:id>/follow", methods=["POST", "DELETE"])
    def follow_or_unfollow(id):
        pass
    
    @app.route("/api/users/me", methods=["GET"])
    def get_user_info():
        pass
    
    @app.route("/api/users/<int:id>", methods=["GET"])
    def get_any_user_info(id):
        pass
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=80)
