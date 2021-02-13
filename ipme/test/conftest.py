# standard imports

# installed imports
import pytest

from src.utils import create_app, create_db, create_api


@pytest.fixture(scope="session")
def app():
    """
    Application fixture.
    """
    yield create_app()


@pytest.fixture(scope="session", autouse=True)
def api(app):
    yield create_api(app)


@pytest.fixture(scope="function", autouse=True)
def db(app):
    """
    Database fixture.
    """
    db = create_db(app)

    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db.session.commit()


@pytest.fixture(scope="function")
def client(app):
    """
    Test client fixture.
    """
    with app.test_client() as _client:
        yield _client