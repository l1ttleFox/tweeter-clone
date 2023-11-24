import pytest
from app.src.app import db as _db
from app.src.models import User, Tweet, Follower, Like
from app.src.routes import application


@pytest.fixture
def app():
    with application.app_context():
        _db.create_all()
        
        test_user = User(name="TestUser", api_key="qwe")
        u1 = User(name="TweetUser", api_key="tweet")
        u2 = User(name="FollowUser", api_key="follow")
        _db.session.add(test_user)
        _db.session.add(u1)
        _db.session.add(u2)

        t1 = Tweet(content="Strawberry", author_id=2)
        t2 = Tweet(content="Banana", author_id=2)
        f = Follower(content_maker_id=2, follower_id=1)
        _db.session.add(f)
        _db.session.add(t1)
        _db.session.add(t2)
        
        like = Like(tweet_id=2, user_id=1)
        _db.session.add(like)
        
        _db.session.commit()
        
        yield application
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client
    
    
@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
