from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    return app


# if __name__ == '__main__':
#     app = Flask(
#         __name__,
#         static_url_path="",
#         static_folder="static",
#         template_folder="static"
#     )
#
#     @app.route("/")
#     def index():
#         return render_template("index.html")
#
#     app.run(debug=True, host="0.0.0.0", port=80)
