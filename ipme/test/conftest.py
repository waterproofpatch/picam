# standard imports
import os

# installed imports
import pytest

from src.application import Ip


@pytest.fixture(autouse=True, scope="session")
def init_database():
    os.environ["DATABASE_URL"] = "something"


@pytest.fixture
def ip_address():
    """
    A test database user
    """
    test_ip_address = Ip(ip="1.2.3.4")
    yield test_ip_address