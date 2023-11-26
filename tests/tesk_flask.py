import io
import json
import os
import random

import pytest
from flask_app.src.models import Follower, Like, Media, Tweet


@pytest.mark.parametrize("route", ["/api/users/me", "/api/tweets", "/api/users/1"])
def test_route_status(client, route) -> None:
    response = client.get(route, headers={"api-key": "qwe"})
    assert response.status_code == 200


def test_post_media(client, db) -> None:
    len_before = len(db.session.query(Media).all())
    filename = (
        str([random.choice("qwertyuiopasdfghjklzxcvbnm") for _ in range(30)]) + ".jpg"
    )

    data = {"file": (io.BytesIO(b"asdasdasdasd"), filename)}
    response = client.post(
        "/api/medias",
        headers={"api-key": "qwe"},
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    assert len_before + 1 == len(db.session.query(Media).all())
    assert os.path.exists(filename) is True

    os.remove(filename)


@pytest.mark.tweet
def test_post_tweet(client, db) -> None:
    len_before = len(db.session.query(Tweet).all())
    tweet_data = {"tweet_data": "qwertyuip"}
    response = client.post(
        "/api/tweets",
        headers={"api-key": "qwe"},
        data=json.dumps(tweet_data),
        content_type="application/json",
    )

    assert response.status_code == 201
    assert len_before + 1 == len(db.session.query(Tweet).all())


@pytest.mark.tweet
def test_delete_tweet(client, db) -> None:
    len_before = len(db.session.query(Tweet).all())
    response = client.delete("/api/tweets/1", headers={"api-key": "tweet"})

    assert response.status_code == 200
    assert len_before - 1 == len(db.session.query(Tweet).all())


@pytest.mark.like
def test_like(client, db) -> None:
    len_before = len(db.session.query(Like).all())
    response = client.post("/api/tweets/1/likes", headers={"api-key": "qwe"})

    assert response.status_code == 200
    assert len_before + 1 == len(db.session.query(Like).all())


@pytest.mark.like
def test_dislike(client, db) -> None:
    len_before = len(db.session.query(Like).all())
    response = client.delete("/api/tweets/2/likes", headers={"api-key": "qwe"})

    assert response.status_code == 200
    assert len_before - 1 == len(db.session.query(Like).all())


@pytest.mark.follow
def test_follow(client, db) -> None:
    len_before = len(db.session.query(Follower).all())
    response = client.post("/api/users/3/follow", headers={"api-key": "qwe"})

    assert response.status_code == 200
    assert len_before + 1 == len(db.session.query(Follower).all())


@pytest.mark.follow
def test_unfollow(client, db) -> None:
    len_before = len(db.session.query(Follower).all())
    response = client.delete("/api/users/2/follow", headers={"api-key": "qwe"})

    assert response.status_code == 200
    assert len_before - 1 == len(db.session.query(Follower).all())
