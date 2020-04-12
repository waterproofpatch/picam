import json

import pytest

from flask_jwt_extended import create_access_token, create_refresh_token


def test_get_items(client):
    """
    Test the items endpoint
    """
    res = client.get('/api/items')
    assert 200 == res.status_code
    assert 'application/json' == res.content_type
    # not expecting any items
    assert not res.get_json()

    assert True


def test_post_items_fail_empty_payload(authenticated_client):
    """
    Test that items endpoint fails when content type is wrong
    """
    res = authenticated_client.post('/api/items', json={})
    assert 400 == res.status_code
    assert 'error' in res.json


def test_post_items_fail_content_type(authenticated_client):
    """
    Test that items endpoint fails when content type is wrong
    """
    res = authenticated_client.post('/api/items')
    assert 400 == res.status_code
    assert 'error' in res.json


def test_post_items_success(authenticated_client):
    """
    Test that we can add an item
    """
    pass
