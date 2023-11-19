from sqlalchemy import UniqueConstraint, func, desc
from .app import db
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    """
    Модель пользователя приложения.
    """
    __tablename__ = "users"
    
    id = db.Collumn(db.Integer, primary_key=True)
    name = db.Collumn(db.String(50), nullable=False)
    api_key = db.Collumn(db.String(100), nullable=False, unique=True)
    
    likes_association = db.relationship("Like", back_populates="user")
    likes = association_proxy("likes_association", "tweet")
    
    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "followers": [
                {
                    "id": i_follower.id,
                    "name": i_follower.name
                }
                for i_follower in self.followers
            ],
            "following": [
                {
                    "id": i_content_maker.id,
                    "name": i_content_maker.name
                }
                for i_content_maker in self.content_makers
            ]
        }
    
    @hybrid_property
    def followers(self):
        """
        Метод получения фолловеров пользователя.
        """
        followers_ids = db.session.query(Follower.follower_id).filter(
            Follower.content_maker_id == self.id
        ).all()
        result = db.session.query(User).filter(User.id.in_(followers_ids)).all()
        return result
    
    @hybrid_property
    def content_makers(self):
        """
        Метод получения всех, на кого подписан пользователь.
        """
        content_makers_ids = db.session.query(
            Follower.content_maker_id).filter(
            Follower.follower_id == self.id).all()
        result = db.session.query(User).filter(
            User.id.in_(content_makers_ids)).order_by(
            func.count(User.followers).desc()).all()
        return result
    
    @hybrid_property
    def ordered_tweets(self):
        """
        Метод получения твитов, которые написал пользователь,
        отсортированных по новизне.
        """
        result = db.session.query(
            User.tweets).filter(
            User.id == self.id).order_by(
            desc(Tweet.added_at)).limit(5).all()
        return result


class Tweet(db.Model):
    """
    Модель твита.
    """
    __tablename__ = "tweets"
    
    id = db.Collumn(db.Integer, primary_key=True)
    content = db.Collumn(db.String(140))
    added_at = db.Collumn(db.DateTime, default=db.func.now())
    author_id = db.Collumn(db.Integer, db.ForeignKey("users.id"))
    
    author = db.relationship("User", backref="tweets")
    likes_association = db.relationship("Like", back_populates="tweet")
    likes = association_proxy("likes_association", "user")
    
    def to_json(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "attachments": [
                i_media.filename
                for i_media in self.media
            ],
            "author": {
                "id": self.author.id,
                "name": self.author.name
            },
            "likes": [
                {
                    "user_id": i_like.id,
                    "name": i_like.name
                }
                for i_like in self.likes
            ]
        }


class Like(db.Model):
    """
    Модель для хранения информации о лайках на твитах.
    """
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("tweet_id", "user_id", name="tweet_user_uc"),
    )
    
    id = db.Collumn(db.Integer, primary_key=True)
    tweet_id = db.Collumn(db.Integer, db.ForeignKey("tweets.id"))
    user_id = db.Collumn(db.Integer, db.ForeignKey("users.id"))
    
    tweet = db.relationship("Tweet", back_populates="likes")
    user = db.relationship("User", back_populates="likes")


class Follower(db.Model):
    """
    Модель для хранения информации о подписках.
    """
    __tablename__ = "followers"
    __table_args__ = (
        UniqueConstraint(
            "content_maker_id",
            "follower_id",
            name="content_maker_follower_uc"),
    )
    
    id = db.Collumn(db.Integer, primary_key=True)
    content_maker_id = db.Collumn(db.Integer, db.ForeignKey("user.id"))
    follower_id = db.Collumn(db.Integer, db.ForeignKey("user.id"))
    
    content_maker = db.relationship("User", backref="followers")
    follower = db.relationship("User", backref="followers")


class Media(db.Model):
    """
    Модель для хранения медиа.
    """
    __tablename__ = "medias"
    
    id = db.Collumn(db.Integer, primary_key=True)
    filename = db.Collumn(db.String(100), nullable=False)
    tweet_id = db.Collumn(db.Integer, db.ForeignKey("tweets.id"), nullable=True)
    
    tweet = db.relationship("Tweet", backref="media")
