from .main import db
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    __tablename__ = "users"
    
    id = db.Collumn(db.Integer, primary_key=True)
    name = db.Collumn(db.String(50), nullable=False)
    api_key = db.Collumn(db.String(100), nullable=False, unique=True)
    
    likes_association = db.relationship("Likes", back_populates="user")
    likes = association_proxy("likes_association", "tweet")
    
    def to_json(self):
        pass
    
    @hybrid_property
    def followers(self):
        followers_ids = db.session.query(Followers.follower_id).filter(
            Followers.content_maker_id == self.id
        ).all()
        result = db.session.query(User).filter(User.id.in_(followers_ids)).all()
        return result
    
    @hybrid_property
    def content_makers(self):
        content_makers_ids = db.session.query(
            Followers.content_maker_id).filter(
            Followers.follower_id == self.id).all()
        result = db.session.query(User).filter(
            User.id.in_(content_makers_ids)).all()
        return result
        

class Tweet(db.Model):
    __tablename__ = "tweets"
    
    id = db.Collumn(db.Integer, primary_key=True)
    content = db.Collumn(db.String(140))
    author_id = db.Collumn(db.Integer, db.ForeignKey("users.id"))
    
    author = db.relationship("User", backref="tweets")
    likes_association = db.relationship("Likes", back_populates="tweet")
    likes = association_proxy("likes_association", "user")
    
    def to_json(self):
        pass


class Likes(db.Model):
    __tablename__ = "likes"
    
    id = db.Collumn(db.Integer, primary_key=True)
    twit_id = db.Collumn(db.Integer, db.ForeignKey("tweets.id"))
    user_id = db.Collumn(db.Integer, db.ForeignKey("users.id"))
    
    twit = db.relationship("Tweet", back_populates="likes")
    user = db.relationship("User", back_populates="likes")


class Followers(db.Model):
    __tablename__ = "followers"
    
    id = db.Collumn(db.Integer, primary_key=True)
    content_maker_id = db.Collumn(db.Integer, db.ForeignKey("user.id"))
    follower_id = db.Collumn(db.Integer, db.ForeignKey("user.id"))
    
    content_maker = db.relationship("User", backref="followers")
    follower = db.relationship("User", backref="followers")

