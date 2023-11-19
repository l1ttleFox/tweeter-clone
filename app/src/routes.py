from .app import create_app, db
from .models import Media, User, Tweet, Like, Follower
from flask import render_template, request, jsonify
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
import os

app = create_app()


def error(status: int = 400):
    """
    Служебная функция для генерации типовых неудачных ответов API.
    :param status: (int) статус ответа.
    :return: ответ API.
    """
    return jsonify({"result": False}), status


def success(status: int = 200):
    """
    Служебная функция для генерации типовых успешных ответов API.
    :param status: (int) статус ответа.
    :return: ответ API.
    """
    return jsonify({"result": True}), status


@app.before_request
def check_api_key():
    """
    Функция проверки наличия в заголовках запроса api-key пользователя.
    Если заголовок отсутствует, возвращает клиенту ошибку.
    """
    api_key = request.headers.get("api-key", None)
    if api_key is None:
        return error()
    try:
        db.session.query(User).filter(User.api_key == api_key).one()
    except (NoResultFound, MultipleResultsFound):
        return error()


@app.route("/", methods=["GET"])
def index():
    """
    Эндпоинт для отдачи главной страницы сервиса.
    """
    return render_template("index.html")


@app.route("/api/tweets", methods=["GET", "POST"])
def get_or_post_tweets():
    """
    Эндпоинт API для работы с твитами.
    """
    user = db.session.query(User).filter(
        User.api_key == request.headers.get("api-key")
    ).one()
    
    if request.method == "GET":
        tweets = list()
        for i_content_maker in user.content_makers:
            tweets.extend(
                [
                    i_tweet.to_json() for i_tweet in
                    i_content_maker.ordered_tweets
                ]
            )
        
        return jsonify({
            "result": True,
            "tweets": tweets
        })
    
    elif request.method == "POST":
        data = request.json
        new_tweet = Tweet(
            content=data["tweet_data"],
            author_id=user.id
        )
        db.session.add(new_tweet)
        media_ids = data.get("tweet_media_ids", None)
        for i_media_id in media_ids:
            i_media = db.session.query(Media).filter(
                Media.id == i_media_id).one()
            i_media.tweet_id = new_tweet.id
        
        db.session.commit()
        
        return jsonify({
            "result": True,
            "tweet_id": new_tweet.id
        }), 201


@app.route("/api/medias", methods=["POST"])
def post_media():
    """
    Эндпоинт API для загрузки медиа к твитам.
    """
    file = request.files["file"]
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    
    new_media = Media(filename=file.filename)
    db.session.add(new_media)
    db.session.commit()
    
    return jsonify({
        "result": True,
        "media_id": new_media.id
    }), 201


@app.route("/api/tweets/<int:id>", methods=["DELETE"])
def delete_tweet(id):
    """
    Эндпоинт API для удаления твита.
    """
    user = db.session.query(User).filter(
        User.api_key == request.headers.get("api-key")
    ).one()
    try:
        tweet = db.session.query(Tweet).filter(Tweet.id == id).one()
    except NoResultFound:
        return error(404)
    
    if tweet.author_id != user.id:
        return error(403)
    
    db.session.delete(tweet)
    
    db.session.commit()
    return success()


@app.route("/api/tweets/<int:id>/likes", methods=["POST", "DELETE"])
def like_or_dislike(id):
    """
    Эндпоинт API для работы с лайками.
    """
    user = db.session.query(User).filter(
        User.api_key == request.headers.get("api-key")
    ).one()
    try:
        tweet = db.session.query(Tweet).filter(Tweet.id == id).one()
    except NoResultFound:
        return error(404)
    
    if request.method == "POST":
        new_like = Like(
            tweet_id=tweet.id,
            user_id=user.id
        )
        db.session.add(new_like)
    
    elif request.method == "DELETE":
        try:
            like = db.session.query(Like).filter(
                Like.tweet_id == tweet.id).filter(
                Like.user_id == user.id).one()
            db.session.delete(like)
        
        except NoResultFound:
            return error(404)
    
    db.session.commit()
    return success()


@app.route("/api/users/<int:id>/follow", methods=["POST", "DELETE"])
def follow_or_unfollow(id):
    """
    Эндпоинт API для работы с подписками.
    """
    follower = db.session.query(User).filter(
        User.api_key == request.headers.get("api-key")
    ).one()
    try:
        content_maker = db.session.query(User).filter(User.id == id).one()
    except NoResultFound:
        return error(404)
    
    if request.method == "POST":
        new_follow = Follower(
            content_maker_id=content_maker.id,
            follower_id=follower.id
        )
        db.session.add(new_follow)
    
    elif request.method == "DELETE":
        try:
            follow = db.session.query(Follower).filter(
                Follower.content_maker_id == content_maker.id).filter(
                Follower.follower_id == follower.id).one()
            db.session.delete(follow)
        
        except NoResultFound:
            return error(404)
    
    db.session.commit()
    return success()


@app.route("/api/users/me", methods=["GET"])
def get_user_info():
    """
    Эндпоинт API для получения информации пользователя, который делает запрос.
    """
    user = db.session.query(User).filter(
        User.api_key == request.headers.get("api-key")
    ).one()
    return jsonify({
        "result": True,
        "user": jsonify(user.to_json())
    })


@app.route("/api/users/<int:id>", methods=["GET"])
def get_any_user_info(id):
    """
    Эндпоинт API для получения информации любого пользователя по id.
    """
    user = db.session.query(User).filter(User.id == id).one()
    return jsonify({
        "result": True,
        "user": jsonify(user.to_json())
    })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
