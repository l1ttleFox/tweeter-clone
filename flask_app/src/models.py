from sqlalchemy import UniqueConstraint, desc, func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from app import db


class User(db.Model):
    """
    Модель пользователя приложения.
    """

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(100), nullable=False, unique=True)

    cm_association = db.relationship(
        "Follower", foreign_keys="Follower.follower_id", back_populates="follower"
    )
    f_association = db.relationship(
        "Follower",
        foreign_keys="Follower.content_maker_id",
        back_populates="content_maker",
    )
    likes_association = db.relationship("Like", back_populates="user")
    cm_followers = association_proxy("cm_association", "content_maker")
    f_followers = association_proxy("f_association", "follower")
    likes = association_proxy("likes_association", "tweet")

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "followers": [
                {"id": i_follower.id, "name": i_follower.name}
                for i_follower in self.f_followers
            ],
            "following": [
                {"id": i_content_maker.id, "name": i_content_maker.name}
                for i_content_maker in self.cm_followers
            ],
        }

    @hybrid_property
    def followers(self):
        """
        Метод получения фолловеров пользователя.
        """
        followers_ids = (
            db.session.query(Follower.follower_id)
            .filter(Follower.content_maker_id == self.id)
            .all()
        )
        result = db.session.query(User).filter(User.id.in_(followers_ids)).all()
        return [{"id": i_follower.id, "name": i_follower.name} for i_follower in result]

    def content_makers(self):
        """
        Метод получения всех, на кого подписан пользователь.
        """
        content_makers_ids = (
            db.session.query(Follower.content_maker_id)
            .filter(Follower.follower_id == self.id)
            .all()
        )
        result = (
            db.session.query(User, func.count(User.f_followers).label("f_amount"))
            .filter(User.id.in_(content_makers_ids))
            .order_by(desc("f_amount"))
            .all()
        )
        return result

    def ordered_tweets(self):
        """
        Метод получения твитов, которые написал пользователь,
        отсортированных по новизне.
        """
        result = (
            db.session.query(Tweet)
            .filter(Tweet.author_id == self.id)
            .order_by(desc(Tweet.added_at))
            .limit(5)
            .all()
        )
        return result


class Tweet(db.Model):
    """
    Модель твита.
    """

    __tablename__ = "tweet"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140))
    added_at = db.Column(db.DateTime, default=db.func.now())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    author = db.relationship("User", backref="tweets")
    likes_association = db.relationship("Like", back_populates="tweet")
    likes = association_proxy("likes_association", "user")

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "attachments": [i_media.filename for i_media in self.media],
            "author": {"id": self.author.id, "name": self.author.name},
            "likes": [
                {"user_id": i_like.id, "name": i_like.name} for i_like in self.likes
            ],
        }


class Follower(db.Model):
    """
    Модель для хранения информации о подписках.
    """

    __tablename__ = "followers"
    __table_args__ = (
        UniqueConstraint(
            "content_maker_id", "follower_id", name="content_maker_follower_uc"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    content_maker_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    content_maker = db.relationship(
        "User",
        foreign_keys=[
            content_maker_id,
        ],
        back_populates="f_association",
    )
    follower = db.relationship(
        "User",
        foreign_keys=[
            follower_id,
        ],
        back_populates="cm_association",
    )


class Like(db.Model):
    """
    Модель для хранения информации о лайках на твитах.
    """

    __tablename__ = "like"
    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="tweet_user_uc"),)

    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey("tweet.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    tweet = db.relationship("Tweet", back_populates="likes_association")
    user = db.relationship("User", back_populates="likes_association")


class Media(db.Model):
    """
    Модель для хранения медиа.
    """

    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey("tweet.id"), nullable=True)

    tweet = db.relationship("Tweet", backref="media")
