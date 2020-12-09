import pytest
import tempfile
import os
import base64

from backend import flask_app, db, app
from backend.models import User, Image

from flask_jwt_extended import create_access_token, create_refresh_token

from backend.models import User, Image
from backend import db


@pytest.fixture
def test_users():
    """
    A test database user
    """
    hashed_pw = User.generate_hash(plaintext_password="passwordpassword1".encode())
    test_user_1 = User(
        email="test1@gmail.com", password=base64.b64encode(hashed_pw).decode()
    )
    hashed_pw = User.generate_hash(plaintext_password="passwordpassword2".encode())
    test_user_2 = User(
        email="test2@gmail.com", password=base64.b64encode(hashed_pw).decode()
    )
    yield [test_user_1, test_user_2]


@pytest.fixture
def unauthenticated_client(test_users):
    """
    A client with no access tokens.
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "test_app.db")
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    flask_app.config["TESTING"] = True

    app.init_db(db, drop_all=True)

    with flask_app.test_client() as client:
        for test_user in test_users:
            db.session.add(test_user)
        db.session.commit()
    yield client


@pytest.fixture()
def authenticated_client(unauthenticated_client):
    """
    A client with valid access and refresh tokens, capable of authenticating
    against endpoints guarded with @jwt_reqired
    """

    # we'll authenticate as test1
    with unauthenticated_client.application.app_context():
        access_token = create_access_token(identity="test1@gmail.com")
        refresh_token = create_refresh_token(identity="test1@gmail.com")
        unauthenticated_client.set_cookie("/", "access_token_cookie", access_token)
        unauthenticated_client.set_cookie("/", "refresh_token_cookie", refresh_token)
    yield unauthenticated_client


@pytest.fixture()
def test_images(authenticated_client, test_users):
    image_1 = Image(url="image1.jpg")
    image_2 = Image(url="image2.jpg")
    with authenticated_client.application.app_context():
        db.session.add(item_1)
        db.session.add(item_2)
        db.session.commit()
